"""
Test plot and diagram generation functions for git-outlier.
"""

import pytest
from git_outlier.git_outlier import convert_analysis_to_plot_data, get_diagram_output


class TestDiagramGeneration:
    """Test diagram and plot generation functions"""

    def test_convert_analysis_to_plot_data_comprehensive(self):
        """Test convert_analysis_to_plot_data with various scenarios"""
        # Test with mixed outliers and non-outliers
        data = {
            "high_churn_high_complexity.py": {"Churn": 20, "Complexity": 15},
            "low_churn_low_complexity.py": {"Churn": 2, "Complexity": 1},
            "medium_file.py": {"Churn": 10, "Complexity": 8},
        }

        points_to_plot, outliers_to_plot, outliers = convert_analysis_to_plot_data(
            data, "Churn", "Complexity", 20, 10
        )

        # Should have outliers in high churn/complexity zone
        assert len(outliers) > 0
        assert isinstance(points_to_plot, dict)
        assert isinstance(outliers_to_plot, dict)

    def test_convert_analysis_to_plot_data_no_outliers(self):
        """Test convert_analysis_to_plot_data with no outliers"""
        data = {
            "low_complexity.py": {"Churn": 1, "Complexity": 1},
            "medium_file.py": {"Churn": 5, "Complexity": 3},
            "high_churn_low_complexity.py": {"Churn": 10, "Complexity": 1},
            "high_complexity_low_churn.py": {"Churn": 1, "Complexity": 10},
        }

        points_to_plot, outliers_to_plot, outliers = convert_analysis_to_plot_data(
            data, "Churn", "Complexity", 20, 10
        )

        # Should have no outliers (none in upper-right quadrant)
        assert len(outliers) == 0
        assert isinstance(points_to_plot, dict)
        assert isinstance(outliers_to_plot, dict)

    def test_convert_analysis_to_plot_data_all_outliers(self):
        """Test convert_analysis_to_plot_data with all files as outliers"""
        data = {
            "high1.py": {"Churn": 18, "Complexity": 15},
            "high2.py": {"Churn": 20, "Complexity": 18},
            "high3.py": {"Churn": 19, "Complexity": 16},
        }

        points_to_plot, outliers_to_plot, outliers = convert_analysis_to_plot_data(
            data, "Churn", "Complexity", 20, 18
        )

        # All should be outliers
        assert len(outliers) == 3
        assert isinstance(points_to_plot, dict)
        assert isinstance(outliers_to_plot, dict)

    def test_get_diagram_output_empty(self):
        """Test get_diagram_output with empty data"""
        points_to_plot = {0: None, 1: None, 2: None}
        outliers_to_plot = {0: None, 1: None, 2: None}
        max_xval = 2
        max_yval = 2
        x_axis = "xAxis"
        y_axis = "yAxis"

        result = get_diagram_output(
            points_to_plot, outliers_to_plot, max_xval, max_yval, x_axis, y_axis
        )

        assert "yAxis" in result
        assert "xAxis" in result
        assert result == "yAxis\n|\n|\n|\n---xAxis"

    def test_get_diagram_output_with_data(self):
        """Test get_diagram_output with points and outliers"""
        points_to_plot = {0: None, 1: None, 2: None, 3: None, 4: None, 5: [0], 6: [0]}
        outliers_to_plot = {0: None, 1: None, 2: None, 3: None, 4: None, 5: [0], 6: [1]}
        max_xval = 5
        max_yval = 6
        x_axis = "xAxis"
        y_axis = "yAxis"

        result = get_diagram_output(
            points_to_plot, outliers_to_plot, max_xval, max_yval, x_axis, y_axis
        )

        assert "yAxis" in result
        assert "xAxis" in result
        assert "o" in result  # outlier marker
        assert "." in result  # point marker
