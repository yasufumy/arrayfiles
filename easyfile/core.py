from typing import Union, Iterator, List, Dict, Any, Optional
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

    def __init__(self, path: str, encoding: Optional[str] = 'utf-8') -> None:
        path = os.path.expanduser(path)
        assert os.path.exists(path)

        self._path = path
        self._encoding = encoding
        with utils.fd_open(path, os.O_RDWR) as fd:
            self._mm = mmap.mmap(fd, 0, access=mmap.ACCESS_READ)

    def _get_offsets(self) -> List[int]:
        mm = self._mm
        mm.seek(0)
        return [0] + [mm.tell() for _ in iter(mm.readline, b'')]

    @property
    @functools.lru_cache()
    def _offsets(self) -> List[int]:
        return self._get_offsets()

    def _get_length(self) -> int:
        return len(self._offsets) - 1

    @property
    @functools.lru_cache()
    def _length(self) -> int:
        return self._get_length()

    def __iter__(self) -> Iterator[str]:
        with io.open(self._path, encoding=self._encoding) as fp:
            for line in fp:
                yield line.rstrip(os.linesep)

    def iterate(self, start: int, end: int) -> Iterator[str]:
        if start > end:
            raise ValueError('end should be larger than start.')
        self._mm.seek(self._offsets[start])
        readline = self._mm.readline
        tell = self._mm.tell
        end = self._offsets[end] if end < len(self._offsets) else self._offsets[-1]
        while tell() != end:
            yield readline().decode(self._encoding).rstrip(os.linesep)

    def __getitem__(self, index: Union[int, slice]) -> Union[str, List[str]]:
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
        start, end = self._offsets[i: i + 2]
        return self._mm[start: end].decode(self._encoding).rstrip(os.linesep)

    def __len__(self) -> int:
        return self._length

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        del state['_mm']
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        with utils.fd_open(self._path, os.O_RDWR) as fd:
            self._mm = mmap.mmap(fd, 0, access=mmap.ACCESS_READ)

    def __del__(self) -> None:
        if getattr(self, '_mm', None):
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
                 encoding: Optional[str] = 'utf-8',
                 delimiter: Optional[str] = ',',
                 header: Optional[bool] = False,
                 fieldnames: Optional[List[str]] = None) -> None:
        super().__init__(path, encoding)

        self._delimiter = delimiter
        self._header = header
        if header:
            if fieldnames is None:
                with io.open(path, encoding=encoding) as fp:
                    fieldnames = next(csv.reader(fp, delimiter=delimiter))
            # TODO: csv.DictReader skips blank lines.
            # So the item length doesn't match if the given file includes black lines.
            self._reader = functools.partial(csv.DictReader, delimiter=delimiter, fieldnames=fieldnames)
        else:
            self._reader = functools.partial(csv.reader, delimiter=delimiter)

    def _get_offsets(self) -> List[int]:
        offsets = super(CsvFile, self)._get_offsets()
        if self._header:
            offsets.pop(0)
        return offsets

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


class CustomNewlineTextFile(TextFile):
    """Load a line-oriented text file with custom newline letters.

    Args:
        path (str): The path to the text file.
        newline (str): The newline letters.
        encoding (str, optional): The name of the encoding used to decode.
    """

    def __init__(self, path: str, newline: str, encoding: Optional[str] = 'utf-8') -> None:
        super(CustomNewlineTextFile, self).__init__(path, encoding)

        self._newline = newline.encode(encoding)

    def _get_offsets(self) -> List[int]:
        mm = self._mm
        mm.seek(0)

        offsets = [0]
        start = 0
        newline = self._newline
        newline_offset = len(newline)
        while True:
            temp = mm.find(newline, start)
            if temp == -1:
                break
            start = temp + newline_offset
            offsets.append(start)
        return offsets

    def __iter__(self) -> Iterator[str]:
        mm = self._mm
        for start, end in zip(self._offsets, self._offsets[1:]):
            yield mm[start: end].decode(self._encoding).rstrip(os.linesep)


def read_text(
    path: str,
    encoding: Optional[str] = 'utf-8',
    newline: Optional[str] = '\n',
    lazy: Optional[bool] = True
) -> Union[TextFile, CustomNewlineTextFile, List[str]]:
    """Load a line-oriented text file.

    Args:
        path (str): The path to the text file.
        encoding (str, optional): The name of the encoding used to decode.
        newline (str, optional): The newline letters.
        lazy (bool, optional): If ``True``, the function returns ``TextFile`` or
        ``CustomNewlineTextFile`` object. Otherwise, returns a list of string.

    Returns (Union[TextFile, CustomNewlineTextFile, List[str]]):
        The loaded array-like accessible text file.

    Examples:
        >>> import easyfile
        >>> text = easyfile.read_text('/path/to/your/text')
        >>> print(text[0])
        The 1st line in your text will be displayed.
        >>> print(text[10:20])
        The 10th to 20th lines in your text will be displayed.
    """

    if newline == '\n':
        data = TextFile(path, encoding)
    else:
        data = CustomNewlineTextFile(path, newline, encoding)

    if lazy:
        return data
    else:
        return list(data)


def read_csv(
    path: str,
    encoding: Optional[str] = 'utf-8',
    delimiter: Optional[str] = ',',
    header: Optional[bool] = False,
    fieldnames: Optional[List[str]] = None,
    lazy: Optional[str] = True
) -> Union[CsvFile, List[str]]:
    """Load a CSV file.

    Args:
        path (str): The path to the text file.
        encoding (str, optional): The name of the encoding used to decode.
        delimiter (str, optional): A one-character string used to separate fields. It defaults to ','.
        header (bool, optional): If ``True``, this method will use the first line of the file as a header.
        fieldnames (list, optional): custom header.
        lazy (bool, optional): If ``True``, the function returns ``TextFile`` or
        ``CustomNewlineTextFile`` object. Otherwise, returns a list of string.

    Returns (Union[CsvFile, List[str]]):
        The loaded array-like accessible csv file.

    Examples:
        >>> import easyfile
        >>> text = easyfile.read_csv('/path/to/your/tsv', delimiter='\t')
        >>> print(text[0])
        ['the', 'first', 'row']
        >>> print(text[10:12])
        [['the', '10th', 'row'], ['the', '12th', 'row']]
    """

    data = CsvFile(path, encoding, delimiter, header, fieldnames)

    if lazy:
        return data
    else:
        return list(data)
