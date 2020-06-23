import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


runtime = set([
    "pyyaml",
])

develop = set([
    "coverage",
    "flake8",
    "pytest",
    "pytest-cov",
    "setuptools",
    "twine",
    "wheel",
])

docs = set([
    "Sphinx",
    "sphinx_rtd_theme",
])

optional = set([
    "pandas",
    "IPython"
])


if __name__ == "__main__":
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = f.read()

    setup(
        name="squerly",
        version="0.1.1",
        description="Squerly takes the tedium out of nested dicts and lists.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/csams/squerly",
        author="Christopher Sams",
        author_email="csams@gmail.com",
        packages=find_packages(),
        install_requires=list(runtime),
        package_data={"": ["LICENSE"]},
        license="Apache 2.0",
        extras_require={
            "develop": list(develop | docs | optional),
            "docs": list(docs),
            "optional": list(optional),
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8"
        ],
        include_package_data=True
    )
