#!/usr/bin/env python3

import logging
import subprocess
import os
import argparse
import sys
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Tuple, Union, Any, Optional, Sequence
import lizard


def get_git_log_in_current_directory(start_date: str) -> str:
    pipe = subprocess.PIPE

    git_command = [
        "git",
        "log",
        "--numstat",
        "--no-merges",
        f"--since={start_date}",
        "--pretty=",
    ]
    logging.info(f"Git command: {git_command}")
    try:
        process = subprocess.Popen(
            git_command,
            stdout=pipe,
            stderr=pipe,
            universal_newlines=True,
        )
        stdoutput, stderroutput = process.communicate()

        # Check if git command failed (e.g., not in a git repository)
        if process.returncode != 0:
            if "not a git repository" in stderroutput.lower():
                logging.error("fatal: not a git repository")
                sys.exit(128)  # Git's standard exit code for "not a git repository"
            elif "does not have any commits yet" in stderroutput.lower():
                # Empty repository with no commits - return empty string instead of exiting
                logging.info("Repository has no commits yet")
                return ""
            else:
                logging.error(f"Git command failed: {stderroutput}")
                sys.exit(1)
    except OSError as err:
        logging.error(f"OS error: {err}")
        sys.exit(1)
    except Exception as err:
        logging.error("Unexpected error: %s", err)
        logging.error("Trying to execute the following subprocess: %s", git_command)
        logging.error("Git problem, exiting...")
        sys.exit(1)

    return stdoutput


def parse_filename_from_log(line: str) -> str:
    parts = line.split()
    if len(parts) >= 3:
        return parts[2]
    return ""


def parse_churn_from_log(log: str) -> Tuple[Dict[str, int], List[str]]:
    churn: Dict[str, int] = {}
    file_names: List[str] = []
    for line in log.splitlines():
        file_name = parse_filename_from_log(line)
        if file_name != "":
            if file_name in churn:
                churn[file_name] += 1
            else:
                churn[file_name] = 1
                file_names.append(file_name)
    return churn, file_names


def sort_by_occurrence(dictionary_file_name_occurence: Dict[str, int]) -> List[Tuple[str, int]]:
    return sorted(
        dictionary_file_name_occurence.items(),
        key=lambda kv: (kv[1], kv[0]),
        reverse=True,
    )


def get_diagram_output(
    points_to_plot: Dict[int, Optional[List[int]]], 
    outliers_to_plot: Dict[int, Optional[List[int]]], 
    max_xval: int, 
    max_yval: int, 
    x_axis: str, 
    y_axis: str
) -> str:
    lines = [y_axis]
    for y_val in range(max_yval, -1, -1):
        line = "|"
        if points_to_plot[y_val] is not None or outliers_to_plot[y_val] is not None:
            for x_val in range(0, max_xval + 1, 1):
                outlier_list = outliers_to_plot[y_val]
                point_list = points_to_plot[y_val]
                if (
                    outlier_list is not None
                    and x_val in outlier_list
                ):
                    line += "o"
                elif (
                    point_list is not None and x_val in point_list
                ):
                    line += "."
                else:
                    line += " "
        lines.append(line)
    lines.append("-" * (max_xval + 1) + x_axis)
    return "\n".join(lines)


