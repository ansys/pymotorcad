"""Test script for generating docs for methods."""
import ast
from dataclasses import dataclass
from enum import Enum
import pathlib
import shutil

# FOR DEVELOPERS :
#
# If you are adding a new documentation category, follow these steps :
#  1. Add a new entry to the `doc_categories` list with the appropriate values using a
#     _DocCategory obj.
#  2. Add to doc/source/methods/MotorCAD_object.rst file
#  3. Run this script to generate the documentation files.
#
# If you are adding a Unit category specifically, the rpc_methods_core python file will
# need to be updated. A class attribute will need to be added and set to be an alias of
# the rpc class, this attribute will share the name as the runtime instance used. This is
# used by the doc gen to find the methods but has no functional impact when using the api.
# e.g. for messageconfig, the runtime instance is referenced via MotorCad.messageconfig.<method>
#      and is set to _RpcMessageConfig(mc_connection). Along with this there needs to be a
#      _RpcMethodsCore.messageconfig attribute set to _RpcMessageConfig.
# See messageconfig in rpc_methods_core for an example.
#
# If you are adding a new documentation category generation type, follow the steps:
#  1. Add a new entry to the _DocCategoryGenType enumeration with the appropriate value.
#  2. Update _DocCategory with any new fields required for the new generation type.
#  3. Create any templates needed in _templates/templates/
#  4. Update the replace_dict passed to _doctemplate_find_and_replace if needed for new
#     _DocCategory fields.
#  5. Update the generate_method_docs function to handle the new generation type if necessary.
#  6. Test the documentation generation to ensure it works correctly with the new generation
#     type.
#  7. Update any comments related to the new documentation category or generation type. Also
#     note the README in _templates/


class _DocCategoryGenType(str, Enum):
    """Provides an enumeration for doc category generation types."""

    default = "default"  # MotorCAD.<method>
    unit = "unit"  # MotorCAD.[unit].<method>


@dataclass
class _DocCategory:
    category_type: _DocCategoryGenType
    category_name: str
    file_name: str
    unit_name: str | None = None  # Only required for unit type categories


def _doctemplate_find_and_replace(file_path: str, replace_dict: dict):
    with open(file_path, "r") as doctemplate_file:
        file_content = doctemplate_file.read()

    for key, value in replace_dict.items():
        file_content = file_content.replace(key, value)

    with open(file_path, "w") as doctemplate_file:
        doctemplate_file.write(file_content)


