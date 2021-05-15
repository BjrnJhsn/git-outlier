#!/usr/bin/env python3

import lizard
import subprocess
import os

def get_git_log_in_current_directory():
    PIPE = subprocess.PIPE
    branch = "my_branch"

    # git log --numstat --pretty="" --no-merges
    process = subprocess.Popen(
        ["git", "log", "--numstat", "--no-merges", "--pretty="],
        stdout=PIPE,
        stderr=PIPE,
        text=True
    )
    stdoutput, stderroutput = process.communicate()

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


def get_diagram_output(points_to_plot, max_xval, max_yval, x_axis, y_axis):
    output = ""
    output = output + x_axis + "\n"
    for y_val in range(max_yval, -1, -1):
        output = output + "|"
        if points_to_plot[y_val] is not None:
            for x_val in range(0, max_xval + 1, 1):
                if x_val in points_to_plot[y_val]:
                    output = output + "X"
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
    for y_val in range(max_y_output, -1, -1):
        points_to_plot[y_val] = None
    for value in data.values():
        discretized_yval = round(value[y_label] / y_max * max_y_output)
        discretized_xval = round(value[x_label] / x_max * max_x_output)
        if points_to_plot[discretized_yval] is None:
            points_to_plot[discretized_yval] = [discretized_xval]
        else:
            #points_to_plot[discretized_yval] = [
            #    points_to_plot[discretized_yval],
            #    discretized_xval,
            #]
            points_to_plot[discretized_yval].append(
                discretized_xval)

    return points_to_plot

def keep_only_files_with_correct_ending(list, ending):
    output_list = []
    for item in list:
        if type(item) is list or type(item) is tuple:
            filename, file_extension = os.path.splitext(item[0])
        else:
            filename, file_extension = os.path.splitext(item)
        if file_extension == ending:
            output_list.append(item)
    return output_list

def get_complexity_for_file_list(list):
    complexity = {}
    for file_name in list:
        complexity[file_name] = run_analyzer_on_file(file_name).CCN
    return complexity

def run_analyzer_on_file(file_name):
    return lizard.analyze_file(file_name)

def combine_churn_and_complexity(file_occurence, complexity, filtered_file_names):
    result = {}
    for file_name in filtered_file_names:
        if file_name in file_occurence and file_name in complexity:
            result[file_name] = {"Churn": file_occurence[file_name], "Complexity": complexity[file_name]}
    return result

def main():
    startup_path = os.getcwd()
    os.chdir(os.path.expanduser("~/sources/github/conan"))

    #i = lizard.analyze_file("outlier.py")
    #print(i.__dict__)
    #for function in i.__dict__["function_list"]:
    #    print(function.__dict__)

    # git log --numstat --pretty="" --no-merges > conan_git_log_output.txt

    f = open("conan_git_log_output.txt", "r")
    for line in f:
        print(line)

    f.close()
    f = open("conan_git_log_output.txt", "r")
    all_of_it = get_git_log_in_current_directory() # f.read()
    file_occurence, file_names = get_file_occurences_from_git_log(all_of_it)

    filtered_file_names = keep_only_files_with_correct_ending(file_names,".py")
    complexity = get_complexity_for_file_list(filtered_file_names[0:30])

    result = combine_churn_and_complexity(file_occurence, complexity, filtered_file_names)


    print(ordered_list_with_files(file_occurence))

    top_churners = 10
    print("The top " + str(top_churners) + " files with churn in descending order:")
    cleaned_ordered_list_with_files = keep_only_files_with_correct_ending(ordered_list_with_files(file_occurence),".py")
    print(f"Changes Filenames")
    for items in  cleaned_ordered_list_with_files[0:top_churners]:
        print(f"{str(items[1]):8}{items[0]:10}")

    data = {
        "filename": {"Churn": 1, "Complexity": 20},
        "filename2": {"Churn": 5, "Complexity": 20},
        "yada": {"Churn": 20, "Complexity": 1},
        "yada2": {"Churn": 15, "Complexity": 15},
        "yada5": {"Churn": 15, "Complexity": 15},
        "yada20": {"Churn": 1, "Complexity": 1},
    }
    print(result)
    print(data["filename"]["Churn"])

    x_label = "Complexity"
    y_label = "Churn"
    max_x_output = 70
    max_y_output = 30
    points_to_plot = prepare_plot_data(
        result, x_label, y_label, max_x_output, max_y_output
    )

    print(points_to_plot)
    print(
        "\n\n***************************************************\n\nChurn vs Complexity diagram \n"
    )

    print(
        get_diagram_output(
            points_to_plot, max_x_output, max_y_output, "Churn", "Complexity"
        )
    )
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/

    os.chdir(startup_path)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()