def convert_analysis_to_plot_data(
    data: Dict[str, Dict[str, int]], 
    x_label: str, 
    y_label: str, 
    max_x_output: int, 
    max_y_output: int
) -> Tuple[Dict[int, Optional[List[int]]], Dict[int, Optional[List[int]]], Dict[str, Dict[str, int]]]:
    y_max = 0
    x_max = 0
    for value in data.values():
        if value[y_label] > y_max:
            y_max = value[y_label]
        if value[x_label] > x_max:
            x_max = value[x_label]

    points_to_plot: Dict[int, Optional[List[int]]] = dict()
    outliers_to_plot: Dict[int, Optional[List[int]]] = dict()
    outliers: Dict[str, Dict[str, int]] = dict()
    for y_val in range(max_y_output, -1, -1):
        points_to_plot[y_val] = None
        outliers_to_plot[y_val] = None
    for file_name, value in data.items():
        discretized_yval = round(value[y_label] / y_max * max_y_output)
        discretized_xval = round(value[x_label] / x_max * max_x_output)
        outlier = (
            discretized_xval > max_x_output / 2 and discretized_yval > max_y_output / 2
        )
        if outlier:
            outliers[file_name] = value
            if outliers_to_plot[discretized_yval] is None:
                outliers_to_plot[discretized_yval] = [discretized_xval]
            else:
                outlier_list = outliers_to_plot[discretized_yval]
                if outlier_list is not None and discretized_xval not in outlier_list:
                    outlier_list.append(discretized_xval)
        else:
            if points_to_plot[discretized_yval] is None:
                points_to_plot[discretized_yval] = [discretized_xval]
            else:
                point_list = points_to_plot[discretized_yval]
                if point_list is not None and discretized_xval not in point_list:
                    point_list.append(discretized_xval)

    return points_to_plot, outliers_to_plot, outliers


def filter_files_by_extension(file_list: Sequence[Union[str, Tuple[str, int]]], endings: List[str]) -> List[Union[str, Tuple[str, int]]]:
    output_list = []
    for item in file_list:
        if isinstance(item, tuple):
            filename, file_extension = os.path.splitext(item[0])
        else:
            filename, file_extension = os.path.splitext(item)
        if file_extension in endings:
            output_list.append(item)
    return output_list


def get_complexity_for_file_list(file_list: List[str], complexity_metric: str) -> Dict[str, int]:
    complexity = {}
    for file_name in file_list:
        if os.path.isfile(file_name):
            logging.info(f"Analyzing {file_name}")
            result = run_analyzer_on_file(file_name)
            if complexity_metric == "CCN":
                complexity[file_name] = result.CCN
            elif complexity_metric == "NLOC":
                complexity[file_name] = result.nloc
            else:
                logging.error("Internal error: Unknown complexity metric specified")
                sys.exit(1)
    return complexity


def run_analyzer_on_file(file_name: str) -> Any:
    return lizard.analyze_file(file_name)


def combine_churn_and_complexity(
    churn: Dict[str, int], 
    complexity: Dict[str, int], 
    filtered_file_names: List[str]
) -> Dict[str, Dict[str, int]]:
    result = {}
    for file_name in filtered_file_names:
        if file_name in churn and file_name in complexity:
            result[file_name] = {
                "Churn": churn[file_name],
                "Complexity": complexity[file_name],
            }
    return result


def get_outliers_output(outliers: Dict[str, Any]) -> str:
    if len(outliers) == 0:
        return "No outliers were found.\n"
    else:
        return "\n".join(outliers) + "\n"


def big_separator() -> str:
    return "=" * 99


def print_headline(headline: str) -> None:
    print(f"\n{big_separator()}")
    print(f"=  {headline}")
    print(f"{big_separator()}\n")


def print_subsection(subsection: str) -> None:
    print(f"\n-= {subsection} =-")


def print_big_separator() -> None:
    print(f"\n{big_separator()}")


def print_small_separator() -> None:
    print("\n============================================================\n")


def print_churn_and_complexity_outliers(
    complexity: Dict[str, int], 
    churn: Dict[str, int], 
    filtered_file_names: List[str], 
    complexity_metric: str, 
    start_date: str
) -> None:
    outlier_output, plot_output = prepare_outlier_analysis(
        complexity, complexity_metric, churn, filtered_file_names
    )
    print_plot_and_outliers(plot_output, outlier_output, start_date)


def prepare_outlier_analysis(
    complexity: Dict[str, int], 
    complexity_metric: str, 
    churn: Dict[str, int], 
    filtered_file_names: List[str]
) -> Tuple[str, str]:
    analysis_result = combine_churn_and_complexity(
        churn, complexity, filtered_file_names
    )
    x_label = "Complexity"
    y_label = "Churn"
    max_x_output = 70
    max_y_output = 30
    points_to_plot, outliers_to_plot, outliers = convert_analysis_to_plot_data(
        analysis_result, x_label, y_label, max_x_output, max_y_output
    )
    x_label_to_print = f"{x_label}({complexity_metric})"
    y_label_to_print = y_label
    plot_output = get_diagram_output(
        points_to_plot,
        outliers_to_plot,
        max_x_output,
        max_y_output,
        x_label_to_print,
        y_label_to_print,
    )
    outlier_output = get_outliers_output(outliers)
    return outlier_output, plot_output


