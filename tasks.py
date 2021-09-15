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
def tests(context):
    cmd = [
        "coverage",
        "run",
        "-m",
        "unittest",
        "discover ",
        f"{project_root}/tests/unittests",
    ]
    subprocess.run(" ".join(cmd), shell=True)
    cmd = [
        "coverage",
        "run",
        "-m",
        "robot",
        f"--argumentfile={project_root}/tests/rf_cli.args",
        f"--variable=root:{project_root}",
        f"--outputdir={project_root}/tests/logs",
        f"--loglevel=TRACE:DEBUG",
        f"{project_root}/tests/suites",
    ]
    subprocess.run(" ".join(cmd), shell=True)
    subprocess.run("coverage combine", shell=True)
    subprocess.run("coverage report", shell=True)
    subprocess.run("coverage html", shell=True)


@task
def libdoc(context):
    json_file = f"{project_root}/tests/files/petstore_openapi.json"
    source = f"{project_root}/src/OpenApiDriver/openapidriver.py::{json_file}"
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
    source = f"{project_root}/src/OpenApiDriver/openapidriver.py::{json_file}"
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
    with open(f"{project_root}/docs/README.md", "w", encoding="utf-8") as readme:
        doc_string = openapidriver.__doc__
        readme.write(str(doc_string).replace("\\", "\\\\").replace("\\\\*", "\\*"))


@task(libdoc, libspec, readme)
def build(context):
    subprocess.run("poetry build", shell=True)


@task(post=[build])
def bump_version(context, rule):
    subprocess.run(f"poetry version {rule}", shell=True)
