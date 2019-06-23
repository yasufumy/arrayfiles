# Easyfile: File Access for Humans
[![Build Status](https://travis-ci.org/yasufumy/easyfile.svg?branch=master)](https://travis-ci.org/yasufumy/easyfile)
[![codecov](https://codecov.io/gh/yasufumy/easyfile/branch/master/graph/badge.svg)](https://codecov.io/gh/yasufumy/easyfile)

Easyfile allows you to access an arbitrary line of a text file.

## Installation

To install Easyfile:

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
