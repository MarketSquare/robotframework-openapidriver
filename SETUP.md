## Preparing your system to run Python-based tests

This repo uses [poetry](https://python-poetry.org/) for Python environment isolation and package management. Before poetry can be installed, Python must be installed. The minimum version to be
installed can be found in the `pyproject.toml` file (e.g. python = "^3.8"). The appropriate
download for your OS can be found [here](https://www.python.org/downloads/).

After installing Python, poetry can be installed. For OSX/ Linux / bashonwindows the command is:

```curl
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
```

For Windows the PowerShell command is:

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -UseBasicParsing).Content | python -
```

To ensure the install succeeded, you can open a new shell and run
```
poetry --version
```
> Windows users: if this does not work, see https://python-poetry.org/docs/master/#windows-powershell-install-instructions

Next poetry can be configured to create virtual environments for repos within the repo
(this makes it easy to locate the .venv for a given repo if you want to clean / delete it):
```
poetry config virtualenvs.in-project true
```
Now that poetry is set up, the project's Python dependencies can be installed:
```
poetry install --remove-untracked
```

## Running tests using poetry and invoke

In addition to poetry, the [invoke](http://www.pyinvoke.org/index.html) package is used to
create tasks that can be ran on all platforms in the same manner. These tasks are defined in
the `tasks.py` file in the root of the repo. To see which tasks are available, run
```
poetry run inv --list
```
> If the `.venv` is activated in the current shell, this can be shortened to `inv --list`


Further information / documentation of the tasks (if available) can be shown using
```
poetry run inv --help <task_name>
```
