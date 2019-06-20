# easyfile: File Access for Humans

easyfile allows you to access an arbitrary line of a text file.

## Installation

To install easyfile, simply:

```bash
pip install easyfile
```

## Usage

```py
import easyfile

data = easyfile.TextFile('/path/to/your/text')

# It supports these methods below
data[0] # positive index access
data[-1] # negative index access
data[0:-1] # slicing
```
