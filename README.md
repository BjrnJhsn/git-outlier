# git-outlier
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/BjrnJhsn/git-outlier/branch/main/graph/badge.svg?token=UJXXUA0Q9D)](https://codecov.io/gh/BjrnJhsn/git-outlier)
![example workflow](https://github.com/BjrnJhsn/git-outlier/actions/workflows/python-app.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/git-outlier.svg)](https://badge.fury.io/py/git-outlier)

**Find refactoring candidates by analyzing git history and code complexity.**

A git add-on that identifies source code files most likely to benefit from refactoring by combining git commit history (churn) with code complexity metrics.

## How It Works

Git-outlier analyzes your codebase to identify refactoring candidates by examining:

1. **Code Churn**: How frequently files change over time (from git history)
2. **Code Complexity**: Cyclomatic complexity or lines of code (using [lizard](http://www.lizard.ws/))
3. **Combined Analysis**: Files that are both complex AND frequently changed

### Analysis Categories

Git-outlier provides three types of analysis:

- **Complexity Outliers**: Files with the highest complexity scores
- **Churn Outliers**: Files that change most frequently  
- **Combined Outliers**: Files with both high complexity and high churn ⭐ **Prime refactoring candidates**

### The Four Zones

The complexity vs. churn plot divides files into four zones:

- **Low churn, low complexity** → ✅ Healthy code
- **Low churn, high complexity** → ⚠️ Complex but stable  
- **High churn, low complexity** → ⚠️ Simple but frequently changing
- **High churn, high complexity** → 🚨 **Refactoring candidates**

Files in the high churn, high complexity zone change frequently AND are complex, making them harder to maintain and more error-prone.

## Installation

### From PyPI (Recommended)
Install from PyPI to use as a git add-on:
```bash
[sudo] pip install git-outlier
```

### For Development
If you want to contribute or modify the code:
```bash
# Clone the repository
git clone https://github.com/BjrnJhsn/git-outlier.git
cd git-outlier

# Install with Poetry (recommended)
poetry install
poetry shell

# Or install with pip
pip install -e .
```

Once installed, the tool is available as `git outlier` (note the space) when run from within a git repository. You can also invoke it directly as `git-outlier` (with hyphen) from anywhere.

## Usage

Once installed, git-outlier can be used as a git add-on:
```bash
git outlier                                # analyze last 12 months
git outlier --since="6 months ago"        # analyze last 6 months
git outlier --since="2023-01-01" --until="2023-12-31"  # specific date range
```

Or directly as a Python script:
```bash
git-outlier --since="1 month ago" -l python javascript
```

### Command Options

```
usage: git_outlier.py [-h] [--languages <lang>] [--metric <type>]
                      [--since <date>] [--until <date>] [--top <n>] [-v]
                      [path]

Find refactoring candidates by analyzing git history and code complexity.

positional arguments:
  path                  Path to git repository to analyze. Default: current
                        directory

optional arguments:
  -h, --help            Show this help message and exit
  --languages <lang>, -l <lang>
                        Only analyze specified languages (can be repeated).
                        Default: all supported languages. Available: c, cpp,
                        csharp, fortran, go, java, javascript, lua,
                        objective-c, php, python, ruby, rust, scala, swift,
                        typescript
  --metric <type>, -m <type>
                        Complexity metric to use: CCN (cyclomatic complexity)
                        or NLOC (lines of code). Default: CCN
  --since <date>        Show commits more recent than specific date. Accepts:
                        '2023-01-01', '6 months ago', 'last week'. Default: 12
                        months ago
  --until <date>        Show commits older than specific date. Accepts:
                        '2023-12-31', '1 month ago', 'yesterday'. Default:
                        today
  --top <n>, -t <n>     Limit output to top N outliers per category. Default:
                        10
  -v, --verbose         Be more verbose (can be repeated for more detail)

Examples:
  git outlier                            # analyze last 12 months (if installed as git add-on)
  git-outlier                            # same as above, direct invocation
  git outlier --since="6 months ago"     # analyze last 6 months  
  git outlier --since="2023-01-01" --until="2023-12-31"  # specific date range
  git outlier -l python -l javascript    # analyze only Python and JavaScript
  git outlier --metric=NLOC              # use lines of code instead of cyclomatic complexity

For more information, see: https://github.com/BjrnJhsn/git-outlier
```

### Examples

```bash
# Basic usage - analyze last 12 months
git outlier

# Analyze specific time period
git outlier --since="3 months ago" --until="1 week ago"

# Focus on specific languages
git outlier -l python -l javascript -l typescript

# Use lines of code instead of cyclomatic complexity
git outlier --metric=NLOC

# Show more results and be verbose
git outlier --top=20 -v

# Analyze specific directory
git outlier /path/to/project
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

