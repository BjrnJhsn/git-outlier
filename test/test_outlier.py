from git_outlier.git_outlier import *


def test_get_file_name_from_git_log_line():
    # When
    subject = get_file_name_from_git_log_line("  34   28341287341234  filename")

    # Then
    assert subject == "filename"


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

    subject = parse_arguments([".", "-l", "cpp", "-l", "python"])
    assert subject.span == 12
    assert subject.languages == ["cpp", "python"]
