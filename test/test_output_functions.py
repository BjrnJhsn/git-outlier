"""
Test output formatting functions for git-outlier.
"""

import pytest
from unittest.mock import patch
from git_outlier.git_outlier import (
    print_headline,
    print_subsection,
    print_big_separator,
    print_small_separator,
    big_separator,
    get_outliers_output,
    print_churn_outliers,
    print_complexity_outliers,
    print_churn_and_complexity_outliers,
)


class TestBasicOutputFunctions:
    """Test basic output formatting functions"""

    def test_big_separator(self):
        """Test big_separator output"""
        result = big_separator()
        assert result == "=" * 99

    def test_print_headline(self, capsys):
        """Test print_headline output"""
        print_headline("Test Headline")
        captured = capsys.readouterr()
        assert "Test Headline" in captured.out
        assert "=" * 99 in captured.out

    def test_print_subsection(self, capsys):
        """Test print_subsection output"""
        print_subsection("Test Subsection")
        captured = capsys.readouterr()
        assert "-= Test Subsection =-" in captured.out

    def test_print_big_separator(self, capsys):
        """Test print_big_separator output"""
        print_big_separator()
        captured = capsys.readouterr()
        assert "=" * 99 in captured.out

    def test_print_small_separator(self, capsys):
        """Test print_small_separator output"""
        print_small_separator()
        captured = capsys.readouterr()
        assert "============================================================" in captured.out


class TestOutlierOutputFunctions:
    """Test outlier output formatting functions"""

    def test_get_outliers_output_empty(self):
        """Test get_outliers_output with empty list"""
        result = get_outliers_output({})
        assert result == "No outliers were found.\n"

    def test_get_outliers_output_with_outliers(self):
        """Test get_outliers_output with outliers"""
        outliers = {"file1.py": {"complexity": 10}, "file2.py": {"complexity": 15}}
        result = get_outliers_output(outliers)
        assert "file1.py" in result
        assert "file2.py" in result

    def test_print_churn_outliers(self, capsys):
        """Test print_churn_outliers output"""
        churn = {"file1.py": 5, "file2.py": 3}
        endings = [".py"]
        print_churn_outliers("2023-01-01", churn, endings, 2)
        captured = capsys.readouterr()
        assert "Churn outliers" in captured.out
        assert "file1.py" in captured.out

    def test_print_complexity_outliers(self, capsys):
        """Test print_complexity_outliers output"""
        complexity = {"file1.py": 10, "file2.py": 8}
        endings = [".py"]
        print_complexity_outliers(complexity, "CCN", "2023-01-01", endings, 2)
        captured = capsys.readouterr()
        assert "Complexity outliers" in captured.out
        assert "file1.py" in captured.out

    @patch('git_outlier.git_outlier.prepare_outlier_analysis')
    @patch('git_outlier.git_outlier.print_plot_and_outliers')
    def test_print_churn_and_complexity_outliers(self, mock_print, mock_prepare):
        """Test print_churn_and_complexity_outliers"""
        mock_prepare.return_value = ("outlier_output", "plot_output")
        complexity = {"file1.py": 10}
        churn = {"file1.py": 5}
        filtered_files = ["file1.py"]
        
        print_churn_and_complexity_outliers(
            complexity, churn, filtered_files, "CCN", "2023-01-01"
        )
        
        mock_prepare.assert_called_once()
        mock_print.assert_called_once()