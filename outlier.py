#!/usr/bin/env python3

import lizard


def get_file_name_from_git_log_line(line):
    parts = line.split()
    if len(parts) >= 3:
        return parts[2]
    else:
        return ""


def get_file_occurences_from_git_log(log):
    file_occurences = {}
    for line in log.splitlines():
        file_name = get_file_name_from_git_log_line(line)
        if file_name in file_occurences:
            file_occurences[file_name] += 1
        else:
            file_occurences[file_name] = 1
    return file_occurences


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
            points_to_plot[discretized_yval] = [
                points_to_plot[discretized_yval],
                discretized_xval,
            ]
    return points_to_plot


def main():
    i = lizard.analyze_file("outlier.py")
    print(i.__dict__)

    f = open("conan_git_log_output.txt", "r")
    for line in f:
        print(line)

    f.close()
    f = open("conan_git_log_output.txt", "r")
    all_of_it = f.read()
    file_occurence = get_file_occurences_from_git_log(all_of_it)
    print(ordered_list_with_files(file_occurence))

    top_churners = 10
    print("The top " + str(top_churners) + " files with churn in descending order:")
    ordered_list = ordered_list_with_files(file_occurence)
    print(f"Changes Filenames")
    for items in ordered_list_with_files(file_occurence)[0:top_churners]:
        print(f"{str(items[1]):8}{items[0]:10}")

    data = {
        "filename": {"Churn": 1, "Complexity": 20},
        "filename2": {"Churn": 5, "Complexity": 20},
        "yada": {"Churn": 20, "Complexity": 1},
        "yada2": {"Churn": 15, "Complexity": 15},
        "yada5": {"Churn": 15, "Complexity": 15},
        "yada20": {"Churn": 1, "Complexity": 1},
    }
    print(data)
    print(data["filename"]["Churn"])

    x_label = "Complexity"
    y_label = "Churn"
    max_x_output = 70
    max_y_output = 25
    points_to_plot = prepare_plot_data(
        data, x_label, y_label, max_x_output, max_y_output
    )

    print(points_to_plot)
    print(
        "\n\n***************************************************\n\nChurn vs Complexity diagram \n"
    )

    print(get_diagram_output(points_to_plot, max_x_output, max_y_output, "Churn", "Complexity"))
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()


# git log --numstat --pretty="" --no-merges > conan_git_log_output.txt
