PyMotorCAD
==========
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.7-blue
   :target: https://pypi.org/project/ansys-motorcad-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-motorcad-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-motorcad-core/
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/pymotorcad/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pymotorcad
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pymotorcad/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pymotorcad/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


Overview
--------

Ansys Motor-CAD is a dedicated design and analysis tool for electric motors. It enables rapid
and accurate multiphysics design and analysis of electric machines across the full-operating
spectrum.

PyMotorCAD uses a Python JSON-RPC (remote procedure call) interface for
Motor-CAD to launch or connect with a Motor-CAD instance, either locally or
from a remote machine via HTTP. With PyMotorCAD, you can programmatically
create, interact with, and control a Motor-CAD model, with or without using
the Motor-CAD GUI.

Documentation and issues
------------------------
Documentation for the latest stable release of PyMotorCAD is hosted at
`PyMotorCAD documentation <https://motorcad.docs.pyansys.com/version/stable/>`_.

In the upper right corner of the documentation's title bar, there is an option for switching from
viewing the documentation for the latest stable release to viewing the documentation for the
development version or previously released versions.

You can also `view <https://cheatsheets.docs.pyansys.com/pymotorcad_cheat_sheet.png>`_ or
`download <https://cheatsheets.docs.pyansys.com/pymotorcad_cheat_sheet.pdf>`_ the
PyMotorCAD cheat sheet. This one-page reference provides syntax rules and commands
for using PyMotorCAD. 

On the `PyMotorCAD Issues <https://github.com/ansys/pymotorcad/issues>`_ page, you can create
issues to report bugs and request new features. On the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback. 

To reach the project support team, email `pyansys.core@ansys.com <mailto:pyansys.core@ansys.com>`_.

Installation
------------

PyMotorCAD has two installation modes: user and developer.

Install in user mode
^^^^^^^^^^^^^^^^^^^^

Before installing PyMotorCAD in user mode, run this command to ensure
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

**Note:** Before contributing to this project, ensure that you are familiar
with all guidelines in the `PyAnsys Developer's Guide`_.
    
To install in developer mode, complete these steps:

#. Clone the ``pymotorcad`` repository with this command:

    .. code:: bash

        git clone https://github.com/ansys/pymotorcad
        cd pymotorcad

#. Create a fresh-clean Python environment and then activate it with these
   commands:

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
    
        python -m pip install --editable .
    
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

If required, you can call style commands, such as `black`_, `isort`_,
and `flake8`_, or unit testing commands, such as`pytest`_, from the command line.
However, using these commands does not guarantee that your project is being
tested in an isolated environment, which is why tools like `tox`_ exist.


Style checks
------------

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool by running this command:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


Documentation builds
--------------------

To build documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile with a command like this:

.. code:: bash

    make -C doc/ html && your_browser_name doc/html/index.html

However, the recommended way of checking documentation integrity is to use
a ``tox`` command like this:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html


Distribution
------------

If you would like to create either source or wheel files, run the following
commands to install the building requirements and execute the build module:

.. code:: bash

    python -m pip install -U pip
    python -m build
    python -m twine check dist/*


License and acknowledgements
----------------------------

PyMotorCAD is licensed under the MIT license. For more information, see the
`LICENSE <https://github.com/ansys/pymotorcad/raw/main/LICENSE>`_ file.

PyMotorCAD makes no commercial claim over Ansys whatsoever. This library
extends the capability of Ansys Motor-CAD by adding a Python interface
to Motor-CAD without changing the core behaviour or license of the original
software. Using PyMotorCAD for interactive control of Motor-CAD requires
a legally licensed copy of Motor-CAD.

For more information on Motor-CAD, see the `Ansys Motor-CAD <https://www.ansys.com/products/electronics/ansys-motor-cad>`_
page on the Ansys website.

.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's Guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
