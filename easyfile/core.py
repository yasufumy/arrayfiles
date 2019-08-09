from typing import Union, Iterator, List, Dict, Any
import os
import io
import mmap
import csv
import functools

from easyfile import utils


class TextFile:
    """Load a line-oriented text file.

    Args:
        path (str): The path to the text file.
        encoding (str, optional): The name of the encoding used to decode.
    """

    def __init__(self, path: str, encoding: str = 'utf-8') -> None:
        path = os.path.expanduser(path)
        assert os.path.exists(path)

        self._path = path
        self._encoding = encoding
        self._ready = False
        self._length = None
        self._offsets = None
        self._mm = None

    def _prepare_reading(self) -> None:
        if self._ready:
            return
        with utils.open(self._path, os.O_RDWR) as fd:
            mm = mmap.mmap(fd, 0, access=mmap.ACCESS_READ)
        self._offsets = [0] + [mm.tell() for _ in iter(mm.readline, b'')]
        self._mm = mm
        self._length = len(self._offsets) - 1
        self._ready = True

    def __iter__(self) -> Iterator[str]:
        with io.open(self._path, encoding=self._encoding) as fp:
            for line in fp:
                yield line.rstrip(os.linesep)

    def iterate(self, start: int, end: int) -> Iterator[str]:
        self._prepare_reading()
        if start > end:
            raise ValueError('end should be larger than start.')
        self._mm.seek(self._offsets[start])
        readline = self._mm.readline
        tell = self._mm.tell
        end = self._offsets[end] if end < len(self._offsets) else self._offsets[-1]
        while tell() != end:
            yield readline().decode(self._encoding).rstrip(os.linesep)

    def __getitem__(self, index: Union[int, slice]) -> Union[str, List[str]]:
        self._prepare_reading()
        if isinstance(index, slice):
            start, stop, step = index.indices(self._length)
            return [self.getline(i) for i in range(start, stop, step)]

        if index >= 0:
            if index >= self._length:
                raise IndexError('Text object index out of range')
        else:
            if index < - self._length:
                raise IndexError('Text object index out of range')
            index += self._length

        return self.getline(index)

    def getline(self, i: int) -> str:
        self._mm.seek(self._offsets[i])
        return self._mm.readline().decode(self._encoding).rstrip(os.linesep)

    def __len__(self) -> int:
        self._prepare_reading()
        return self._length

    def __getstate__(self) -> Dict[str, Any]:
        self._prepare_reading()
        state = self.__dict__.copy()
        del state['_mm']
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        with utils.open(self._path, os.O_RDWR) as fd:
            self._mm = mmap.mmap(fd, 0, access=mmap.ACCESS_READ)

    def __del__(self) -> None:
        if self._mm is not None:
            self._mm.close()


class CsvFile(TextFile):
    """Load a CSV file.

    Args:
        path (str): The path to the text file.
        encoding (str, optional): The name of the encoding used to decode.
        delimiter (str, optional): A one-character string used to separate fields. It defaults to ','.
        header (bool, optional): If ``True``, the csvfile will use the first line of the file as a header.
    """

    def __init__(self,
                 path: str,
                 encoding: str = 'utf-8',
                 delimiter: str = ',',
                 header: bool = False,
                 fieldnames: List[str] = None) -> None:
        super().__init__(path, encoding)

        self._delimiter = delimiter
        self._header = header
        if header:
            if fieldnames is None:
                with io.open(path, encoding=encoding) as fp:
                    fieldnames = next(csv.reader(fp, delimiter=delimiter))
            self._reader = functools.partial(csv.DictReader, delimiter=delimiter, fieldnames=fieldnames)
        else:
            self._reader = functools.partial(csv.reader, delimiter=delimiter)

    def _prepare_reading(self) -> None:
        if self._ready:
            return
        super()._prepare_reading()
        if self._header:
            self._offsets.pop(0)
            self._length -= 1

    def __iter__(self) -> Iterator[Union[List[Any], Dict[str, Any]]]:
        with io.open(self._path, encoding=self._encoding) as fp:
            if self._header:
                fp.readline()
            yield from self._reader(fp)

    def __getitem__(self, index: Union[int, slice]) -> Union[List[Any], Dict[str, Any]]:
        x = super().__getitem__(index)
        if not isinstance(x, list):
            x = [x]
        row = list(self._reader(x))
        if len(row) == 1:
            return row[0]
        return row
