import pathlib
import subprocess

from invoke import task

from OpenApiDriver import openapidriver

project_root = pathlib.Path(__file__).parent.resolve().as_posix()


@task
def testserver(context):
    testserver_path = f"{project_root}/tests/server/testserver.py"
    subprocess.run(f"python {testserver_path}", shell=True)


@task
def utests(context):
    cmd = [
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover ",
        f"{project_root}/tests/unittests",
    ]
    subprocess.run(" ".join(cmd), shell=True)


@task
def atests(context):
    cmd = [
        "coverage",
        "run",
        "-m",
        "robot",
        f"--argumentfile={project_root}/tests/rf_cli.args",
        f"--variable=root:{project_root}",
        f"--outputdir={project_root}/tests/logs",
        "--loglevel=TRACE:DEBUG",
        f"{project_root}/tests/suites",
    ]
    subprocess.run(" ".join(cmd), shell=True)


@task(utests, atests)
def tests(context):
    subprocess.run("coverage combine", shell=True)
    subprocess.run("coverage report", shell=True)
    subprocess.run("coverage html", shell=True)


@task
def lint(context):
    subprocess.run(f"mypy {project_root}", shell=True)
    subprocess.run(f"pylint {project_root}/src/OpenApiDriver", shell=True)


@task
def format_code(context):
    subprocess.run(f"black {project_root}", shell=True)
    subprocess.run(f"isort {project_root}", shell=True)
    subprocess.run(f"robotidy {project_root}", shell=True)


@task
def libdoc(context):
    json_file = f"{project_root}/tests/files/petstore_openapi.json"
    source = f"OpenApiDriver::{json_file}"
    target = f"{project_root}/docs/openapidriver.html"
    cmd = [
        "python",
        "-m",
        "robot.libdoc",
        source,
        target,
    ]
    subprocess.run(" ".join(cmd), shell=True)


@task
def libspec(context):
    json_file = f"{project_root}/tests/files/petstore_openapi.json"
    source = f"OpenApiDriver::{json_file}"
    target = f"{project_root}/src/OpenApiDriver/openapidriver.libspec"
    cmd = [
        "python",
        "-m",
        "robot.libdoc",
        source,
        target,
    ]
    subprocess.run(" ".join(cmd), shell=True)


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
    with open(f"{project_root}/docs/README.md", "w", encoding="utf-8") as readme:
        doc_string = openapidriver.__doc__
        readme.write(front_matter)
        readme.write(str(doc_string).replace("\\", "\\\\").replace("\\\\*", "\\*"))


@task(format_code, libdoc, libspec, readme)
def build(context):
    subprocess.run("poetry build", shell=True)


@task(post=[build])
def bump_version(context, rule):
    subprocess.run(f"poetry version {rule}", shell=True)
