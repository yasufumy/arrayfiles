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
        text = easyfile.read_text(self.fp.name)
        self.assertEqual(text._path, self.fp.name)
        self.assertEqual(text._encoding, 'utf-8')

    def test_supports_random_access(self):
        text = easyfile.read_text(self.fp.name)
        for i in range(self.length):
            self.assertEqual(text[i], f'line #{i}')
            self.assertEqual(text[i - self.length], f'line #{i}')

    def test_iterates_each_line(self):
        text = easyfile.read_text(self.fp.name)
        for i, x in enumerate(text):
            self.assertEqual(x, f'line #{i}')

    def test_slices_items(self):
        text = easyfile.read_text(self.fp.name)
        self.assertSequenceEqual(text[:self.length], text)

    def test_iterates(self):
        text = easyfile.read_text(self.fp.name)
        with self.assertRaises(ValueError):
            next(text.iterate(self.length, 0))

    def test_raise_value_error_with_invalid_span(self):
        text = easyfile.read_text(self.fp.name)
        step = 10
        for start in range(0, self.length, step):
            end = start + step
            with self.subTest(start=start, end=end):
                for i, line in zip(range(start, end), text.iterate(start, end)):
                    self.assertEqual(line, f'line #{i}')

    def test_raises_index_error_with_invalid_index(self):
        text = easyfile.read_text(self.fp.name)

        def getitem(i):
            return text[i]

        with self.assertRaises(IndexError):
            getitem(self.length)
        with self.assertRaises(IndexError):
            getitem(-self.length-1)

    def test_dunder_len(self):
        text = easyfile.read_text(self.fp.name)
        self.assertEqual(len(text), self.length)
        self.assertEqual(len(text[:None]), self.length)
        self.assertEqual(len(list(text)), self.length)

    def test_dunder_getstate(self):
        text = easyfile.read_text(self.fp.name)
        state = text.__getstate__()
        self.assertNotIn('_mm', state)

    def test_dunder_setstate(self):
        text = easyfile.read_text(self.fp.name)
        state = text.__getstate__()
        self.assertNotIn('_mm', state)
        text.__setstate__(state)
        self.assertIn('_mm', text.__dict__)

    def test_eager_load(self):
        text1 = easyfile.read_text(self.fp.name, lazy=False)
        text2 = easyfile.read_text(self.fp.name, lazy=True)
        for a, b in zip(text1, text2):
            self.assertEqual(a, b)


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
        data = easyfile.read_csv(self.fp.name)
        self.assertEqual(data._path, self.fp.name)
        self.assertEqual(data._encoding, 'utf-8')
        self.assertEqual(data._delimiter, ',')
        self.assertFalse(data._header)

    def test_slices_items(self):
        data = easyfile.read_csv(self.fp.name)
        self.assertSequenceEqual(data[:len(self.lines)], data)

    def test_loads_csv_with_header(self):
        data = easyfile.read_csv(self.fp.name, header=True)
        self.assertTrue(data._header)

    def test_iterates_csv_with_header(self):
        from collections import OrderedDict

        data = easyfile.read_csv(self.fp.name, header=True)
        header = self.lines[0].split(',')
        expected = [OrderedDict(zip(header, line.split(',')))
                    for line in self.lines[1:]]
        for i, (x, y) in enumerate(zip(data, expected)):
            self.assertEqual(x, y)
            self.assertEqual(data[i], y)

    def test_iterates_csv_without_header(self):
        data = easyfile.read_csv(self.fp.name, header=False)
        expected = [line.split(',') for line in self.lines]
        self.assertSequenceEqual(data, expected)
        for x, y in zip(data, expected):
            self.assertEqual(x, y)

    def test_eager_load(self):
        text1 = easyfile.read_csv(self.fp.name, lazy=False)
        text2 = easyfile.read_csv(self.fp.name, lazy=True)
        for a, b in zip(text1, text2):
            self.assertEqual(a, b)


class CustomNewlineTextTestCase(TestCase):

    def setUp(self):
        self.length = 100

        fp = tempfile.NamedTemporaryFile()
        for i in range(self.length):
            fp.write(f'line #{i}\n\n'.encode('utf-8'))
        fp.seek(0)
        self.fp = fp
        self.newline = '\n\n'

    def tearDown(self):
        self.fp.close()

    def test_dunder_len(self):
        text = easyfile.read_text(self.fp.name, newline=self.newline)
        self.assertEqual(len(text), self.length)
        self.assertEqual(len(text[:None]), self.length)
        self.assertEqual(len(list(text)), self.length)

    def test_iterates_each_line(self):
        text = easyfile.read_text(self.fp.name, newline=self.newline)
        for i, (x, y) in enumerate(zip(text, text[:None])):
            self.assertEqual(x, y, f'line #{i}')

    def test_eager_load(self):
        text1 = easyfile.read_text(self.fp.name, newline=self.newline, lazy=False)
        text2 = easyfile.read_text(self.fp.name, newline=self.newline, lazy=True)
        for a, b in zip(text1, text2):
            self.assertEqual(a, b)
