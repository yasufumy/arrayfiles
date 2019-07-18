from typing import Union, Iterator, List, Dict, Any
import os
import io
import mmap
import csv

from easyfile import utils


class TextFile:
    """Load a line-oriented text file.

    Args:
        path (str): The path to the text file.
        encoding (str, optional): The name of the encoding used to decode.
    """

    def __init__(self, path: str, encoding: str = 'utf-8') -> None:
        assert os.path.exists(path)

        self._path = os.path.expanduser(path)
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
                 header: bool = False) -> None:
        super().__init__(path, encoding)

        self._delimiter = delimiter
        self._reader = csv.DictReader if header else csv.reader
        self._header = header
        self._filednames = None

    def _prepare_reading(self) -> None:
        if self._ready:
            return
        super()._prepare_reading()
        if self._header:
            self._filednames = next(csv.reader([self.getline(0)], delimiter=self._delimiter))
            self._offsets.pop(0)
            self._length -= 1

    def __iter__(self) -> Iterator[Union[List[Any], Dict[str, Any]]]:
        with io.open(self._path, encoding=self._encoding) as fp:
            if self._header:
                fp.readline()
                yield from self._reader(fp, delimiter=self._delimiter, fieldnames=self._filednames)
            else:
                yield from self._reader(fp, delimiter=self._delimiter)

    def __getitem__(self, index: Union[int, slice]) -> Union[List[Any], Dict[str, Any]]:
        x = super().__getitem__(index)
        if not isinstance(x, list):
            x = [x]
        if self._header:
            row = self._reader(x, delimiter=self._delimiter, fieldnames=self._filednames)
        else:
            row = self._reader(x, delimiter=self._delimiter)
        row = list(row)
        if len(row) == 1:
            return row[0]
        return row
