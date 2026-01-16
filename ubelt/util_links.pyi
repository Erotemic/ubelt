from os import PathLike


def symlink(real_path: str | PathLike,
            link_path: str | PathLike,
            overwrite: bool = False,
            verbose: int = 0) -> str | PathLike:
    ...
