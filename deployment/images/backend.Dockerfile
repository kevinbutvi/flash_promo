FROM python:3.9 as requirements-stage

WORKDIR /tmp

RUN pip install poetry
RUN pip install poetry-plugin-export

COPY /backend/pyproject.toml /backend/poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output /tmp/requirements.txt --without-hashes --with dev ;

FROM python:3.11

WORKDIR /app

ARG VERSION
ENV VERSION $VERSION

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./backend /app