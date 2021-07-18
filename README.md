# git-outlier
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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