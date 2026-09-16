"""Test script for generating docs for methods."""
import pathlib
import re
import shutil


def generate_method_docs():
    """Add files to document and names for the units here.

    New categories also need adding in MotorCAD_object.rst
    """
    category_configs = [
        {
            "category": "Calculations",
            "file_name": "rpc_methods_calculations.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "FEA Geometry",
            "file_name": "rpc_methods_fea_geometry.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "General",
            "file_name": "rpc_methods_general.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Geometry",
            "file_name": "rpc_methods_geometry.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Adaptive Geometry",
            "file_name": "adaptive_geometry.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Graphs",
            "file_name": "rpc_methods_graphs.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Internal Scripting",
            "file_name": "rpc_methods_internal_scripting.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Lab",
            "file_name": "rpc_methods_lab.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Materials",
            "file_name": "rpc_methods_materials.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Message Config",
            "file_name": "rpc_message_config.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD.messageconfig",
        },
        {
            "category": "Thermal",
            "file_name": "rpc_methods_thermal.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "UI",
            "file_name": "rpc_methods_ui.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Utility",
            "file_name": "rpc_methods_utility.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
        {
            "category": "Variables",
            "file_name": "rpc_methods_variables.py",
            "currentmodule": "ansys.motorcad.core.motorcad_methods.MotorCAD",
        },
    ]

    for config in category_configs:
        category = config["category"]
        file_name = config["file_name"]
        currentmodule = config["currentmodule"]

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
        file_contents = file_contents.replace("CurrentmodulePath", currentmodule)
        file_contents = file_contents.replace("_autosummary_path", "_autosummary_" + category)
        doc_file.close()

        # write title to file
        doc_file = open(new_file_name, "w")
        doc_file.write(file_contents)
        doc_file.close()

        # append to end of file
        doc_file = open(new_file_name, "a")

        func_names = sorted(func_names)

        for func_name in func_names:
            doc_file.write("   " + func_name + "\n")


if __name__ == "__main__":
    generate_method_docs()
