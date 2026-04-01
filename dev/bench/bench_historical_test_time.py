#!/usr/bin/env python3
"""
Benchmark ubelt test runtime across tagged versions and the current HEAD.

What this script does
---------------------
* Enumerates git tags (optionally filtered) plus HEAD.
* Creates a git worktree for each ref.
* Creates an isolated uv virtual environment for each ref using a requested
  Python interpreter/version.
* Installs runtime + test requirements if present.
* Installs the package from that ref.
* Runs the tests from a sandbox directory against the installed package.
* Repeats each run N times, records timing, and writes:
    - JSON summary
    - CSV rows
    - PNG plot

Example
-------
python ~/code/ubelt/dev/bench/bench_historical_test_time.py \
    --python 3.12 \
    --repetitions 3 \
    --ref HEAD \
    --ref v1.4.1 \
    --ref v1.4.0 \
    --ref v1.3.8 \
    --ref v1.3.7 \
    --outdir dev/bench-test-times

Notes
-----
* Older tags may fail to install or test under a modern Python version. Those
  failures are recorded instead of aborting the whole benchmark.
* By default this benchmarks all version-like tags plus HEAD. Use --limit if
  you want a quicker sample.
* This script avoids coverage during timing because coverage can dominate the
  runtime signal and distort comparisons.
"""
from __future__ import annotations

import argparse
import csv
import json
import pandas as pd
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass
class RunResult:
    ref: str
    kind: str  # "tag", "head", or generic "ref"
    version_label: str
    repetition: int
    ok: bool
    duration_sec: float | None
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
    """
    Thin wrapper around subprocess.run with readable failure messages.
    """
    kwargs = {
        "cwd": os.fspath(cwd) if cwd is not None else None,
        "env": env,
        "text": True,
    }
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE

    proc = subprocess.run(cmd, **kwargs)
    if check and proc.returncode != 0:
        cmd_text = " ".join(map(str, cmd))
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {cmd_text}\n"
            f"--- stdout ---\n{stdout}\n"
            f"--- stderr ---\n{stderr}"
        )
    return proc


def repo_root() -> pathlib.Path:
    proc = run(["git", "rev-parse", "--show-toplevel"], check=True, capture=True)
    return pathlib.Path(proc.stdout.strip())


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text)


def venv_python(venv_dir: pathlib.Path) -> pathlib.Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def create_worktree(repo_dpath: pathlib.Path, ref: str, wt_dpath: pathlib.Path) -> None:
    run(["git", "worktree", "add", "--detach", os.fspath(wt_dpath), ref], cwd=repo_dpath)


def remove_worktree(repo_dpath: pathlib.Path, wt_dpath: pathlib.Path) -> None:
    try:
        run(["git", "worktree", "remove", "--force", os.fspath(wt_dpath)], cwd=repo_dpath)
    except Exception:
        # Best-effort cleanup fallback
        shutil.rmtree(wt_dpath, ignore_errors=True)


def create_uv_venv(python_spec: str, venv_dir: pathlib.Path, cwd: pathlib.Path) -> pathlib.Path:
    run(["uv", "venv", "--python", python_spec, os.fspath(venv_dir)], cwd=cwd)
    pyexe = venv_python(venv_dir)
    if not pyexe.exists():
        raise RuntimeError(f"Expected venv python at {pyexe}")
    return pyexe


def install_for_ref(pyexe: pathlib.Path, wt_dpath: pathlib.Path, venv_dpath: pathlib.Path) -> None:
    """
    Install a ref's dependencies into the uv-created venv.
    """
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env["VIRTUAL_ENV"] = os.fspath(venv_dpath)
    env["PATH"] = f"{venv_python(venv_dpath).parent}{os.pathsep}{env.get('PATH', '')}"

    req_runtime = wt_dpath / "requirements" / "runtime.txt"
    req_tests = wt_dpath / "requirements" / "tests.txt"

    if req_runtime.exists():
        run(
            ["uv", "pip", "install", "--python", os.fspath(pyexe), "-r", os.fspath(req_runtime)],
            cwd=wt_dpath,
            env=env,
        )
    if req_tests.exists():
        run(
            ["uv", "pip", "install", "--python", os.fspath(pyexe), "-r", os.fspath(req_tests)],
            cwd=wt_dpath,
            env=env,
        )

    # Install package itself. Editable install is usually the most robust across tags.
    run(
        ["uv", "pip", "install", "--python", os.fspath(pyexe), "-e", "."],
        cwd=wt_dpath,
        env=env,
    )


