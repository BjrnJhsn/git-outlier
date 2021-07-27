# git-outlier
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Data-driven screening to find source code that may need refactoring.

Still under development and not yet ready to be used.

## Introduction
Run git-outlier to find source code files that are suitable candidates for refactoring.
git-outlier finds outliers in a source code directory under git version control in three categories: complexity, churn, and
combined complexity and churn. The top files are worthy of further investigation.

The source code is analyzed per file, so this requires your project to contain multiple source code files 
with logic entities in separate files to make sense.

## Installation

The latest release will be available via PyPI in the near future.

## Usage

If installed as a package, it should be directly available as
```
git outlier
```
and use the same options as the python script.

The python script can be run with the following options.
```
usage: git_outlier.py [-h] [--languages LANGUAGES] [--metric METRIC] [--span SPAN] [path]

Analyze a source directory that uses git as version handling system. The source files are analyzed for different type of outliers and these outliers can
be good candidates for refactoring to increase maintainability. The source files are ranked in falling order after churn, complexity, and combined churn
and complexity.

positional arguments:
  path                  The path to the source directory to be analyzed. Will default to current directory if not present.

optional arguments:
  -h, --help            show this help message and exit
  --languages LANGUAGES, -l LANGUAGES
                        List the programming languages you want to analyze. if left empty, it'llsearch for python. 'outlier -l cpp -l python'searches
                        forC++ and Python code. The available languages are: cpp, python
  --metric METRIC, -m METRIC
                        Choose the complexity metric you would like to base the results on. Either cyclomaticcomplexity 'CCN' or lines of code without
                        comments 'NLOC'. If not specified, the default is 'CCN.
  --span SPAN, -s SPAN  The number (integer) of months the analysis will look at. Default is 12 months.
```



## Background
The idea comes from Michael Feathers' article [Getting Empirical about Refactoring](https://www.agileconnection.com/article/getting-empirical-about-refactoring).

The code complexity is computed using [lizard](http://www.lizard.ws/).
