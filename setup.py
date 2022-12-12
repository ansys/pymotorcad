"""Project installation script."""

from setuptools import find_namespace_packages, setup

setup(
    name="ansys-motorcad-core",
    version="0.1.dev1",
    url="https://github.com/pyansys/pymotorcad",
    author="ANSYS, Inc.",
    author_email="pyansys.support@ansys.com",
    maintainer="PyAnsys developers",
    maintainer_email="pyansys.maintainers@ansys.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    license_file="LICENSE",
    description="A python rpc-json interface for motor-cad",
    long_description=open("README.rst").read(),
    install_requires=[
        "importlib-metadata >=4.12.0",
        "psutil >= 5.9.0",
        "requests >= 2.27.1",
        "packaging >= 21.3",
    ],
    python_requires=">=3.7",
    packages=find_namespace_packages(where="src", include="ansys*"),
    package_dir={"": "src"},
)
