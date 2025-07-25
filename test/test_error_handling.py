"""
Test error handling and edge cases for git-outlier.
"""

import pytest
from unittest.mock import patch, Mock
from git_outlier.git_outlier import (
    get_git_log_in_current_directory,
    change_directory,
    restore_directory,
    parse_arguments,
)


class TestGitCommandErrors:
    """Test git command error handling"""

    @patch('subprocess.Popen')
    def test_git_command_failure(self, mock_popen):
        """Test git command failure handling"""
        process = Mock()
        process.communicate.return_value = ("", "git command failed")
        process.returncode = 1  # Non-zero return code
        mock_popen.return_value = process
        
        with pytest.raises(SystemExit) as exc_info:
            get_git_log_in_current_directory("2023-01-01")
        assert exc_info.value.code == 1

    @patch('subprocess.Popen')
    def test_git_os_error(self, mock_popen):
        """Test OS error when executing git command"""
        mock_popen.side_effect = OSError("Command not found")
        
        with pytest.raises(SystemExit) as exc_info:
            get_git_log_in_current_directory("2023-01-01")
        assert exc_info.value.code == 1

    @patch('subprocess.Popen')
    def test_git_unexpected_error(self, mock_popen):
        """Test unexpected error handling"""
        mock_popen.side_effect = Exception("Unexpected error")
        
        with pytest.raises(SystemExit) as exc_info:
            get_git_log_in_current_directory("2023-01-01")
        assert exc_info.value.code == 1

    def test_empty_repository_scenario(self):
        """Test scenario with empty git repository"""
        with patch('subprocess.Popen') as mock_popen:
            process = Mock()
            process.communicate.return_value = ("", "does not have any commits yet")
            process.returncode = 1
            mock_popen.return_value = process
            
            result = get_git_log_in_current_directory("2023-01-01")
            assert result == ""


class TestDirectoryErrors:
    """Test directory change error handling"""

    def test_change_directory_os_error(self):
        """Test change_directory with invalid path"""
        with pytest.raises(SystemExit) as exc_info:
            change_directory("/nonexistent/path/that/does/not/exist")
        assert exc_info.value.code == 1

    def test_change_directory_unexpected_error(self):
        """Test change_directory with unexpected error"""
        with patch('os.chdir', side_effect=Exception("Unexpected error")):
            with pytest.raises(SystemExit) as exc_info:
                change_directory(".")
            assert exc_info.value.code == 1

    def test_restore_directory_os_error(self):
        """Test restore_directory with invalid path"""
        with pytest.raises(SystemExit) as exc_info:
            restore_directory("/nonexistent/path/that/does/not/exist")
        assert exc_info.value.code == 1

    def test_restore_directory_unexpected_error(self):
        """Test restore_directory with unexpected error"""
        with patch('os.chdir', side_effect=Exception("Unexpected error")):
            with pytest.raises(SystemExit) as exc_info:
                restore_directory(".")
            assert exc_info.value.code == 1


class TestArgumentValidationErrors:
    """Test argument parsing validation errors"""

    def test_invalid_metric(self):
        """Test invalid complexity metric"""
        with pytest.raises(SystemExit):
            parse_arguments(["--metric", "INVALID", "."])

    def test_invalid_since_date(self):
        """Test invalid since date"""
        with pytest.raises(SystemExit):
            parse_arguments(["--since", "invalid date", "."])

    def test_invalid_until_date(self):
        """Test invalid until date"""
        with pytest.raises(SystemExit):
            parse_arguments(["--until", "not a date", "."])

    def test_unsupported_language(self):
        """Test unsupported language"""
        with pytest.raises(SystemExit):
            parse_arguments(["-l", "unsupported_language", "."])

    def test_valid_date_parsing_edge_cases(self):
        """Test edge cases in date parsing that should succeed"""
        # Test with whitespace
        args = parse_arguments(["--since", "  6 months ago  ", "."])
        assert args.since == "  6 months ago  "
        
        # Test with valid absolute date
        args = parse_arguments(["--since", "2023-01-01", "."])
        assert args.since == "2023-01-01"