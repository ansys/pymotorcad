.. _ref_contributing:

==========
Contribute
==========

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <dev_guide_contributing_>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyMotorCAD.
 
The following contribution information is specific to PyMotorCAD.

Clone the repository
====================

Run this code to clone and install the latest version of PyMotorCAD in development mode:

.. code:: console

    git clone https://github.com/ansys/pymotorcad
    cd pymotorcad
    pip install --editable .


Post issues
===========

Use the `PyMotorCAD Issues <PyMotorCAD_issues_>`_
page to submit questions, report bugs, and request new features. When possible,
use these issue templates:

* Bug report template
* Feature request template
* Documentation issue template

If your issue does not fit into one of these categories, create your own issue.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

View PyMotorCAD documentation
=============================

Documentation for the latest stable release of PyMotorCAD is hosted at
`PyMotorCAD Documentation <PyMotorCAD_docs_>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

Adhere to code style
====================

PyMotorCAD is compliant with the `PyAnsys code style
<https://dev.docs.pyansys.com/coding-style/index.html>`_. it
uses the tool `pre-commit <pre-commit_>`_ to enforce the code style.
You can install and activate this tool with this code::

    pip install pre-commit
    pre-commit run --all-files

You can also install this tool as a pre-commit hook by running this command::

    pre-commit install

This way, it's not possible for you to push code that fails the style checks. For example::

    $ pre-commit install
    $ git commit -am "Add a new feature."
    black....................................................................Passed
    blacken-docs.............................................................Passed
    isort....................................................................Passed
    flake8...................................................................Passed
    codespell................................................................Passed
    pydocstyle...............................................................Passed
    check for merge conflicts................................................Passed
    debug statements (python)................................................Passed
    Validate GitHub Workflows................................................Passed


.. LINKS AND REFERENCES
.. _pre-commit: https://pre-commit.com/
.. _pyansys_support: pyansys.core@ansys.com
.. _dev_guide_pyansys: https://dev.docs.pyansys.com/
.. _dev_guide_contributing: https://dev.docs.pyansys.com/dev/how-to/contributing.html
.. _dev_guide_coding_style: https://dev.docs.pyansys.com/dev/coding-style/index.html
.. _PyMotorCAD_issues: https://github.com/ansys/pymotorcad/issues/
.. _PyMotorCAD_docs: https://motorcad.docs.pyansys.com/