#!/usr/bin/env python3

import logging
import subprocess
import os
import argparse
import sys
from datetime import date
from dateutil.relativedelta import relativedelta
import lizard


def get_git_log_in_current_directory(start_date):
    pipe = subprocess.PIPE

    git_command = [
        "git",
        "log",
        "--numstat",
        "--no-merges",
        "--since=" + start_date,
        "--pretty=",
    ]
    logging.info("Git command: " + str(git_command))
    try:
        process = subprocess.Popen(
            git_command,
            stdout=pipe,
            stderr=pipe,
            universal_newlines=True,
        )
        stdoutput, stderroutput = process.communicate()
    except OSError as err:
        logging.error("OS error: {0}".format(err))
        sys.exit(1)
    except:
        logging.error("Unexpected error: ", sys.exc_info()[0])
        logging.error("Trying to execute the following subprocess: " + str(git_command))
        logging.error("Git problem, exiting...")
        sys.exit(1)

    return stdoutput


def get_file_name_from_git_log_line(line):
    parts = line.split()
    if len(parts) >= 3:
        return parts[2]
    return ""


def get_file_occurences_from_git_log(log):
    file_occurences = {}
    file_names = []
    for line in log.splitlines():
        file_name = get_file_name_from_git_log_line(line)
        if file_name != "":
            if file_name in file_occurences:
                file_occurences[file_name] += 1
            else:
                file_occurences[file_name] = 1
                file_names.append(file_name)
    return file_occurences, file_names


def ordered_list_with_files(dictionary_file_name_occurence):
    return sorted(
        dictionary_file_name_occurence.items(),
        key=lambda kv: (kv[1], kv[0]),
        reverse=True,
    )


def get_diagram_output(
    points_to_plot, outliers_to_plot, max_xval, max_yval, x_axis, y_axis
):
    output = ""
    output = output + y_axis + "\n"
    for y_val in range(max_yval, -1, -1):
        output = output + "|"
        if points_to_plot[y_val] or outliers_to_plot[y_val] is not None:
            for x_val in range(0, max_xval + 1, 1):
                if (
                    outliers_to_plot[y_val] is not None
                    and x_val in outliers_to_plot[y_val]
                ):
                    output = output + "O"
                elif (
                    points_to_plot[y_val] is not None and x_val in points_to_plot[y_val]
                ):
                    output = output + "X"

                else:
                    output = output + " "
        output = output + "\n"
    for x_val in range(0, max_xval + 1, 1):
        output = output + "-"
    output = output + x_axis
    return output


def convert_analysis_to_plot_data(data, x_label, y_label, max_x_output, max_y_output):
    y_max = 0
    x_max = 0
    for value in data.values():
        if value[y_label] > y_max:
            y_max = value[y_label]
        if value[x_label] > x_max:
            x_max = value[x_label]

    points_to_plot = dict()
    outliers_to_plot = dict()
    outliers = dict()
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
                if discretized_xval not in outliers_to_plot[discretized_yval]:
                    outliers_to_plot[discretized_yval].append(discretized_xval)
        else:
            if points_to_plot[discretized_yval] is None:
                points_to_plot[discretized_yval] = [discretized_xval]
            else:
                if discretized_xval not in points_to_plot[discretized_yval]:
                    points_to_plot[discretized_yval].append(discretized_xval)

    return points_to_plot, outliers_to_plot, outliers


def keep_only_files_with_correct_endings(file_list, endings):
    output_list = []
    for item in file_list:
        if type(item) is file_list or type(item) is tuple:
            filename, file_extension = os.path.splitext(item[0])
        else:
            filename, file_extension = os.path.splitext(item)
        if file_extension in endings:
            output_list.append(item)
    return output_list


def get_complexity_for_file_list(file_list, complexity_metric):
    complexity = {}
    for file_name in file_list:
        if os.path.isfile(file_name):
            logging.info("Analyzing " + str(file_name))
            result = run_analyzer_on_file(file_name)
            if complexity_metric == "CCN":
                complexity[file_name] = result.CCN
            elif complexity_metric == "NLOC":
                complexity[file_name] = result.nloc
            else:
                logging.error("Internal error: Unknown complexity metric specified")
                sys.exit(1)
    return complexity


def run_analyzer_on_file(file_name):
    return lizard.analyze_file(file_name)


def combine_churn_and_complexity(file_occurence, complexity, filtered_file_names):
    result = {}
    for file_name in filtered_file_names:
        if file_name in file_occurence and file_name in complexity:
            result[file_name] = {
                "Churn": file_occurence[file_name],
                "Complexity": complexity[file_name],
            }
    return result


def get_outliers_output(outliers):
    if len(outliers) == 0:
        return "No outliers were found.\n"
    else:
        output = ""
        for key in outliers:
            output = output + key + "\n"
        return output


def big_separator():
    return (
        "=================================================="
        + "================================================="
    )


def print_headline(headline):
    print("\n" + big_separator())
    print("=  " + headline)
    print(big_separator() + "\n")


def print_subsection(subsection):
    print("\n-= " + subsection + " =-")


def print_big_separator():
    print("\n" + big_separator())


