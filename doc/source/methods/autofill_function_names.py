"""Test script for generating docs for methods."""
import pathlib
import re
import shutil

function_categories = ["general", "materials"]
file_names = ["rpc_methods_general.py", "rpc_methods_materials.py"]

for i in range(len(function_categories)):
    category = function_categories[i]
    file_name = file_names[i]

    current_folder = str(pathlib.Path(__file__).parent.resolve())

    file_path = current_folder + r"\..\..\..\src\ansys\motorcad\core\methods\\" + file_name
    methods_file = open(file_path)

    func_names = []

    for line in methods_file:
        # get function names from file
        if ("    def" in line) and (not "__init__" in line):
            test = re.search("    def.*\(", line)
            get_name = test.group()

            # strip def and (
            get_name = get_name[7:]
            get_name = get_name[:-1]

            func_names.append(get_name)

    methods_file.close()

    new_file_name = current_folder + r"\_autogen_" + category + ".rst"
    # Copy template file
    shutil.copyfile(current_folder + r"\template.rst_template", new_file_name)

    # read file
    doc_file = open(new_file_name, "r")
    file_contents = doc_file.read()

    # replace some names/paths
    file_contents = file_contents.replace("Category", category + " functions")
    file_contents = file_contents.replace("_autosummary_path", "_autosummary_" + category)
    doc_file.close()

    # write title to file
    doc_file = open(new_file_name, "w")
    doc_file.write(file_contents)
    doc_file.close()

    # append to end of file
    doc_file = open(new_file_name, "a")

    for func_name in func_names:
        doc_file.write("   " + func_name + "\n")
