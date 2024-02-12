FROM python:3.12-slim-bookworm

RUN pip install --upgrade pip

# poetry install into the default Python interpreter since we're in a container
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project false

# Copy the pyproject.toml and poetry.lock file to be able to install dependencies using poetry
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

EXPOSE 8888
ENTRYPOINT /bin/sh
