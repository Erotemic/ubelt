#!/usr/bin/env python3
"""
Benchmark ubelt import runtime across selected historical refs.

This script is intended to be more robust than an ad hoc historical import-time
benchmark by:
    * using explicit git refs via --ref
    * creating one git worktree per ref
    * creating one isolated uv venv per ref
    * emitting structured CSV / JSON outputs
    * recording both:
        - wall-clock import time
        - CPython -X importtime cumulative timing
    * doing warmup runs before measured repetitions

Example
-------
python dev/bench/bench_historical_import_time.py \
    --python 3.12 \
    --ref HEAD \
    --ref v1.4.1 \
    --ref v1.4.0 \
    --ref v1.3.8 \
    --ref v1.3.7 \
    --target "import ubelt" \
    --target "from ubelt import Path" \
    --target "import json" \
    --warmup 5 \
    --repetitions 300 \
    --outdir dev/bench-import-times

Notes
-----
* Older refs may fail to install or may not support the requested Python
  version. Failures are recorded instead of aborting the full run.
* The default target is "import ubelt".
* Measurements are done in subprocesses to better isolate import timing.
"""

from __future__ import annotations

import argparse
import csv
import json
import pandas as pd
import os
import pathlib
import platform
import re
import shutil
import statistics
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass
class MeasureRow:
    ref: str
    kind: str
    label: str
    target: str
    repetition: int
    mode: str  # "wall" or "importtime"
    ok: bool
    value_us: float | None
    returncode: int | None
    stage: str
    error: str | None


def run(
    cmd: list[str],
    cwd: pathlib.Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    kwargs = {
        'cwd': os.fspath(cwd) if cwd is not None else None,
        'env': env,
        'text': True,
    }
    if capture:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
    proc = subprocess.run(cmd, **kwargs)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f'Command failed ({proc.returncode}): {" ".join(map(str, cmd))}\n'
            f'--- stdout ---\n{proc.stdout or ""}\n'
            f'--- stderr ---\n{proc.stderr or ""}'
        )
    return proc


def repo_root() -> pathlib.Path:
    proc = run(['git', 'rev-parse', '--show-toplevel'])
    return pathlib.Path(proc.stdout.strip())


