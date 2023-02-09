"""Test script for generating docs for methods."""
import pathlib
import re
import shutil


def generate_method_docs():
    """Add files to document and names for the units here.

    New categories also need adding in MotorCAD_object.rst
    """
    function_categories = [
        "Calculations",
        "FEA Geometry",
        "FEA Results",
        "General",
        "Geometry",
        "Graphs",
        "Internal Scripting",
        "Lab",
        "Materials",
        "Thermal",
        "UI",
        "Utility",
        "Variables",
    ]

    file_names = [
        "rpc_methods_calculations.py",
        "rpc_methods_fea_geometry.py",
        "rpc_methods_fea_results.py",
        "rpc_methods_general.py",
        "rpc_methods_geometry.py",
        "rpc_methods_graphs.py",
        "rpc_methods_internal_scripting.py",
        "rpc_methods_lab.py",
        "rpc_methods_materials.py",
        "rpc_methods_thermal.py",
        "rpc_methods_ui.py",
        "rpc_methods_utility.py",
        "rpc_methods_variables.py",
    ]

    for i in range(len(function_categories)):
        category = function_categories[i]
        file_name = file_names[i]

        current_folder = pathlib.Path(__file__).parent.resolve()
        parent_path = current_folder.parents[2].absolute()

        file_path = str(
            (parent_path / "src" / "ansys" / "motorcad" / "core" / "methods" / file_name).absolute()
        )
        methods_file = open(file_path)

        func_names = []

        for line in methods_file:
            # get function names from file
            if ("    def" in line) and (not "def _" in line):
                # Don't include internal functions
                test = re.search("    def.*\(", line)
                get_name = test.group()

                # strip def and (
                get_name = get_name[7:]
                get_name = get_name[:-1]

                func_names.append(get_name)

        methods_file.close()

        new_file_name = str((current_folder / ("_autogen_" + category + ".rst")).absolute())
        # Copy template file
        shutil.copyfile(str(current_folder / "template.rst_template"), new_file_name)

        # read file
        doc_file = open(new_file_name, "r")
        file_contents = doc_file.read()

        # replace some names/paths
        file_contents = file_contents.replace("Category", category)
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


if __name__ == "__main__":
    generate_method_docs()
