"""
Real lizard integration tests that verify actual lizard functionality.
These tests use lizard directly without mocking to ensure proper integration.
"""

import os
import tempfile
import pytest
from pathlib import Path

from git_outlier.git_outlier import (
    run_analyzer_on_file,
    get_complexity_for_file_list,
)


def test_lizard_integration_real_python_file():
    """Test actual lizard analysis on real Python file"""
    # Use our own test file as a known good Python file
    test_file = "test/test_outlier.py"
    assert os.path.isfile(test_file), f"Test file {test_file} must exist"
    
    result = run_analyzer_on_file(test_file)
    
    # Verify lizard result has expected attributes
    assert hasattr(result, 'CCN'), "Result should have CCN attribute"
    assert hasattr(result, 'nloc'), "Result should have nloc attribute"
    assert hasattr(result, 'filename'), "Result should have filename attribute"
    assert hasattr(result, 'function_list'), "Result should have function_list attribute"
    
    # Verify values are reasonable
    assert result.CCN > 0, "CCN should be positive for non-empty file"
    assert result.nloc > 0, "NLOC should be positive for non-empty file"
    assert result.filename == test_file
    assert isinstance(result.function_list, list)


def test_lizard_metrics_extraction_ccn_vs_nloc():
    """Test both CCN and NLOC extraction work correctly and return different values"""
    test_file = "test/test_outlier.py"
    
    ccn_complexity = get_complexity_for_file_list([test_file], "CCN")
    nloc_complexity = get_complexity_for_file_list([test_file], "NLOC")
    
    # Both should contain our test file
    assert test_file in ccn_complexity, "CCN analysis should include test file"
    assert test_file in nloc_complexity, "NLOC analysis should include test file"
    
    # Values should be positive and different
    ccn_value = ccn_complexity[test_file]
    nloc_value = nloc_complexity[test_file]
    
    assert ccn_value > 0, "CCN value should be positive"
    assert nloc_value > 0, "NLOC value should be positive"
    assert ccn_value != nloc_value, "CCN and NLOC should typically be different"


def test_lizard_main_module_analysis():
    """Test lizard analysis on the main git_outlier module"""
    main_file = "git_outlier/git_outlier.py"
    assert os.path.isfile(main_file), f"Main file {main_file} must exist"
    
    result = run_analyzer_on_file(main_file)
    
    # Main module should have substantial complexity
    assert result.CCN > 10, "Main module should have significant complexity"
    assert result.nloc > 100, "Main module should have substantial NLOC"
    assert len(result.function_list) > 10, "Main module should have many functions"
    
    # Test first function has expected attributes
    if result.function_list:
        func = result.function_list[0]
        assert hasattr(func, 'cyclomatic_complexity')
        assert hasattr(func, 'nloc')
        assert hasattr(func, 'name')
        assert hasattr(func, 'parameter_count')
        assert func.cyclomatic_complexity >= 1


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def simple_function():
    '''A simple function'''
    return 42

def complex_function(x):
    '''A more complex function'''
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x + 1
    else:
        return 0
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


def test_lizard_with_temp_file(temp_python_file):
    """Test lizard analysis with a controlled temporary file"""
    result = run_analyzer_on_file(temp_python_file)
    
    # Should detect both functions
    assert len(result.function_list) == 2
    
    # Find the complex function
    complex_func = None
    for func in result.function_list:
        if func.name == 'complex_function':
            complex_func = func
            break
    
    assert complex_func is not None, "Should find complex_function"
    assert complex_func.cyclomatic_complexity > 1, "Complex function should have CCN > 1"
    assert complex_func.parameter_count == 1, "Function should have 1 parameter"


def test_lizard_error_handling_invalid_metric():
    """Test error handling for invalid complexity metric"""
    test_file = "test/test_outlier.py"
    
    # This should call sys.exit(1) for invalid metric
    with pytest.raises(SystemExit) as exc_info:
        get_complexity_for_file_list([test_file], "INVALID_METRIC")
    
    assert exc_info.value.code == 1


def test_lizard_nonexistent_file():
    """Test lizard behavior with nonexistent file"""
    nonexistent_file = "this_file_does_not_exist.py"
    
    # Should not crash, should skip the file
    result = get_complexity_for_file_list([nonexistent_file], "CCN")
    
    # Result should be empty since file doesn't exist
    assert nonexistent_file not in result
    assert len(result) == 0


def test_lizard_empty_file_list():
    """Test lizard with empty file list"""
    result = get_complexity_for_file_list([], "CCN")
    assert result == {}


def test_lizard_mixed_existing_nonexisting_files():
    """Test lizard with mix of existing and non-existing files"""
    test_file = "test/test_outlier.py"
    nonexistent_file = "does_not_exist.py"
    
    result = get_complexity_for_file_list([test_file, nonexistent_file], "CCN")
    
    # Should only contain the existing file
    assert test_file in result
    assert nonexistent_file not in result
    assert len(result) == 1


@pytest.fixture
def temp_empty_python_file():
    """Create a temporary empty Python file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")  # Empty file
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


def test_lizard_empty_file(temp_empty_python_file):
    """Test lizard analysis with empty file"""
    result = run_analyzer_on_file(temp_empty_python_file)
    
    # Empty file should have minimal metrics
    assert result.CCN == 0, "Empty file should have CCN of 0"
    assert result.nloc == 0, "Empty file should have NLOC of 0"
    assert len(result.function_list) == 0, "Empty file should have no functions"


@pytest.fixture
def temp_syntax_error_file():
    """Create a temporary Python file with syntax errors"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def broken_function(
    # Missing closing parenthesis and colon
    return "this will not parse"
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


def test_lizard_syntax_error_handling(temp_syntax_error_file):
    """Test lizard behavior with syntax errors"""
    # Lizard should handle syntax errors gracefully
    # It may return partial results or empty results, but shouldn't crash
    result = run_analyzer_on_file(temp_syntax_error_file)
    
    # Should not crash and return a result object
    assert hasattr(result, 'CCN')
    assert hasattr(result, 'nloc')
    assert hasattr(result, 'function_list')
    
    # Lizard might still detect some lines even with syntax errors
    assert result.nloc >= 0
    assert result.CCN >= 0