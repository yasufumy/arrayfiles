# ArrayFiles: Array-like File Access in Python
[![Build Status](https://travis-ci.com/yasufumy/arrayfiles.svg?branch=master)](https://travis-ci.com/yasufumy/arrayfiles)
[![Build Status](https://github.com/yasufumy/arrayfiles/workflows/Run%20CI%20build/badge.svg)](https://github.com/yasufumy/arrayfiles/actions?query=workflow%3A%22Run+CI+build%22)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/yasufumy/arrayfiles.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/yasufumy/arrayfiles/context:python)
 [![Codacy Badge](https://api.codacy.com/project/badge/Grade/b2c2289a10fd4f2284f436c961e81258)](https://www.codacy.com/manual/yasufumy/arrayfiles?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=yasufumy/arrayfiles&amp;utm_campaign=Badge_Grade)
 [![Codacy Badge](https://api.codacy.com/project/badge/Coverage/b2c2289a10fd4f2284f436c961e81258)](https://www.codacy.com/manual/yasufumy/arrayfiles?utm_source=github.com&utm_medium=referral&utm_content=yasufumy/arrayfiles&utm_campaign=Badge_Coverage)
[![codecov](https://codecov.io/gh/yasufumy/arrayfiles/branch/master/graph/badge.svg)](https://codecov.io/gh/yasufumy/arrayfiles)

ArrayFiles allows you to access an arbitrary line of a text file.

If your interest is in using arrayfiles for Deep Learning, please check [LineFlow](https://github.com/yasufumy/lineflow).

## Installation

To install arrayfiles:

```bash
pip install arrayfiles
```

## Usage

```py
import arrayfiles

data = arrayfiles.read_text('/path/to/text')

data[0] # Access the first line of your text
data[-1] # Access the last line of your text
data[10:100] # Access the 10th line to the 100 the line of your text
```
