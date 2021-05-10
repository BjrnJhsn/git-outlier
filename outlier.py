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


# git log --numstat --pretty="" --no-merges > conan_git_log_output.txt


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
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

    maxChurn = 0
    maxComplexity = 0
    for value in data.values():
        if value["Churn"] > maxChurn:
            maxChurn = value["Churn"]
        if value["Complexity"] > maxComplexity:
            maxComplexity = value["Complexity"]
    max_yval = 25
    discretization_yval = 1 / max_yval
    max_xval = 70
    discretization_xval = 1 / max_xval

    points_to_plot = dict()
    for y_val in range(max_yval, -1, -1):
        points_to_plot[y_val] = None

    for value in data.values():
        discreatized_yval = round(value["Churn"] / maxChurn * max_yval)
        discreatized_xval = round(value["Complexity"] / maxComplexity * max_xval)
        if points_to_plot[discreatized_yval] is None:
            points_to_plot[discreatized_yval] = [discreatized_xval]
        else:
            points_to_plot[discreatized_yval] = [
                points_to_plot[discreatized_yval],
                discreatized_xval,
            ]
    print(points_to_plot)
    print(
        "\n\n***************************************************\n\nChurn vs Complexity diagram \n"
    )
    print("Churn")
    for y_val in range(max_yval, -1, -1):
        print("|", end="")
        if points_to_plot[y_val] is not None:
            for x_val in range(0, max_xval + 1, 1):
                if x_val in points_to_plot[y_val]:
                    print("X", end="")
                else:
                    print(" ", end="")
        print("")

    for x_val in range(0, max_xval + 1, 1):
        print("-", end="")
    print(" Complexity")
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
