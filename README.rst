PyMotorCAD
==========
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.7-blue
   :target: https://pypi.org/project/pymotorcad-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/pymotorcad-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pymotorcad-core
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/pyansys/pymotorcad/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/pyansys/pymotorcad
   :alt: Codecov

.. |GH-CI| image:: https://github.com/pyansys/pymotorcad/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pymotorcad/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


This Python package provides the core Python RPC-JSON interface for Motor-CAD.

Install the package
-------------------

PyMotorCAD has two installation modes: user and developer.

Install in user mode
^^^^^^^^^^^^^^^^^^^^

Before installing PyMotorCAD in user mode, run this command to esure
that you have the latest version of `pip`_:

.. code:: bash

    python -m pip install -U pip

Then, run this command to install PyMotorCAD:

.. code:: bash

    python -m pip install ansys-motorcad-core

Install in developer mode
^^^^^^^^^^^^^^^^^^^^^^^^^

Installing PyMotorCAD in developer mode allows
you to modify the source and enhance it.

.. note::

    Before contributing to this project, ensure that you are familiar
    with all guidelines in the `PyAnsys Developer's Guide`_.
    
To install in developer mode, complete these steps:

#. Clone the ``pymotorcad`` repository with this command:

    .. code:: bash

        git clone https://github.com/pyansys/pymotorcad

#. Create a fresh-clean Python environment and activate it with
   these commands:

    .. code:: bash

        # Create a virtual environment
        python -m venv .venv

        # Activate it in a POSIX system
        source .venv/bin/activate

        # Activate it in Windows CMD environment
        .venv\Scripts\activate.bat

        # Activate it in Windows Powershell
        .venv\Scripts\Activate.ps1

#. Ensure that you have the latest required build system and
   documentation, testing, and CI tools with this command:

    .. code:: bash

        python -m pip install -U pip tox

#. Install the project in editable mode with this command:

    .. code:: bash
    
        python -m pip install --editable ansys-motorcad-core
    
#. Verify your development installation with this command:

    .. code:: bash
        
        tox

Testing
-------

This project takes advantage of `tox`_. This tool allows you to automate common
development tasks (similar to Makefile), but it is oriented towards Python
development. 

While Makefile has rules, ``tox`` has environments. In fact, ``tox`` creates
its own virtual environment to guarantee the project's integrity by isolating
anything being tested.

``tox`` commands
^^^^^^^^^^^^^^^^

Here are commands for running various checks in the  ``tox`` environment:

- **tox -e style**: Checks for coding style quality.
- **tox -e py**: Checks for unit tests.
- **tox -e py-coverage**: Checks for unit testing and code coverage.
- **tox -e doc**: Checks for the documentation-building process.

Raw testing
^^^^^^^^^^^

If required, you can call style commands, incuding `black`_, `isort`_,
and `flake8`_ or unit testing commands like`pytest`_ from the command line.
However, using these commands does not guarantee that your project is being
tested in an isolated environment, which is why tools like `tox`_ exist.


Style checks
------------

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool by running this command:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


Documentation
-------------

To build documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile with a command like this:

.. code:: bash

    make -C doc/ html && your_browser_name doc/html/index.html

However, the recommended way of checking documentation integrity is to use
this ``tox`` command:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html


For more information, see the `Documentation <https://motorcad.docs.pyansys.com/>`_
page in the PyMotorCAD documentation.

Distribution
------------

If you would like to create either source or wheel files, run the following
code to install the building requirements and execute the build module:

.. code:: bash

    python -m pip install -U pip
    python -m build
    python -m twine check dist/*

.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
