#!/usr/bin/env python3

import logging
import subprocess
import os
import argparse
import sys
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as parse_date
from typing import Dict, List, Tuple, Union, Any, Optional, Sequence
import lizard


def get_git_log_in_current_directory(
    start_date: str, end_date: Optional[str] = None
) -> str:
    pipe = subprocess.PIPE

    git_command = [
        "git",
        "log",
        "--numstat",
        "--no-merges",
        f"--since={start_date}",
        "--pretty=",
    ]

    # Add --until parameter if end_date is provided
    if end_date:
        git_command.insert(-1, f"--until={end_date}")
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


def sort_by_occurrence(
    dictionary_file_name_occurence: Dict[str, int],
) -> List[Tuple[str, int]]:
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
    y_axis: str,
) -> str:
    lines = [y_axis]
    for y_val in range(max_yval, -1, -1):
        line = "|"
        if points_to_plot[y_val] is not None or outliers_to_plot[y_val] is not None:
            for x_val in range(0, max_xval + 1, 1):
                outlier_list = outliers_to_plot[y_val]
                point_list = points_to_plot[y_val]
                if outlier_list is not None and x_val in outlier_list:
                    line += "o"
                elif point_list is not None and x_val in point_list:
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
    max_y_output: int,
) -> Tuple[
    Dict[int, Optional[List[int]]],
    Dict[int, Optional[List[int]]],
    Dict[str, Dict[str, int]],
]:
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


def filter_files_by_extension(
    file_list: Sequence[Union[str, Tuple[str, int]]], endings: List[str]
) -> List[Union[str, Tuple[str, int]]]:
    output_list = []
    for item in file_list:
        if isinstance(item, tuple):
            filename, file_extension = os.path.splitext(item[0])
        else:
            filename, file_extension = os.path.splitext(item)
        if file_extension in endings:
            output_list.append(item)
    return output_list


def get_complexity_for_file_list(
    file_list: List[str], complexity_metric: str
) -> Dict[str, int]:
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
    churn: Dict[str, int], complexity: Dict[str, int], filtered_file_names: List[str]
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
    start_date: str,
) -> None:
    outlier_output, plot_output = prepare_outlier_analysis(
        complexity, complexity_metric, churn, filtered_file_names
    )
    print_plot_and_outliers(plot_output, outlier_output, start_date)


