# pylint: disable=missing-function-docstring
import pathlib
import subprocess

from invoke import task

from OpenApiDriver import openapidriver

ROOT = pathlib.Path(__file__).parent.resolve().as_posix()


@task
def testserver(context):
    testserver_path = f"{ROOT}/tests/server/testserver.py"
    subprocess.run(f"python {testserver_path}", shell=True, check=False)


@task
def utests(context):
    cmd = [
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover ",
        f"{ROOT}/tests/unittests",
    ]
    subprocess.run(" ".join(cmd), shell=True, check=False)


@task
def atests(context):
    cmd = [
        "coverage",
        "run",
        "-m",
        "robot",
        f"--argumentfile={ROOT}/tests/rf_cli.args",
        f"--variable=root:{ROOT}",
        f"--outputdir={ROOT}/tests/logs",
        "--loglevel=TRACE:DEBUG",
        f"{ROOT}/tests/suites",
    ]
    subprocess.run(" ".join(cmd), shell=True, check=False)


@task(utests, atests)
def tests(context):
    subprocess.run("coverage combine", shell=True, check=False)
    subprocess.run("coverage report", shell=True, check=False)
    subprocess.run("coverage html", shell=True, check=False)


@task
def lint(context):
    subprocess.run(f"mypy {ROOT}", shell=True, check=False)
    subprocess.run(f"pylint {ROOT}/src/OpenApiDriver", shell=True, check=False)


@task
def format_code(context):
    subprocess.run(f"black {ROOT}", shell=True, check=False)
    subprocess.run(f"isort {ROOT}", shell=True, check=False)
    subprocess.run(f"robotidy {ROOT}", shell=True, check=False)


@task
def libdoc(context):
    json_file = f"{ROOT}/tests/files/petstore_openapi.json"
    source = f"OpenApiDriver.openapidriver.DocumentationGenerator::{json_file}"
    # FIXME: replace DocumentationGenerator with OpenApiDriver in libspec
    target = f"{ROOT}/docs/openapidriver.html"
    cmd = [
        "python",
        "-m",
        "robot.libdoc",
        source,
        target,
    ]
    subprocess.run(" ".join(cmd), shell=True, check=False)


@task
def libspec(context):
    json_file = f"{ROOT}/tests/files/petstore_openapi.json"
    source = f"OpenApiDriver.openapidriver.DocumentationGenerator::{json_file}"
    # FIXME: replace DocumentationGenerator with OpenApiDriver in libspec
    # and fix library version and docstring
    target = f"{ROOT}/src/OpenApiDriver/openapidriver.libspec"
    cmd = [
        "python",
        "-m",
        "robot.libdoc",
        source,
        target,
    ]
    subprocess.run(" ".join(cmd), shell=True, check=False)


@task
def readme(context):
    #     front_matter = (
    # r"""---
    # ![[Unit-tests](https://img.shields.io/github/workflow/status/MarketSquare/robotframework-openapidriver/Unit%20tests/main)](https://github.com/MarketSquare/robotframework-openapidriver/actions?query=workflow%3A%22Unit+tests%22 "GitHub Workflow Unit Tests Status")
    # ![Codecov](https://img.shields.io/codecov/c/github/MarketSquare/robotframework-openapidriver/main "Code coverage on master branch")
    # ![PyPI](https://img.shields.io/pypi/v/robotframework-openapidriver?label=version "PyPI package version")
    # ![Python versions](https://img.shields.io/pypi/pyversions/robotframework-openapidriver "Supported Python versions")
    # ![Licence](https://img.shields.io/pypi/l/robotframework-openapidriver "PyPI - License")
    # ---
    # """)
    front_matter = """---\n---\n"""
    with open(f"{ROOT}/docs/README.md", "w", encoding="utf-8") as readme:
        doc_string = openapidriver.__doc__
        readme.write(front_matter)
        readme.write(str(doc_string).replace("\\", "\\\\").replace("\\\\*", "\\*"))


@task(format_code, libdoc, libspec, readme)
def build(context):
    subprocess.run("poetry build", shell=True, check=False)


@task(post=[build])
def bump_version(context, rule):
    subprocess.run(f"poetry version {rule}", shell=True, check=False)
