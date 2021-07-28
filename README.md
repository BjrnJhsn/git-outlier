# git-outlier
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/BjrnJhsn/git-outlier/branch/main/graph/badge.svg?token=UJXXUA0Q9D)](https://codecov.io/gh/BjrnJhsn/git-outlier)
![example workflow](https://github.com/BjrnJhsn/git-outlier/actions/workflows/python-app.yml/badge.svg)


Data-driven screening to find source code that need refactoring.

Still under development and not yet ready to be used.

## Introduction
Run git-outlier to find source code files that are suitable candidates for refactoring.
git-outlier finds outliers in a source code directory under git version control in three categories: complexity, churn,
and  combined complexity and churn. The top files are worthy of further investigation. 

The combined complexity and churn outliers should be the top candidates for refactoring. The complexity and churn plot
is divided into four equal zones. All zones are ok to be in except the right-top-zone; these files are both complex and 
change often. The source code in these files will probably be easier to change and maintain if they are refactored.

The source code is analyzed per file, so this requires your project to contain multiple source code files 
with logic entities in separate files to make sense.

There are different metrics of complexity available. Choose the one that makes most sense for you or try both. Files
that are outliers
regardless of chosen complexity metrics are top candidates for refactoring.

## Installation

The latest release should be available via PyPI.
```
[sudo] pip install git-outlier
```

## Usage

If installed as a package, it should be directly available in git as
```
git outlier
```
and use the same options as the python script.

The python script can be run with the following options.
```
usage: git_outlier.py [-h] [--languages LANGUAGES] [--metric METRIC] [--span SPAN] [--top TOP] [-v] [path]

Analyze a source directory that uses git as version handling system. The source files are analyzed for different type of 
outliers and these outliers can be good candidates for refactoring to increase maintainability. The source files are 
ranked in falling order after churn, complexity, and combined churn and complexity.

positional arguments:
  path                  The path to the source directory to be analyzed. Will default to current directory if not present.

optional arguments:
  -h, --help            show this help message and exit
  --languages LANGUAGES, -l LANGUAGES
                        List the programming languages you want to analyze. If left empty, it'll search for all 
                        recognized languages. Example: 'outlier -l cpp -l python' searches for C++ and Python code. The
                        available languages are: c, cpp, csharp, fortran, go, java, javascript, lua, objective-c, php, 
                        python, ruby, rust, scala, swift, typescript
  --metric METRIC, -m METRIC
                        Choose the complexity metric you would like to base the results on. Either cyclomatic complexity
                         'CCN' or lines of code without comments 'NLOC'. If not specified, the default is 'CCN'.
  --span SPAN, -s SPAN  The number (integer) of months the analysis will look at. Default is 12 months.
  --top TOP, -t TOP     The number (integer) of outliers to show. Note that for the combined churn and complexity 
                        outliers, there is no maximum. Default is 10.
  -v, --verbose         Show analysis details and debug info.
```

## Supported languages
Supported languages
- C
- C++
- C#
- Fortran
- Go
- Java
- JavaScript
- Lua 
- Objective-c
- Php
- Python
- Ruby
- Rust
- Scala
- Swift
- TypeScript

The code complexity is computed using [lizard](http://www.lizard.ws/).
## References
The idea comes from Michael Feathers' article [Getting Empirical about Refactoring](https://www.agileconnection.com/article/getting-empirical-about-refactoring).