def prepare_outlier_analysis(
    complexity: Dict[str, int],
    complexity_metric: str,
    churn: Dict[str, int],
    filtered_file_names: List[str],
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


def print_plot_and_outliers(
    diagram_output: str, outlier_output: str, start_date: str
) -> None:
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
    top_complexity: int = 10,
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
    start_date: str, churn: Dict[str, int], endings: List[str], top_churners: int = 10
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
    start_date: str,
    end_date: Optional[str] = None,
) -> Tuple[Dict[str, int], Dict[str, int], List[str]]:
    all_of_it = get_git_log_in_current_directory(start_date, end_date)
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
        description="Find refactoring candidates by analyzing git history and code complexity.",
        epilog="""Examples:
  git outlier                            # analyze last 12 months (if installed as git add-on)
  git-outlier                            # same as above, direct invocation
  git outlier --since="6 months ago"     # analyze last 6 months  
  git outlier --since="2023-01-01" --until="2023-12-31"  # specific date range
  git outlier -l python -l javascript    # analyze only Python and JavaScript
  git outlier --metric=NLOC              # use lines of code instead of cyclomatic complexity

For more information, see: https://github.com/BjrnJhsn/git-outlier""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    supported_languages = get_supported_languages()
    supported_languages_list = [*supported_languages]
    parser.add_argument(
        "--languages",
        "-l",
        action="append",
        metavar="<lang>",
        help="Only analyze specified languages (can be repeated). "
        f"Default: all supported languages. Available: {', '.join(sorted(supported_languages))}",
        type=str,
    )
    parser.add_argument(
        "--metric",
        "-m",
        metavar="<type>",
        help="Complexity metric to use: CCN (cyclomatic complexity) or NLOC (lines of code). Default: CCN",
        default="CCN",
    )
    parser.add_argument(
        "--since",
        metavar="<date>",
        help="Show commits more recent than specific date. "
        "Accepts: '2023-01-01', '6 months ago', 'last week'. Default: 12 months ago",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--until",
        metavar="<date>",
        help="Show commits older than specific date. "
        "Accepts: '2023-12-31', '1 month ago', 'yesterday'. Default: today",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--top",
        "-t",
        metavar="<n>",
        help="Limit output to top N outliers per category. Default: 10",
        default=10,
        type=int,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to git repository to analyze. Default: current directory",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Be more verbose (can be repeated for more detail)",
    )

    args = parser.parse_args(incoming)

    # Validate date parameters
    try:
        if args.since:
            parse_git_date(args.since)
        if args.until:
            parse_git_date(args.until)
    except ValueError as e:
        parser.error(str(e))

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


def parse_git_date(date_str: Optional[str], default_months_ago: int = 0) -> str:
    """Parse git-style date string into ISO format for git log --since/--until"""
    if date_str is None:
        # Default behavior - go back specified months or use today
        if default_months_ago == 0:
            return str(date.today())
        else:
            start = date.today() + relativedelta(months=-default_months_ago)
            return str(start)

    # Handle relative dates like "6 months ago", "last week", etc.
    date_str = date_str.strip().lower()

    # Common git-style relative dates
    if "years ago" in date_str or "year ago" in date_str:
        try:
            years = int(date_str.split()[0])
            start = date.today() + relativedelta(years=-years)
            return str(start)
        except (ValueError, IndexError):
            pass
    elif "months ago" in date_str or "month ago" in date_str:
        try:
            months = int(date_str.split()[0])
            start = date.today() + relativedelta(months=-months)
            return str(start)
        except (ValueError, IndexError):
            pass
    elif "weeks ago" in date_str or "week ago" in date_str:
        try:
            weeks = int(date_str.split()[0])
            start = date.today() + relativedelta(weeks=-weeks)
            return str(start)
        except (ValueError, IndexError):
            pass
    elif "days ago" in date_str or "day ago" in date_str:
        try:
            days = int(date_str.split()[0])
            start = date.today() + relativedelta(days=-days)
            return str(start)
        except (ValueError, IndexError):
            pass
    elif date_str in ["yesterday"]:
        start = date.today() + relativedelta(days=-1)
        return str(start)
    elif date_str in ["last week"]:
        start = date.today() + relativedelta(weeks=-1)
        return str(start)
    elif date_str in ["last month"]:
        start = date.today() + relativedelta(months=-1)
        return str(start)
    elif date_str in ["last year"]:
        start = date.today() + relativedelta(years=-1)
        return str(start)
    elif date_str in ["today"]:
        return str(date.today())

    # Try to parse as absolute date using dateutil
    try:
        parsed_date = parse_date(date_str)
        return str(parsed_date.date())
    except Exception as e:
        raise ValueError(f"Unable to parse date '{date_str}': {e}")


def get_date_range(
    since: Optional[str], until: Optional[str]
) -> Tuple[str, Optional[str]]:
    """Get the date range for git log analysis, handling both --since and --until"""
    # If no since specified, default to 12 months ago
    start_date = parse_git_date(since, default_months_ago=12)

    # Parse until date if provided
    end_date = parse_git_date(until, default_months_ago=0) if until else None

    return start_date, end_date


def main() -> None:

    options = parse_arguments(sys.argv[1:])
    logging.basicConfig(
        level=options.level, format="%(asctime)s %(levelname)s %(message)s"
    )

    startup_path = change_directory(options.path)

    endings = get_file_endings_for_languages(options.languages)
    start_date, end_date = get_date_range(options.since, options.until)
    (
        computed_complexity,
        churn,
        filtered_file_names,
    ) = get_git_and_complexity_data(endings, options.metric, start_date, end_date)

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
