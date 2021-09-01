import pathlib
import subprocess

from invoke import task

from OpenApiDriver import OpenApiDriver

project_root = pathlib.Path(__file__).parent.resolve().as_posix()


@task
def readme(context):
    with open("README.rst", "w", encoding="utf-8") as readme:
        doc_string = OpenApiDriver.__doc__
        readme.write(str(doc_string).replace("\\", "\\\\").replace("\\\\*", "\\*"))


@task
def testserver(context):
    testserver_path = f"{project_root}/tests/server/testserver.py"
    subprocess.run(["python", testserver_path], shell=True)


@task
def tests(context):
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
    subprocess.run(["coverage", "report"], shell=True)
    subprocess.run(["coverage", "html"], shell=True)


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
    subprocess.run(cmd, shell=True)
