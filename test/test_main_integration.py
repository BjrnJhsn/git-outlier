"""
Test main function integration and end-to-end scenarios for git-outlier.
"""

import pytest
from unittest.mock import patch, Mock
from git_outlier.git_outlier import main, get_git_and_complexity_data


class TestMainFunction:
    """Test main function integration"""

    @patch('git_outlier.git_outlier.parse_arguments')
    @patch('git_outlier.git_outlier.change_directory')
    @patch('git_outlier.git_outlier.restore_directory')
    @patch('git_outlier.git_outlier.get_file_endings_for_languages')
    @patch('git_outlier.git_outlier.get_date_range')
    @patch('git_outlier.git_outlier.get_git_and_complexity_data')
    @patch('git_outlier.git_outlier.print_churn_outliers')
    @patch('git_outlier.git_outlier.print_complexity_outliers')
    @patch('git_outlier.git_outlier.print_churn_and_complexity_outliers')
    @patch('git_outlier.git_outlier.print_big_separator')
    @patch('logging.basicConfig')
    def test_main_function_flow(self, mock_logging, mock_print_sep, mock_print_churn_comp,
                               mock_print_comp, mock_print_churn, mock_get_data,
                               mock_get_range, mock_get_endings, mock_restore,
                               mock_change, mock_parse):
        """Test main function execution flow"""
        # Setup mocks
        mock_args = Mock()
        mock_args.level = "INFO"
        mock_args.path = "."
        mock_args.languages = ["python"]
        mock_args.since = None
        mock_args.until = None
        mock_args.metric = "CCN"
        mock_args.top = 10
        mock_parse.return_value = mock_args
        
        mock_change.return_value = "/original/path"
        mock_get_endings.return_value = [".py"]
        mock_get_range.return_value = ("2023-01-01", None)
        mock_get_data.return_value = ({"file.py": 10}, {"file.py": 5}, ["file.py"])
        
        # Execute main
        main()
        
        # Verify calls
        mock_parse.assert_called_once()
        mock_change.assert_called_once_with(".")
        mock_restore.assert_called_once_with("/original/path")
        mock_get_data.assert_called_once()
        mock_print_churn.assert_called_once()
        mock_print_comp.assert_called_once()
        mock_print_churn_comp.assert_called_once()
        mock_print_sep.assert_called_once()


class TestDataIntegration:
    """Test data processing integration functions"""

    @patch('git_outlier.git_outlier.get_git_log_in_current_directory')
    @patch('git_outlier.git_outlier.parse_churn_from_log')
    @patch('git_outlier.git_outlier.filter_files_by_extension')
    @patch('git_outlier.git_outlier.get_complexity_for_file_list')
    def test_get_git_and_complexity_data_with_until(self, mock_complexity, mock_filter,
                                                   mock_parse_churn, mock_get_log):
        """Test get_git_and_complexity_data with until parameter"""
        mock_get_log.return_value = "git log output"
        mock_parse_churn.return_value = ({"file.py": 5}, ["file.py"])
        mock_filter.return_value = ["file.py"]
        mock_complexity.return_value = {"file.py": 10}
        
        result = get_git_and_complexity_data(
            [".py"], "CCN", "2023-01-01", "2023-12-31"
        )
        
        complexity, churn, files = result
        assert "file.py" in complexity
        assert "file.py" in churn
        assert "file.py" in files
        mock_get_log.assert_called_once_with("2023-01-01", "2023-12-31")

    @patch('git_outlier.git_outlier.get_git_log_in_current_directory')
    @patch('git_outlier.git_outlier.parse_churn_from_log')
    @patch('git_outlier.git_outlier.filter_files_by_extension')
    @patch('git_outlier.git_outlier.get_complexity_for_file_list')
    def test_get_git_and_complexity_data_without_until(self, mock_complexity, mock_filter,
                                                      mock_parse_churn, mock_get_log):
        """Test get_git_and_complexity_data without until parameter"""
        mock_get_log.return_value = "git log output"
        mock_parse_churn.return_value = ({"file.py": 5}, ["file.py"])
        mock_filter.return_value = ["file.py"]
        mock_complexity.return_value = {"file.py": 10}
        
        result = get_git_and_complexity_data([".py"], "CCN", "2023-01-01")
        
        complexity, churn, files = result
        assert "file.py" in complexity
        assert "file.py" in churn
        assert "file.py" in files
        mock_get_log.assert_called_once_with("2023-01-01", None)