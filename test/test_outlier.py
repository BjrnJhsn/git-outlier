from git_outlier.git_outlier import *
from unittest.mock import patch


def test_get_file_name_from_git_log_line():
    # When
    subject = get_file_name_from_git_log_line("  34   28341287341234  filename")

    # Then
    assert subject == "filename"

    # When
    subject = get_file_name_from_git_log_line("1 2")

    # Then
    assert subject == ""


def test_get_file_occurences_from_git_log():
    # When
    file_occurences, file_names = get_file_occurences_from_git_log(
        "  34   28341287341234  filename        \n123                      123 filename \n 456 bla filename2 \n - - filename3 \n - - filename3 \n 123 123 filename3"
    )

    # Then
    assert file_occurences["filename"] == 2
    assert file_occurences["filename2"] == 1
    assert file_occurences["filename3"] == 3


def test_ordered_list_with_files():
    # When
    subject = ordered_list_with_files({"filename": 2, "filename2": 1, "filename3": 3})

    # Then
    assert subject[0][0] == "filename3"
    assert subject[0][1] == 3
    assert subject[2][0] == "filename2"
    assert subject[2][1] == 1


def test_get_diagram_output():
    # When
    points_to_plot = {0: None, 1: None, 2: None}
    outliers_to_plot = {0: None, 1: None, 2: None}
    max_xval = 2
    max_yval = 2
    x_axis = "xAxis"
    y_axis = "yAxis"

    subject = get_diagram_output(
        points_to_plot, outliers_to_plot, max_xval, max_yval, x_axis, y_axis
    )

    # Then
    assert subject == "yAxis\n|\n|\n|\n---xAxis"

    # When
    points_to_plot = {0: None, 1: None, 2: None}
    outliers_to_plot = {0: None, 1: None, 2: None}
    max_xval = 3
    max_yval = 2
    x_axis = "xAxis"
    y_axis = "yAxis"

    subject = get_diagram_output(
        points_to_plot, outliers_to_plot, max_xval, max_yval, x_axis, y_axis
    )

    # Then
    assert subject == "yAxis\n|\n|\n|\n----xAxis"

    # When
    points_to_plot = {0: None, 1: None, 2: None, 3: None, 4: None, 5: [0], 6: [0]}
    outliers_to_plot = {0: None, 1: None, 2: None, 3: None, 4: None, 5: [0], 6: [1]}
    max_xval = 5
    max_yval = 6
    x_axis = "xAxis"
    y_axis = "yAxis"

    subject = get_diagram_output(
        points_to_plot, outliers_to_plot, max_xval, max_yval, x_axis, y_axis
    )

    # Then
    assert subject == "yAxis\n|XO    \n|O     \n|\n|\n|\n|\n|\n------xAxis"


def test_keep_only_files_with_correct_ending():
    subject = keep_only_files_with_correct_endings(
        ["test.py", "yada.py", "keepMe.txt", "DontKeepMe.cpp"], [".txt", ".py"]
    )
    assert subject[0] == "test.py"
    assert subject[1] == "yada.py"
    assert subject[2] == "keepMe.txt"


def test_get_file_endings_for_languages():
    subject = get_file_endings_for_languages(["cpp", "python"])
    assert subject[0] == ".cpp"
    assert subject[1] == ".cc"
    assert subject[2] == ".mm"
    assert subject[3] == ".cxx"
    assert subject[4] == ".h"
    assert subject[5] == ".hpp"
    assert subject[6] == ".py"

    subject = get_file_endings_for_languages(["cpp"])
    assert subject[0] == ".cpp"
    assert subject[1] == ".cc"
    assert subject[2] == ".mm"
    assert subject[3] == ".cxx"
    assert subject[4] == ".h"
    assert subject[5] == ".hpp"

    subject = get_file_endings_for_languages("cpp")
    assert subject[0] == ".cpp"
    assert subject[1] == ".cc"
    assert subject[2] == ".mm"
    assert subject[3] == ".cxx"
    assert subject[4] == ".h"
    assert subject[5] == ".hpp"


def test_argument_parser():
    subject = parse_arguments(".")
    assert subject.span == 12
    assert subject.languages == ["python"]
    assert subject.path == "."

    subject = parse_arguments("")
    assert subject.span == 12
    assert subject.languages == ["python"]
    assert subject.path == "."

    subject = parse_arguments([".", "-l", "cpp", "-l", "python"])
    assert subject.span == 12
    assert subject.languages == ["cpp", "python"]
    assert subject.path == "."


@patch("sys.exit")
@patch("git_outlier.git_outlier.run_analyzer_on_file")
@patch("os.path.isfile", return_value=True)
def test_get_complexity_for_file_list(mock_io, mock_run_analyzer, mock_sys_exit):
    assert mock_io is os.path.isfile
    file_list = ["test.py"]
    subject = get_complexity_for_file_list(file_list, "CCN")
    mock_io.assert_called_once_with(file_list[0])
    mock_run_analyzer.assert_called_once_with("test.py")

    subject = get_complexity_for_file_list(["test.py"], "Does not exist")
    mock_sys_exit.assert_called_once()
