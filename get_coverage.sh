#!/bin/bash
coverage run --source git_outlier -m pytest
coverage html
firefox htmlcov/index.html
