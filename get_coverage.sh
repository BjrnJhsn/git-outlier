#!/bin/bash
# Run coverage on unit tests only (exclude integration tests)
coverage run --source git_outlier -m pytest test/test_outlier.py test/test_date_parameters.py test/test_error_handling.py test/test_output_functions.py test/test_main_integration.py test/test_plot_generation.py
coverage html
firefox htmlcov/index.html