def build_pytest_command(pyexe: pathlib.Path, wt_dpath: pathlib.Path, sandbox_dpath: pathlib.Path) -> list[str]:
    """
    Run from a sandbox directory against the installed module path and the
    worktree's tests directory. This mirrors the CI strategy more closely than
    running pytest inside the source tree.
    """
    tests_dpath = wt_dpath / "tests"

    # Resolve the installed module path from the venv.
    proc = run(
        [
            os.fspath(pyexe),
            "-c",
            (
                "import os, ubelt; "
                "print(os.path.dirname(ubelt.__file__))"
            ),
        ],
        cwd=sandbox_dpath,
        capture=True,
    )
    mod_dpath = proc.stdout.strip()

    cmd = [
        os.fspath(pyexe),
        "-m",
        "pytest",
        "-q",
        "-p",
        "pytester",
        "-p",
        "no:doctest",
        "--xdoctest",
        mod_dpath,
        os.fspath(tests_dpath),
    ]

    # Keep it robust for older tags: only add pyproject-based coverage config if present.
    pyproject = wt_dpath / "pyproject.toml"
    if pyproject.exists():
        # We intentionally omit coverage for timing fidelity.
        pass

    return cmd


def benchmark_ref(
    repo_dpath: pathlib.Path,
    ref: str,
    kind: str,
    python_spec: str,
    repetitions: int,
    keep_worktrees: bool,
    root_tmp: pathlib.Path,
) -> list[RunResult]:
    results: list[RunResult] = []
    label = ref if kind != "head" else "HEAD"

    wt_name = safe_name(f"bench-{label}")
    wt_dpath = root_tmp / "worktrees" / wt_name
    venv_dpath = root_tmp / "venvs" / wt_name
    sandbox_dpath = root_tmp / "sandboxes" / wt_name

    wt_dpath.parent.mkdir(parents=True, exist_ok=True)
    venv_dpath.parent.mkdir(parents=True, exist_ok=True)
    sandbox_dpath.parent.mkdir(parents=True, exist_ok=True)

    try:
        create_worktree(repo_dpath, ref, wt_dpath)
    except Exception as ex:
        return [
            RunResult(
                ref=ref,
                kind=kind,
                version_label=label,
                repetition=0,
                ok=False,
                duration_sec=None,
                returncode=None,
                stage="worktree",
                error=str(ex),
            )
        ]

    try:
        pyexe = create_uv_venv(python_spec=python_spec, venv_dir=venv_dpath, cwd=wt_dpath)
    except Exception as ex:
        if not keep_worktrees:
            remove_worktree(repo_dpath, wt_dpath)
        return [
            RunResult(
                ref=ref,
                kind=kind,
                version_label=label,
                repetition=0,
                ok=False,
                duration_sec=None,
                returncode=None,
                stage="venv",
                error=str(ex),
            )
        ]

    try:
        install_for_ref(pyexe, wt_dpath, venv_dpath)
    except Exception as ex:
        if not keep_worktrees:
            remove_worktree(repo_dpath, wt_dpath)
        return [
            RunResult(
                ref=ref,
                kind=kind,
                version_label=label,
                repetition=0,
                ok=False,
                duration_sec=None,
                returncode=None,
                stage="install",
                error=str(ex),
            )
        ]

    for rep in range(1, repetitions + 1):
        sandbox_dpath.mkdir(parents=True, exist_ok=True)
        cmd = build_pytest_command(pyexe, wt_dpath, sandbox_dpath)
        start = time.perf_counter()
        proc = subprocess.run(
            cmd,
            cwd=os.fspath(sandbox_dpath),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        elapsed = time.perf_counter() - start
        ok = proc.returncode == 0
        results.append(
            RunResult(
                ref=ref,
                kind=kind,
                version_label=label,
                repetition=rep,
                ok=ok,
                duration_sec=elapsed if ok else None,
                returncode=proc.returncode,
                stage="test",
                error=None if ok else (
                    f"pytest failed with code={proc.returncode}\n"
                    f"--- stdout ---\n{proc.stdout}\n"
                    f"--- stderr ---\n{proc.stderr}"
                ),
            )
        )

    if not keep_worktrees:
        remove_worktree(repo_dpath, wt_dpath)

    return results


def summarize_results(rows: list[RunResult]) -> list[dict]:
    grouped: dict[str, list[RunResult]] = {}
    for row in rows:
        grouped.setdefault(row.version_label, []).append(row)

    summary = []
    for label, items in grouped.items():
        ok_times = [r.duration_sec for r in items if r.ok and r.duration_sec is not None]
        failed = [r for r in items if not r.ok]
        first = items[0]
        summary.append({
            "ref": first.ref,
            "kind": first.kind,
            "version_label": label,
            "num_runs": len(items),
            "num_success": len(ok_times),
            "num_failed": len(failed),
            "mean_sec": statistics.mean(ok_times) if ok_times else None,
            "median_sec": statistics.median(ok_times) if ok_times else None,
            "min_sec": min(ok_times) if ok_times else None,
            "max_sec": max(ok_times) if ok_times else None,
            "stdev_sec": statistics.stdev(ok_times) if len(ok_times) >= 2 else 0.0 if ok_times else None,
            "errors": [r.error for r in failed if r.error],
        })
    return summary


def write_csv(rows: list[RunResult], fpath: pathlib.Path) -> None:
    fpath.parent.mkdir(parents=True, exist_ok=True)
    with fpath.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(rows[0]).keys()) if rows else [
            "ref", "kind", "version_label", "repetition", "ok",
            "duration_sec", "returncode", "stage", "error",
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_json(data: object, fpath: pathlib.Path) -> None:
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(json.dumps(data, indent=2))


def make_plot(rows: list[RunResult], fpath: pathlib.Path) -> None:
    """
    Plot raw timing rows with seaborn so error bars are computed from repeated
    runs instead of pre-aggregated summaries.
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except Exception as ex:
        print(f"[WARN] Could not import plotting dependencies: {ex}")
        return

    plot_rows = [
        {
            "version_label": row.version_label,
            "duration_sec": row.duration_sec,
        }
        for row in rows
        if row.ok and row.duration_sec is not None
    ]
    if not plot_rows:
        print("[WARN] No successful runs to plot")
        return

    df = pd.DataFrame(plot_rows)
    order = list(dict.fromkeys(df["version_label"].tolist()))

    fig, ax = plt.subplots(figsize=(max(10, len(order) * 0.55), 6))
    sns.pointplot(
        data=df,
        x="version_label",
        y="duration_sec",
        order=order,
        errorbar="sd",
        capsize=0.2,
        join=True,
        ax=ax,
    )
    ax.set_ylabel("test runtime (seconds)")
    ax.set_xlabel("version / ref")
    ax.set_title("ubelt test runtime by ref")
    ax.tick_params(axis="x", rotation=60)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fpath, dpi=200)
    plt.close(fig)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python",
        required=True,
        help="Python spec for uv, e.g. '3.12', 'python3.11', or '/path/to/python'",
    )
    parser.add_argument(
        "--ref",
        dest="refs",
        action="append",
        required=True,
        help=(
            "Git ref to benchmark. May be repeated. "
            "Examples: --ref v1.3.0 --ref v1.2.4 --ref HEAD"
        ),
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=3,
        help="Number of timing runs per ref.",
    )
    parser.add_argument(
        "--outdir",
        default="dev/bench-test-times",
        help="Directory to write CSV, JSON, and PNG outputs.",
    )
    parser.add_argument(
        "--keep-worktrees",
        action="store_true",
        help="Do not remove worktrees after running.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    repo_dpath = repo_root()
    outdir = (repo_dpath / args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    refs = []
    for ref in args.refs:
        kind = "head" if ref == "HEAD" else "ref"
        refs.append((ref, kind))

    print(f"[INFO] repo_dpath={repo_dpath}")
    print(f"[INFO] benchmarking refs={[r[0] for r in refs]}")
    print(f"[INFO] using python={args.python}")

    all_rows: list[RunResult] = []

    with tempfile.TemporaryDirectory(prefix="ubelt-bench-") as tmp:
        root_tmp = pathlib.Path(tmp)
        for ref, kind in refs:
            print(f"\n[INFO] === Benchmarking {ref} ({kind}) ===")
            rows = benchmark_ref(
                repo_dpath=repo_dpath,
                ref=ref,
                kind=kind,
                python_spec=args.python,
                repetitions=args.repetitions,
                keep_worktrees=args.keep_worktrees,
                root_tmp=root_tmp,
            )
            all_rows.extend(rows)

            fail_rows = [r for r in rows if not r.ok]
            if fail_rows:
                print(f"[WARN] {ref} failed at stage={fail_rows[0].stage}")
                if fail_rows[0].error:
                    print(fail_rows[0].error[:2000])

            ok_times = [r.duration_sec for r in rows if r.ok and r.duration_sec is not None]
            if ok_times:
                print(
                    f"[INFO] {ref}: n={len(ok_times)} "
                    f"mean={statistics.mean(ok_times):.3f}s "
                    f"median={statistics.median(ok_times):.3f}s"
                )
            else:
                print(f"[WARN] {ref}: no successful timed runs")

    summary = summarize_results(all_rows)

    csv_fpath = outdir / "benchmark_rows.csv"
    json_fpath = outdir / "benchmark_summary.json"
    plot_fpath = outdir / "benchmark_plot.png"

    write_csv(all_rows, csv_fpath)
    write_json(summary, json_fpath)
    make_plot(all_rows, plot_fpath)

    print(f"\n[INFO] Wrote: {csv_fpath}")
    print(f"[INFO] Wrote: {json_fpath}")
    print(f"[INFO] Wrote: {plot_fpath}")

    num_fail = sum(1 for r in all_rows if not r.ok)
    if num_fail:
        print(f"[WARN] Completed with {num_fail} failed stage(s) recorded in the outputs")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