def safe_name(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', text)


def venv_python(venv_dir: pathlib.Path) -> pathlib.Path:
    if os.name == 'nt':
        return venv_dir / 'Scripts' / 'python.exe'
    return venv_dir / 'bin' / 'python'


def create_worktree(
    repo_dpath: pathlib.Path, ref: str, wt_dpath: pathlib.Path
) -> None:
    run(
        ['git', 'worktree', 'add', '--detach', os.fspath(wt_dpath), ref],
        cwd=repo_dpath,
    )


def remove_worktree(repo_dpath: pathlib.Path, wt_dpath: pathlib.Path) -> None:
    try:
        run(
            ['git', 'worktree', 'remove', '--force', os.fspath(wt_dpath)],
            cwd=repo_dpath,
        )
    except Exception:
        shutil.rmtree(wt_dpath, ignore_errors=True)


def create_uv_venv(
    python_spec: str, venv_dir: pathlib.Path, cwd: pathlib.Path
) -> pathlib.Path:
    run(['uv', 'venv', '--python', python_spec, os.fspath(venv_dir)], cwd=cwd)
    pyexe = venv_python(venv_dir)
    if not pyexe.exists():
        raise RuntimeError(f'Expected venv python at {pyexe}')
    return pyexe


def install_ref(
    pyexe: pathlib.Path, wt_dpath: pathlib.Path, venv_dpath: pathlib.Path
) -> None:
    """
    Install the ref into the uv-created environment.
    For import-time measurement, runtime requirements are sufficient.
    """
    env = os.environ.copy()
    env.setdefault('PYTHONUTF8', '1')
    env['VIRTUAL_ENV'] = os.fspath(venv_dpath)
    env['PATH'] = (
        f'{venv_python(venv_dpath).parent}{os.pathsep}{env.get("PATH", "")}'
    )

    req_runtime = wt_dpath / 'requirements' / 'runtime.txt'
    if req_runtime.exists():
        run(
            [
                'uv',
                'pip',
                'install',
                '--python',
                os.fspath(pyexe),
                '-r',
                os.fspath(req_runtime),
            ],
            cwd=wt_dpath,
            env=env,
        )

    run(
        ['uv', 'pip', 'install', '--python', os.fspath(pyexe), '-e', '.'],
        cwd=wt_dpath,
        env=env,
    )


def measure_wall_import_us(
    pyexe: pathlib.Path, stmt: str
) -> tuple[bool, float | None, int, str | None]:
    code = (
        'import json, time\n'
        't0 = time.perf_counter()\n'
        f'{stmt}\n'
        'dt_us = (time.perf_counter() - t0) * 1e6\n'
        "print(json.dumps({'wall_us': dt_us}))\n"
    )
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run(
        [os.fspath(pyexe), '-c', code],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if proc.returncode != 0:
        return False, None, proc.returncode, proc.stderr
    try:
        data = json.loads(proc.stdout.strip())
        return True, float(data['wall_us']), proc.returncode, None
    except Exception as ex:
        return (
            False,
            None,
            proc.returncode,
            (
                f'Failed to parse wall-time JSON: {ex}\n'
                f'--- stdout ---\n{proc.stdout}\n'
                f'--- stderr ---\n{proc.stderr}'
            ),
        )


def measure_importtime_us(
    pyexe: pathlib.Path, stmt: str
) -> tuple[bool, float | None, int, str | None]:
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run(
        [os.fspath(pyexe), '-X', 'importtime', '-c', stmt],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if proc.returncode != 0:
        return False, None, proc.returncode, proc.stderr

    lines = [line for line in proc.stderr.splitlines() if line.strip()]
    if not lines:
        return (
            False,
            None,
            proc.returncode,
            'No stderr output from -X importtime',
        )

    final_line = lines[-1]
    try:
        tail = final_line.split(': ', 1)[1]
        parts = [p.strip() for p in tail.split('|')]
        cumulative_us = float(parts[1])
        return True, cumulative_us, proc.returncode, None
    except Exception as ex:
        return (
            False,
            None,
            proc.returncode,
            (f'Could not parse importtime line: {final_line}\n{ex}'),
        )


def benchmark_ref(
    repo_dpath: pathlib.Path,
    ref: str,
    kind: str,
    python_spec: str,
    targets: list[str],
    warmup: int,
    repetitions: int,
    keep_worktrees: bool,
    root_tmp: pathlib.Path,
) -> list[MeasureRow]:
    rows: list[MeasureRow] = []
    label = ref if kind != 'head' else 'HEAD'

    wt_name = safe_name(f'bench-import-{label}')
    wt_dpath = root_tmp / 'worktrees' / wt_name
    venv_dpath = root_tmp / 'venvs' / wt_name

    wt_dpath.parent.mkdir(parents=True, exist_ok=True)
    venv_dpath.parent.mkdir(parents=True, exist_ok=True)

    try:
        create_worktree(repo_dpath, ref, wt_dpath)
    except Exception as ex:
        return [
            MeasureRow(
                ref=ref,
                kind=kind,
                label=label,
                target='',
                repetition=0,
                mode='setup',
                ok=False,
                value_us=None,
                returncode=None,
                stage='worktree',
                error=str(ex),
            )
        ]

    try:
        pyexe = create_uv_venv(python_spec, venv_dpath, wt_dpath)
    except Exception as ex:
        if not keep_worktrees:
            remove_worktree(repo_dpath, wt_dpath)
        return [
            MeasureRow(
                ref=ref,
                kind=kind,
                label=label,
                target='',
                repetition=0,
                mode='setup',
                ok=False,
                value_us=None,
                returncode=None,
                stage='venv',
                error=str(ex),
            )
        ]

    try:
        install_ref(pyexe, wt_dpath, venv_dpath)
    except Exception as ex:
        if not keep_worktrees:
            remove_worktree(repo_dpath, wt_dpath)
        return [
            MeasureRow(
                ref=ref,
                kind=kind,
                label=label,
                target='',
                repetition=0,
                mode='setup',
                ok=False,
                value_us=None,
                returncode=None,
                stage='install',
                error=str(ex),
            )
        ]

    for target in targets:
        for _ in range(warmup):
            measure_wall_import_us(pyexe, target)
            measure_importtime_us(pyexe, target)

        for rep in range(1, repetitions + 1):
            ok, value_us, rc, err = measure_wall_import_us(pyexe, target)
            rows.append(
                MeasureRow(
                    ref=ref,
                    kind=kind,
                    label=label,
                    target=target,
                    repetition=rep,
                    mode='wall',
                    ok=ok,
                    value_us=value_us,
                    returncode=rc,
                    stage='measure',
                    error=err,
                )
            )

            ok, value_us, rc, err = measure_importtime_us(pyexe, target)
            rows.append(
                MeasureRow(
                    ref=ref,
                    kind=kind,
                    label=label,
                    target=target,
                    repetition=rep,
                    mode='importtime',
                    ok=ok,
                    value_us=value_us,
                    returncode=rc,
                    stage='measure',
                    error=err,
                )
            )

    if not keep_worktrees:
        remove_worktree(repo_dpath, wt_dpath)

    return rows


def summarize(rows: list[MeasureRow]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[MeasureRow]] = {}
    for row in rows:
        key = (row.label, row.target, row.mode)
        grouped.setdefault(key, []).append(row)

    out = []
    for (label, target, mode), items in grouped.items():
        vals = [r.value_us for r in items if r.ok and r.value_us is not None]
        first = items[0]
        out.append(
            {
                'ref': first.ref,
                'kind': first.kind,
                'label': label,
                'target': target,
                'mode': mode,
                'num_runs': len(items),
                'num_success': len(vals),
                'num_failed': len(items) - len(vals),
                'mean_us': statistics.mean(vals) if vals else None,
                'median_us': statistics.median(vals) if vals else None,
                'min_us': min(vals) if vals else None,
                'max_us': max(vals) if vals else None,
                'stdev_us': statistics.stdev(vals)
                if len(vals) >= 2
                else 0.0
                if vals
                else None,
                'errors': [r.error for r in items if not r.ok and r.error],
            }
        )
    return out


def write_csv_rows(rows: list[dict], fpath: pathlib.Path) -> None:
    fpath.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = []
    with fpath.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


def write_json(data: object, fpath: pathlib.Path) -> None:
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(json.dumps(data, indent=2))


def make_plot(rows: list[MeasureRow], fpath: pathlib.Path) -> None:
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except Exception as ex:
        print(f'[WARN] Could not import plotting dependencies: {ex}')
        return

    plot_rows = [
        {
            'label': row.label,
            'target': row.target,
            'mode': row.mode,
            'value_us': row.value_us,
        }
        for row in rows
        if row.ok
        and row.value_us is not None
        and row.mode in {'wall', 'importtime'}
    ]
    if not plot_rows:
        print('[WARN] No successful runs to plot')
        return

    df = pd.DataFrame(plot_rows)
    group_keys = list(dict.fromkeys(zip(df['target'], df['mode'])))
    num_groups = len(group_keys)
    fig_height = max(4, 3.5 * num_groups)
    fig, axes = plt.subplots(
        num_groups,
        1,
        figsize=(max(10, 1.2 * df['label'].nunique()), fig_height),
    )
    if num_groups == 1:
        axes = [axes]

    for ax, (target, mode) in zip(axes, group_keys):
        subdf = df[(df['target'] == target) & (df['mode'] == mode)].copy()
        order = list(dict.fromkeys(subdf['label'].tolist()))
        sns.pointplot(
            data=subdf,
            x='label',
            y='value_us',
            order=order,
            errorbar='sd',
            capsize=0.2,
            join=True,
            ax=ax,
        )
        ax.set_ylabel('time (μs)')
        ax.set_xlabel('version / ref')
        ax.set_title(f'{mode}: {target}')
        ax.tick_params(axis='x', rotation=60)
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fpath, dpi=200)
    plt.close(fig)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--python',
        required=True,
        help="Python spec for uv, e.g. '3.12', 'python3.11', or '/path/to/python'",
    )
    parser.add_argument(
        '--ref',
        dest='refs',
        action='append',
        required=True,
        help='Git ref to benchmark. May be repeated.',
    )
    parser.add_argument(
        '--target',
        dest='targets',
        action='append',
        default=None,
        help='Import statement to benchmark. May be repeated. Example: --target "import ubelt"',
    )
    parser.add_argument(
        '--warmup',
        type=int,
        default=5,
        help='Number of warmup repetitions per target/ref before timing starts.',
    )
    parser.add_argument(
        '--repetitions',
        type=int,
        default=30,
        help='Number of measured repetitions per target/ref.',
    )
    parser.add_argument(
        '--outdir',
        default='dev/bench-import-times',
        help='Directory to write CSV, JSON, and PNG outputs.',
    )
    parser.add_argument(
        '--keep-worktrees',
        action='store_true',
        help='Do not remove worktrees after running.',
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    repo_dpath = repo_root()
    outdir = (repo_dpath / args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    refs: list[tuple[str, str]] = []
    for ref in args.refs:
        refs.append((ref, 'head' if ref == 'HEAD' else 'ref'))

    targets = args.targets or ['import ubelt']

    metadata = {
        'python_spec': args.python,
        'refs': [r[0] for r in refs],
        'targets': targets,
        'warmup': args.warmup,
        'repetitions': args.repetitions,
        'platform': platform.platform(),
        'system': platform.system(),
        'machine': platform.machine(),
        'repo_root': os.fspath(repo_dpath),
    }

    print(f'[INFO] repo_dpath={repo_dpath}')
    print(f'[INFO] benchmarking refs={[r[0] for r in refs]}')
    print(f'[INFO] using python={args.python}')
    print(f'[INFO] targets={targets}')

    all_rows: list[MeasureRow] = []

    with tempfile.TemporaryDirectory(prefix='ubelt-bench-import-') as tmp:
        root_tmp = pathlib.Path(tmp)
        for ref, kind in refs:
            print(f'\n[INFO] === Benchmarking {ref} ({kind}) ===')
            rows = benchmark_ref(
                repo_dpath=repo_dpath,
                ref=ref,
                kind=kind,
                python_spec=args.python,
                targets=targets,
                warmup=args.warmup,
                repetitions=args.repetitions,
                keep_worktrees=args.keep_worktrees,
                root_tmp=root_tmp,
            )
            all_rows.extend(rows)

            fail_rows = [r for r in rows if not r.ok]
            if fail_rows:
                print(f'[WARN] {ref} failed at stage={fail_rows[0].stage}')
                if fail_rows[0].error:
                    print(fail_rows[0].error[:2000])

            ok_rows = [r for r in rows if r.ok and r.value_us is not None]
            if ok_rows:
                print(f'[INFO] {ref}: successful measurements={len(ok_rows)}')
            else:
                print(f'[WARN] {ref}: no successful measurements')

    row_dicts = [asdict(r) for r in all_rows]
    summary = summarize(all_rows)

    rows_csv_fpath = outdir / 'import_benchmark_rows.csv'
    summary_csv_fpath = outdir / 'import_benchmark_summary.csv'
    summary_json_fpath = outdir / 'import_benchmark_summary.json'
    plot_fpath = outdir / 'import_benchmark_plot.png'
    metadata_json_fpath = outdir / 'import_benchmark_metadata.json'

    write_csv_rows(row_dicts, rows_csv_fpath)
    write_csv_rows(summary, summary_csv_fpath)
    write_json(summary, summary_json_fpath)
    write_json(metadata, metadata_json_fpath)
    make_plot(all_rows, plot_fpath)

    print(f'\n[INFO] Wrote: {rows_csv_fpath}')
    print(f'[INFO] Wrote: {summary_csv_fpath}')
    print(f'[INFO] Wrote: {summary_json_fpath}')
    print(f'[INFO] Wrote: {metadata_json_fpath}')
    print(f'[INFO] Wrote: {plot_fpath}')

    num_fail = sum(1 for r in all_rows if not r.ok)
    if num_fail:
        print(
            f'[WARN] Completed with {num_fail} failed measurement/setup rows recorded in the outputs'
        )
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