def print_small_separator():
    print("\n============================================================n")


def print_churn_and_complexity_outliers(
    complexity, file_occurence, filtered_file_names, complexity_metric, start_date
):
    outlier_output, plot_output = prepare_churn_and_complexity_outliers_output(
        complexity, complexity_metric, file_occurence, filtered_file_names
    )
    print_plot_and_outliers(plot_output, outlier_output, start_date)


def prepare_churn_and_complexity_outliers_output(
    complexity, complexity_metric, file_occurence, filtered_file_names
):
    analysis_result = combine_churn_and_complexity(
        file_occurence, complexity, filtered_file_names
    )
    x_label = "Complexity"
    y_label = "Churn"
    max_x_output = 80
    max_y_output = 20
    points_to_plot, outliers_to_plot, outliers = convert_analysis_to_plot_data(
        analysis_result, x_label, y_label, max_x_output, max_y_output
    )
    plot_output = get_diagram_output(
        points_to_plot,
        outliers_to_plot,
        max_x_output,
        max_y_output,
        "Churn",
        "Complexity(" + str(complexity_metric) + ")",
    )
    outlier_output = get_outliers_output(outliers)
    return outlier_output, plot_output


def print_plot_and_outliers(diagram_output, outlier_output, start_date):
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
    complexity, complexity_metric, start_date, endings, top_complexity=10
):
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
    cleaned_ordered_list_with_files = keep_only_files_with_correct_endings(
        ordered_list_with_files(complexity), endings
    )
    print("Complexity Filenames")
    for items in cleaned_ordered_list_with_files[0:top_complexity]:
        print(f"{str(items[1]):11}{items[0]:10}")


def print_churn_outliers(start_date, file_occurence, endings, top_churners=10):
    print_headline("Churn outliers")
    print_subsection(
        "The top "
        + str(top_churners)
        + " files with churn in descending order since "
        + start_date
        + ":"
    )
    cleaned_ordered_list_with_files = keep_only_files_with_correct_endings(
        ordered_list_with_files(file_occurence), endings
    )
    print("Changes Filenames")
    for items in cleaned_ordered_list_with_files[0:top_churners]:
        print(f"{str(items[1]):8}{items[0]:10}")


def get_git_and_complexity_data(endings, complexity_metric, start_date):
    all_of_it = get_git_log_in_current_directory(start_date)
    print("Retrieving git log...")
    file_occurence, file_names = get_file_occurences_from_git_log(all_of_it)
    filtered_file_names = keep_only_files_with_correct_endings(file_names, endings)
    print("Computing complexity...")
    complexity = get_complexity_for_file_list(filtered_file_names, complexity_metric)
    print(str(len(filtered_file_names)) + " files analyzed.")
    return complexity, file_occurence, filtered_file_names


def get_supported_languages():
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


def get_file_endings_for_languages(languages):
    supported_languages = get_supported_languages()
    language_file_endings = []
    if not isinstance(languages, list):
        languages = [languages]
    for language in languages:
        if language in supported_languages:
            language_file_endings.extend(supported_languages[language])
    return language_file_endings


def parse_arguments(incoming):
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

    if args.span and args.span < 1 or args.span > 100:
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

    # Need to fix :-)
    if args.languages is None:
        args.languages = supported_languages_list

    if not all(elem in supported_languages_list for elem in args.languages):
        parser.error("Unsupported languages: " + str(args.languages))

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    args.level = levels[
        min(len(levels) - 1, args.verbose)
    ]  # capped to number of levels

    return args


def switch_to_correct_path_and_save_current(path_to_switch):
    startup_path = os.getcwd()
    try:
        expanded_path = os.path.expanduser(path_to_switch)
        os.chdir(expanded_path)
    except OSError as err:
        logging.error("OS error: {0}".format(err))
        sys.exit(1)
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)
    return startup_path


def switch_back_original_directory(path):
    try:
        os.chdir(path)
    except OSError as err:
        logging.error("OS error: {0}".format(err))
        sys.exit(1)
    except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)


def get_start_date(span_in_months):
    today = date.today()
    if isinstance(span_in_months, list):
        span_in_months = span_in_months[0]
    assert span_in_months >= 0
    start = today + relativedelta(months=-span_in_months)
    return str(start)


def main():

    options = parse_arguments(sys.argv[1:])
    logging.basicConfig(
        level=options.level, format="%(asctime)s %(levelname)s %(message)s"
    )

    startup_path = switch_to_correct_path_and_save_current(options.path)

    endings = get_file_endings_for_languages(options.languages)
    start_date = get_start_date(options.span)
    (
        computed_complexity,
        file_occurence,
        filtered_file_names,
    ) = get_git_and_complexity_data(endings, options.metric, start_date)

    switch_back_original_directory(startup_path)

    print_churn_outliers(start_date, file_occurence, endings, options.top)

    print_complexity_outliers(
        computed_complexity, options.metric, start_date, endings, options.top
    )

    print_churn_and_complexity_outliers(
        computed_complexity,
        file_occurence,
        filtered_file_names,
        options.metric,
        start_date,
    )

    print_big_separator()


if __name__ == "__main__":
    main()
