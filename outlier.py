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

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
