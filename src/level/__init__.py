from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("level")
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed (e.g. during local development without install)
    __version__ = "0.0.0"