def generate_method_docs():
    """Add files to document and names for the units here.

    New categories also need adding in MotorCAD_object.rst
    """
    # Docs can be generated in different ways depending on the category type :
    # default   :   MotorCAD.<method>
    # unit      :   MotorCAD.[unit].<method>
    #
    # See _DocCategoryGenType for structure
    #
    doc_categories = [
        _DocCategory(_DocCategoryGenType.default, "Calculations", "rpc_methods_calculations.py"),
        _DocCategory(_DocCategoryGenType.default, "FEA Geometry", "rpc_methods_fea_geometry.py"),
        _DocCategory(_DocCategoryGenType.default, "General", "rpc_methods_general.py"),
        _DocCategory(_DocCategoryGenType.default, "Geometry", "rpc_methods_geometry.py"),
        _DocCategory(_DocCategoryGenType.default, "Adaptive Geometry", "adaptive_geometry.py"),
        _DocCategory(_DocCategoryGenType.default, "Graphs", "rpc_methods_graphs.py"),
        _DocCategory(
            _DocCategoryGenType.default, "Internal Scripting", "rpc_methods_internal_scripting.py"
        ),
        _DocCategory(_DocCategoryGenType.default, "Lab", "rpc_methods_lab.py"),
        _DocCategory(_DocCategoryGenType.default, "Materials", "rpc_methods_materials.py"),
        _DocCategory(_DocCategoryGenType.default, "Thermal", "rpc_methods_thermal.py"),
        _DocCategory(_DocCategoryGenType.default, "UI", "rpc_methods_ui.py"),
        _DocCategory(_DocCategoryGenType.default, "Utility", "rpc_methods_utility.py"),
        _DocCategory(_DocCategoryGenType.default, "Variables", "rpc_methods_variables.py"),
        _DocCategory(
            _DocCategoryGenType.unit, "Message Config", "rpc_message_config.py", "messageconfig"
        ),
    ]

    # Get file/dir paths , see README for template info
    #
    # current_folder      : .../pymotorcad/doc/source/methods/
    # docsource_folder    : .../pymotorcad/doc/source/
    # _templates_folder   : .../pymotorcad/doc/source/_templates/templates
    # templates_folder    : .../pymotorcad/doc/source/_templates/generated
    # parent_path         : .../pymotorcad/
    #
    current_folder = pathlib.Path(__file__).parent.resolve()
    docsource_folder = current_folder.parent.resolve()
    _templates_folder = docsource_folder / "_templates" / "templates"
    templates_folder = docsource_folder / "_templates" / "generated"
    parent_path = current_folder.parents[2].absolute()

    # Ensure template folders exist for templates to be generated into
    _templates_folder.mkdir(exist_ok=True)
    templates_folder.mkdir(exist_ok=True)

    # Generate documentation for each category
    for i, category in enumerate(doc_categories):
        # rpc methods python file path
        file_path = str(
            (
                parent_path / "src" / "ansys" / "motorcad" / "core" / "methods" / category.file_name
            ).absolute()
        )

        # Get functions
        func_names = []
        with open(file_path, "r") as methods_file:
            # filename arg only used for errors
            tree = ast.parse(methods_file.read(), filename=file_path)

        # for node in ast.walk(tree):
        #     if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
        #         func_names.append(node.name)
        #
        # If below isn't finding all the rpc methods try switching to the above for loop instead.
        # It is less strict, allowing methods outside of the _Rpc class to be included.
        # I used this one as a bit safer, but it does have the potential to be more restrictive.
        #
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name.startswith("_Rpc"):
                func_names = [
                    method.name
                    for method in node.body
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not method.name.startswith("_")
                ]
                break
        else:
            raise ValueError(f"No class found in {file_path}")

        func_names = sorted(func_names)  # sorted so more readable in the docs

        # Create method template for the category if it of the unit type
        if category.category_type == _DocCategoryGenType.unit:
            unit_method_template = str(
                (_templates_folder / "autosummary" / "unit_method.rst_template").absolute()
            )
            new_unit_method_template_file = str(
                (templates_folder / f"method_template_{category.category_name}.rst").absolute()
            )

            shutil.copyfile(unit_method_template, new_unit_method_template_file)

            _doctemplate_find_and_replace(
                new_unit_method_template_file,
                {
                    "[Category]": category.category_name,
                    "[unitname]": category.unit_name,
                },
            )

        # Create new documentation autogen file based on template
        category_template = str(
            (
                _templates_folder
                / "autogen"
                / f"{category.category_type.value}_category.rst_template"
            ).absolute()
        )
        new_category_template_file = str(
            (current_folder / ("_autogen_" + category.category_name + ".rst")).absolute()
        )

        shutil.copyfile(category_template, new_category_template_file)

        # Prepare the dictionary for replacing placeholders in the new category autogen file
        #  note: currently optional feilds in _DocCategory default to None, it throws an error if
        #        you pass None to the replace_dict. So it may be better for it to default to None
        #        a "" (empty string) instead of None to avoid many if statements to emit un-used
        #        fields when in a category type not supporting those fields.
        replace_dict = {"[Category]": category.category_name}
        if category.category_type == _DocCategoryGenType.unit:
            replace_dict["[unitname]"] = category.unit_name

        _doctemplate_find_and_replace(new_category_template_file, replace_dict)

        # append method names to end of category documentation file
        with open(new_category_template_file, "a") as doc_file:
            for func_name in func_names:
                doc_file.write("   " + func_name + "\n")


if __name__ == "__main__":
    generate_method_docs()
