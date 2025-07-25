"""
Simple git integration tests that run with real git commands.
These tests create temporary git repositories and test actual git functionality.
"""

import os
import tempfile
import subprocess
import pytest
from pathlib import Path

from git_outlier.git_outlier import get_git_log_in_current_directory, parse_churn_from_log


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)
        original_cwd = os.getcwd()
        
        try:
            # Change to temp directory
            os.chdir(repo_path)
            
            # Initialize git repo
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
            
            yield repo_path
            
        finally:
            # Always restore original directory
            os.chdir(original_cwd)


def test_git_is_available():
    """Test that git command is available in the environment"""
    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'git version' in result.stdout


def test_empty_git_repository(temp_git_repo):
    """Test behavior with empty git repository"""
    # Should not crash with empty repository
    result = get_git_log_in_current_directory('2020-01-01')
    assert result == ''  # Empty repository should return empty string


def test_git_repository_with_commits(temp_git_repo):
    """Test with a git repository that has actual commits"""
    # Create a test file and commit it
    test_file = temp_git_repo / 'test.py'
    test_file.write_text('print("hello world")')
    
    subprocess.run(['git', 'add', 'test.py'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Add test file'], check=True)
    
    # Test git log retrieval
    result = get_git_log_in_current_directory('2020-01-01')
    assert result != ''  # Should have some output
    
    # Test parsing the log
    churn, file_names = parse_churn_from_log(result)
    assert 'test.py' in file_names
    assert churn['test.py'] == 1


def test_git_repository_with_multiple_commits(temp_git_repo):
    """Test with multiple commits to the same file"""
    # Create initial file
    test_file = temp_git_repo / 'example.py'
    test_file.write_text('# Initial version')
    
    subprocess.run(['git', 'add', 'example.py'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
    
    # Modify and commit again
    test_file.write_text('# Updated version\nprint("hello")')
    subprocess.run(['git', 'add', 'example.py'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Update file'], check=True)
    
    # Test churn counting
    result = get_git_log_in_current_directory('2020-01-01')
    churn, file_names = parse_churn_from_log(result)
    
    assert 'example.py' in file_names
    assert churn['example.py'] == 2  # File was changed twice


def test_non_git_directory():
    """Test error handling when not in a git repository"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # Should exit with code 128 when not in a git repository
            with pytest.raises(SystemExit) as exc_info:
                get_git_log_in_current_directory('2020-01-01')
            assert exc_info.value.code == 128  # Git's standard exit code
        finally:
            os.chdir(original_cwd)