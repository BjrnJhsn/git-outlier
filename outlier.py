#!/usr/bin/env python3


import subprocess
import os
import argparse
import sys
import lizard
from datetime import date
from dateutil.relativedelta import relativedelta


def get_git_log_in_current_directory(start_date):
    pipe = subprocess.PIPE

    # git log --numstat --pretty="" --no-merges

    try:
        process = subprocess.Popen(
            [
                "git",
                "log",
                "--numstat",
                "--no-merges",
                "--since=" + start_date,
                "--pretty=",
            ],
            stdout=pipe,
            stderr=pipe,
            text=True,
        )
        stdoutput, stderroutput = process.communicate()
    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)

    # if 'fatal' in stdoutput:
    #
    #   # Handle error case
    #   print("Git problem, exiting...")
    #   exit(1)

    return stdoutput


def get_file_name_from_git_log_line(line):
    parts = line.split()
    if len(parts) >= 3:
        return parts[2]
    else:
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
    output = output + x_axis + "\n"
    for y_val in range(max_yval, -1, -1):
        output = output + "|"
        if points_to_plot[y_val] or outliers_to_plot[y_val] is not None:
            for x_val in range(0, max_xval + 1, 1):
                if points_to_plot[y_val] is not None and x_val in points_to_plot[y_val]:
                    output = output + "X"
                elif (
                    outliers_to_plot[y_val] is not None
                    and x_val in outliers_to_plot[y_val]
                ):
                    output = output + "O"
                else:
                    output = output + " "
        output = output + "\n"
    for x_val in range(0, max_xval + 1, 1):
        output = output + "-"
    output = output + y_axis
    return output


def prepare_plot_data(
    data, x_label="Complexity", y_label="Churn", max_x_output=70, max_y_output=25
):
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
        result = run_analyzer_on_file(file_name)
        # print(result.__dict__)
        if complexity_metric == "CCN":
            complexity[file_name] = result.CCN
        elif complexity_metric == "NLOC":
            complexity[file_name] = result.nloc
        else:
            print("Internal error: Unknown complexity metric specified")
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


def churn_and_complexity_outliers(
    complexity, file_occurence, filtered_file_names, complexity_metric, start_date
):
    result = combine_churn_and_complexity(
        file_occurence, complexity, filtered_file_names
    )
    x_label = "Complexity"
    y_label = "Churn"
    max_x_output = 60
    max_y_output = 20
    points_to_plot, outliers_to_plot, outliers = prepare_plot_data(
        result, x_label, y_label, max_x_output, max_y_output
    )
    print_headline("Churn vs complexity outliers")
    print_subsection(
        "Plot of churn vs complexity for all files since "
        + start_date
        + ". Outliers are marked with O"
    )
    print(
        get_diagram_output(
            points_to_plot,
            outliers_to_plot,
            max_x_output,
            max_y_output,
            "Churn",
            "Complexity(" + str(complexity_metric) + ")",
        )
    )
    print_subsection("Detected outliers (marked with O in the outlier plot)")
    print(get_outliers_output(outliers))


def complexity_outliers(complexity, complexity_metric, start_date, endings=[".py"]):
    top_complexity = 10
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
    left_spacing = 11
    print(f"Complexity Filenames")
    for items in cleaned_ordered_list_with_files[0:top_complexity]:
        print(f"{str(items[1]):11}{items[0]:10}")


def churn_outliers(start_date, file_occurence, endings=[".py"]):
    top_churners = 10
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
    print(f"Changes Filenames")
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
    return {"cpp": [".cpp", ".cxx"], "python": [".py"]}

def get_file_endings_for_languages(languages):
    supported_languages = get_supported_languages()
    language_file_endings = []
    if type(languages) is not list:
        languages = [languages]
    for language in languages:
        if language in supported_languages:
            language_file_endings.extend(supported_languages[language])
    return language_file_endings


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""Analyze a source directory that uses git as version handling system. The source files
        are analyzed for outliers and these outliers can be good candidates for refactoring to increase
        maintainability. The source files are ranked in falling order after churn, complexity, and combined churn 
        and complexity."""
    )
    parser.add_argument(
        "--languages",
        "-l",
        nargs=1,
        help="List the programming languages you want to analyze. if left empty, it'll"
        "search for all languages it knows. 'lizard -l cpp -l java'searches for"
        "C++ and Java code. The available languages are: cpp, java, csharp,"
        "javascript, python, objectivec, ttcn, ruby, php, swift, scala, GDScript,"
        "go, lua, rust, typescript",
        default='python'
    )
    parser.add_argument(
        "--metric",
        "-m",
        nargs=1,
        help="Choose the complexity metric you would like to base the results on. Either cyclomatic"
        "complexity 'CCN' or lines of code without comments 'NLOC'. If not specified, the default is 'CCN.",
        default="CCN",
    )
    parser.add_argument(
        "--span",
        "-s",
        nargs=1,
        help="The number (integer) of months the analysis will look at. Default is 12 months.",
        default=[12],
        type=int,
    )
    parser.add_argument("path", nargs=1)
    args = parser.parse_args()

    if args.span and args.span[0] < 1 or args.span[0] > 100:
        parser.error("Span must be in the range (1,100).")

    ok_metrics = ["NLOC", "CCN"]
    if args.metric not in ok_metrics:
        parser.error(
            str(args.metric)
            + " is not a valid option for complexity metric. Please choose from: "
            + str(ok_metrics)
        )

    # Need to fix :-)
    #if args.languages not in get_supported_languages().keys:
    #    parser.error("Unsupported languages: " + str(args.languages))

    return args


def switch_to_correct_path_and_save_current(path_to_switch):
    startup_path = os.getcwd()
    try:
        os.chdir(os.path.expanduser(path_to_switch[0]))
    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)
    return startup_path


def switch_back_original_directory(path):
    try:
        os.chdir(path)
    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)


def get_start_date(span_in_months):
    today = date.today()
    if type(span_in_months) is list:
        span_in_months = span_in_months[0]
    assert span_in_months >= 0
    start = today + relativedelta(months=-span_in_months)
    return str(start)


def main():

    options = parse_arguments()

    startup_path = switch_to_correct_path_and_save_current(options.path)

    endings = get_file_endings_for_languages(options.languages)
    start_date = get_start_date(options.span)
    (
        computed_complexity,
        file_occurence,
        filtered_file_names,
    ) = get_git_and_complexity_data(endings, options.metric, start_date)

    switch_back_original_directory(startup_path)

    churn_outliers(start_date, file_occurence, endings)

    complexity_outliers(computed_complexity, options.metric, start_date, endings)

    churn_and_complexity_outliers(
        computed_complexity,
        file_occurence,
        filtered_file_names,
        options.metric,
        start_date,
    )

    print_big_separator()


if __name__ == "__main__":
    main()
