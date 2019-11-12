# Easyfile: Random File Access for Humans
[![Build Status](https://travis-ci.org/yasufumy/easyfile.svg?branch=master)](https://github.com/yasufumy/easyfile/actions?query=workflow%3A%22Flake8+and+pytest%22)
[![Build Status](https://github.com/yasufumy/easyfile/workflows/Flake8%20and%20pytest/badge.svg)]()
[![codecov](https://codecov.io/gh/yasufumy/easyfile/branch/master/graph/badge.svg)](https://codecov.io/gh/yasufumy/easyfile)

Easyfile allows you to access an arbitrary line of a text file.

If your interest is in using Easyfile for Deep Learning, please check [Lineflow](https://github.com/yasufumy/lineflow).

## Installation

To install Easyfile:

```bash
pip install easyfile
```

## Usage

```py
import easyfile

data = easyfile.TextFile('/path/to/text')

data[0] # Access the first line of your text
data[-1] # Access the last line of your text
data[10:100] # Access the 10th line to the 100 the line of your text
```
