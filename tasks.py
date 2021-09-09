import pathlib
import subprocess

from invoke import task

from OpenApiDriver import openapidriver

project_root = pathlib.Path(__file__).parent.resolve().as_posix()


@task
def testserver(context):
    testserver_path = f"{project_root}/tests/server/testserver.py"
    subprocess.run(["python", testserver_path])


@task
def tests(context):
    cmd = [
        "coverage",
        "run",
        "-m",
        "unittest",
        f"{project_root}/tests/unittests/test_openapidriver.py",
    ]
    subprocess.run(cmd)
    cmd = [
        "coverage",
        "run",
        "-m",
        "robot",
        f"--argumentfile={project_root}/tests/rf_cli.args",
        f"--variable=root:{project_root}",
        f"--outputdir={project_root}/tests/logs",
        f"{project_root}/tests/suites",
    ]
    subprocess.run(cmd, shell=True)
    subprocess.run(["coverage", "combine"])
    subprocess.run(["coverage", "report"])
    subprocess.run(["coverage", "html"])


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
    subprocess.run(cmd)


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
    subprocess.run(cmd)


@task
def readme(context):
    with open("README.md", "w", encoding="utf-8") as readme:
        doc_string = openapidriver.__doc__
        readme.write(str(doc_string).replace("\\", "\\\\").replace("\\\\*", "\\*"))


@task(libdoc, libspec, readme)
def build(context):
    subprocess.run(["poetry", "build"])


@task(post=[build])
def bump_version(context, rule):
    subprocess.run(["poetry", "version", rule])
