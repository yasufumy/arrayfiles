import os
import contextlib


@contextlib.contextmanager
def open(filename: str, flags, **kwargs) -> int:
    try:
        fd = os.open(filename, flags, **kwargs)
        yield fd
    finally:
        os.close(fd)
