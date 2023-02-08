.. _ref_contributing:

============
Contributing
============

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <dev_guide_contributing_>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with it and all `Coding style <dev_guide_coding_style_>`_ before attempting to
contribute to PyMotorCAD.
 
The following contribution information is specific to PyMotorCAD.


Cloning the PyMotorCAD repository
==========================================

Run this code to clone and install the latest version of PyMotorCAD in development mode:

.. code:: console

    git clone https://github.com/pyansys/pymotorcad
    cd pymotorcad
    pip install --editable ansys-motorcad-core


Posting issues
==============

Use the `PyMotorCAD Issues <PyMotorCAD_issues_>`_
page to submit questions, report bugs, and request new features. When possible,
use these issue templates:

* Bug report template
* Feature request template
* Documentation issue template

If your issue does not fit into one of these categories, create your own issue.

To reach the project support team, email `pyansys.support@ansys.com <pyansys_support_>`_.

Viewing PyMotorCAD documentation
==========================================

Documentation for the latest stable release of PyMotorCAD is hosted at
`PyMotorCAD Documentation <PyMotorCAD_docs_>`_.

Code style
==========

PyMotorCAD follows PEP8 standard as outlined in the `PyAnsys Development Guide
<dev_guide_pyansys_>`_ and implements style checking using
`pre-commit <pre-commit_>`_.

To ensure your code meets minimum code styling standards, run::

    pip install pre-commit
    pre-commit run --all-files

You can also install this as a pre-commit hook by running::

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
.. _pyansys_support: pyansys.support@ansys.com
.. _dev_guide_pyansys: https://dev.docs.pyansys.com/
.. _dev_guide_contributing: https://dev.docs.pyansys.com/dev/how-to/contributing.html
.. _dev_guide_coding_style: https://dev.docs.pyansys.com/dev/coding-style/index.html
.. _PyMotorCAD_issues: https://github.com/pyansys/pymotorcad/issues/
.. _PyMotorCAD_docs: https://motorcad.docs.pyansys.com/