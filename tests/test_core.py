from unittest import TestCase
import tempfile

import easyfile


class TextTestCase(TestCase):

    def setUp(self):
        self.length = 100

        fp = tempfile.NamedTemporaryFile()
        for i in range(self.length):
            fp.write(f'line #{i}\n'.encode('utf-8'))
        fp.seek(0)
        self.fp = fp

    def tearDown(self):
        self.fp.close()

    def test_dunder_init(self):
        text = easyfile.TextFile(self.fp.name)
        self.assertEqual(text._path, self.fp.name)
        self.assertEqual(text._encoding, 'utf-8')
        self.assertFalse(text._ready)
        self.assertIsNone(text._length)
        self.assertIsNone(text._offsets)
        self.assertIsNone(text._mm)

    def test_supports_random_access(self):
        text = easyfile.TextFile(self.fp.name)
        for i in range(self.length):
            self.assertEqual(text[i], f'line #{i}')
            self.assertEqual(text[i - self.length], f'line #{i}')

    def test_iterates_each_line(self):
        text = easyfile.TextFile(self.fp.name)
        for i, x in enumerate(text):
            self.assertEqual(x, f'line #{i}')

    def test_slices_items(self):
        text = easyfile.TextFile(self.fp.name)
        self.assertSequenceEqual(text[:self.length], text)

    def test_raises_index_error_with_invalid_index(self):
        text = easyfile.TextFile(self.fp.name)
        with self.assertRaises(IndexError):
            text[self.length]
        with self.assertRaises(IndexError):
            text[-self.length-1]

    def test_dunder_len(self):
        text = easyfile.TextFile(self.fp.name)
        self.assertEqual(len(text), self.length)

    def test_dunder_getstate(self):
        text = easyfile.TextFile(self.fp.name)
        state = text.__getstate__()
        self.assertNotIn('_mm', state)

    def test_dunder_setstate(self):
        text = easyfile.TextFile(self.fp.name)
        state = text.__getstate__()
        self.assertNotIn('_mm', state)
        text.__setstate__(state)
        self.assertIn('_mm', text.__dict__)


class CsvTestCase(TestCase):

    def setUp(self):
        lines = ['en,ja',
                 'this is English .,this is Japanese .',
                 'this is also English .,this is also Japanese .']
        self.lines = lines
        fp = tempfile.NamedTemporaryFile()
        for x in lines:
            fp.write(f'{x}\n'.encode('utf-8'))
        fp.seek(0)
        self.fp = fp

    def tearDown(self):
        self.fp.close()

    def test_dunder_init(self):
        data = easyfile.CsvFile(self.fp.name)
        self.assertEqual(data._path, self.fp.name)
        self.assertEqual(data._encoding, 'utf-8')
        self.assertFalse(data._ready)
        self.assertIsNone(data._length)
        self.assertIsNone(data._offsets)
        self.assertIsNone(data._mm)
        self.assertEqual(data._delimiter, ',')
        self.assertFalse(data._header)
        self.assertIsNone(data._filednames)

    def test_slices_items(self):
        data = easyfile.CsvFile(self.fp.name)
        self.assertSequenceEqual(data[:len(self.lines)], data)

    def test_loads_csv_with_header(self):
        data = easyfile.CsvFile(self.fp.name, header=True)
        self.assertTrue(data._header)
        data._prepare_reading()
        self.assertListEqual(data._filednames, self.lines[0].split(','))

    def test_iterates_csv_with_header(self):
        from collections import OrderedDict

        data = easyfile.CsvFile(self.fp.name, header=True)
        data._prepare_reading()
        expected = [OrderedDict(zip(data._filednames, line.split(',')))
                    for line in self.lines[1:]]
        self.assertSequenceEqual(data, expected)
        for x, y in zip(data, expected):
            self.assertEqual(x, y)

    def test_iterates_csv_without_header(self):
        data = easyfile.CsvFile(self.fp.name, header=False)
        data._prepare_reading()
        expected = [line.split(',') for line in self.lines]
        self.assertSequenceEqual(data, expected)
        for x, y in zip(data, expected):
            self.assertEqual(x, y)