def print_plot_and_outliers(diagram_output: str, outlier_output: str, start_date: str) -> None:
    print_headline("Churn vs complexity outliers")
    print_subsection(
        "Plot of churn vs complexity for all files since "
        + start_date
        + ". Outliers are marked with O"
    )
    print(diagram_output)
    print_subsection("Detected outliers (marked with O in the outlier plot)")
    print(outlier_output)


def print_complexity_outliers(
    complexity: Dict[str, int], 
    complexity_metric: str, 
    start_date: str, 
    endings: List[str], 
    top_complexity: int = 10
) -> None:
    print_headline("Complexity outliers")
    print_subsection(
        "The top "
        + str(top_complexity)
        + " files with complexity ("
        + str(complexity_metric)
        + ") in descending order since "
        + start_date
        + ":"
    )
    cleaned_ordered_list_with_files = filter_files_by_extension(
        sort_by_occurrence(complexity), endings
    )
    print("Complexity Filenames")
    for items in cleaned_ordered_list_with_files[0:top_complexity]:
        print(f"{str(items[1]):11}{items[0]:10}")


def print_churn_outliers(
    start_date: str, 
    churn: Dict[str, int], 
    endings: List[str], 
    top_churners: int = 10
) -> None:
    print_headline("Churn outliers")
    print_subsection(
        "The top "
        + str(top_churners)
        + " files with churn in descending order since "
        + start_date
        + ":"
    )
    cleaned_ordered_list_with_files = filter_files_by_extension(
        sort_by_occurrence(churn), endings
    )
    print("Changes Filenames")
    for items in cleaned_ordered_list_with_files[0:top_churners]:
        print(f"{str(items[1]):8}{items[0]:10}")


def get_git_and_complexity_data(
    endings: List[str], 
    complexity_metric: str, 
    start_date: str
) -> Tuple[Dict[str, int], Dict[str, int], List[str]]:
    all_of_it = get_git_log_in_current_directory(start_date)
    print("Retrieving git log...")
    churn, file_names = parse_churn_from_log(all_of_it)
    filtered_file_names = filter_files_by_extension(file_names, endings)
    print("Computing complexity...")
    complexity = get_complexity_for_file_list(filtered_file_names, complexity_metric)  # type: ignore
    print(f"{len(filtered_file_names)} files analyzed.")
    return complexity, churn, filtered_file_names  # type: ignore


def get_supported_languages() -> Dict[str, List[str]]:
    return {
        "c": [".c", ".h"],
        "cpp": [".cpp", ".cc", ".mm", ".cxx", ".h", ".hpp"],
        "csharp": [".cs"],
        "fortran": [
            ".f70",
            ".f90",
            ".f95",
            ".f03",
            ".f08",
            ".f",
            ".for",
            ".ftn",
            ".fpp",
        ],
        "go": [".go"],
        "java": [".java"],
        "javascript": [".js"],
        "lua": [".lua"],
        "objective-c": [".m", ".mm"],
        "php": [".php"],
        "python": [".py"],
        "ruby": [".rb"],
        "rust": [".rs"],
        "scala": [".scala"],
        "swift": [".swift"],
        "typescript": [".ts"],
    }


def get_file_endings_for_languages(languages: Union[str, List[str]]) -> List[str]:
    supported_languages = get_supported_languages()
    language_file_endings = []
    if not isinstance(languages, list):
        languages = [languages]
    for language in languages:
        if language in supported_languages:
            language_file_endings.extend(supported_languages[language])
    return language_file_endings


def parse_arguments(incoming: List[str]) -> Any:
    parser = argparse.ArgumentParser(
        description="""Analyze a source directory that uses git as version handling system.
        The source files are analyzed for different type of outliers and these outliers can 
        be good candidates for refactoring to increase maintainability. The source files 
        are ranked in falling order after churn, complexity, and combined churn 
        and complexity."""
    )
    supported_languages = get_supported_languages()
    supported_languages_list = [*supported_languages]
    parser.add_argument(
        "--languages",
        "-l",
        action="append",
        help="List the programming languages you want to analyze. If left empty, it'll"
        " search for all recognized languages. Example: 'outlier -l cpp -l python' searches for"
        " C++ and Python code. The available languages are: "
        + ", ".join(supported_languages),
        type=str,
    )
    parser.add_argument(
        "--metric",
        "-m",
        help="Choose the complexity metric you would like to base the results on. Either cyclomatic"
        " complexity 'CCN' or lines of code without comments 'NLOC'. If not specified,"
        " the default is 'CCN'.",
        default="CCN",
    )
    parser.add_argument(
        "--span",
        "-s",
        help="The number (integer) of months the analysis will look at. Default is 12 months.",
        default=12,
        type=int,
    )
    parser.add_argument(
        "--top",
        "-t",
        help="The number (integer) of outliers to show. Note that for the combined churn and complexity outliers,"
        " there is no maximum. Default is 10.",
        default=10,
        type=int,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="The path to the source directory to be analyzed. Will default to current "
        "directory if not present.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Show analysis details and debug info.",
    )

    args = parser.parse_args(incoming)

    if args.span and (args.span < 1 or args.span > 100):
        parser.error("Span must be in the range (1,100).")

    ok_metrics = ["NLOC", "CCN"]
    if args.metric not in ok_metrics:
        parser.error(
            str(args.metric)
            + " is not a valid option for complexity metric. Please choose from: "
            + str(ok_metrics)
        )

    supported_languages = get_supported_languages()
    supported_languages_list = [*supported_languages]

    if args.languages is None:
        args.languages = supported_languages_list

    if not all(elem in supported_languages_list for elem in args.languages):
        parser.error(f"Unsupported languages: {args.languages}")

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    args.level = levels[
        min(len(levels) - 1, args.verbose)
    ]  # capped to number of levels

    return args


def change_directory(path_to_switch: str) -> str:
    startup_path = os.getcwd()
    try:
        expanded_path = os.path.expanduser(path_to_switch)
        os.chdir(expanded_path)
    except OSError as err:
        logging.error(f"OS error: {err}")
        sys.exit(1)
    except Exception as err:
        logging.error("Unexpected error: %s", err)
        sys.exit(1)
    return startup_path


def restore_directory(path: str) -> None:
    try:
        os.chdir(path)
    except OSError as err:
        logging.error(f"OS error: {err}")
        sys.exit(1)
    except Exception as err:
        logging.error("Unexpected error: %s", err)
        sys.exit(1)


def get_start_date(span_in_months: Union[int, List[int]]) -> str:
    today = date.today()
    if isinstance(span_in_months, list):
        span_in_months = span_in_months[0]
    assert span_in_months >= 0
    start = today + relativedelta(months=-span_in_months)
    return str(start)


def main() -> None:

    options = parse_arguments(sys.argv[1:])
    logging.basicConfig(
        level=options.level, format="%(asctime)s %(levelname)s %(message)s"
    )

    startup_path = change_directory(options.path)

    endings = get_file_endings_for_languages(options.languages)
    start_date = get_start_date(options.span)
    (
        computed_complexity,
        churn,
        filtered_file_names,
    ) = get_git_and_complexity_data(endings, options.metric, start_date)

    restore_directory(startup_path)

    print_churn_outliers(start_date, churn, endings, options.top)

    print_complexity_outliers(
        computed_complexity, options.metric, start_date, endings, options.top
    )

    print_churn_and_complexity_outliers(
        computed_complexity,
        churn,
        filtered_file_names,
        options.metric,
        start_date,
    )

    print_big_separator()


if __name__ == "__main__":
    main()
