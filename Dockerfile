FROM python:3.12.1 as build

WORKDIR /opt/app

RUN pip install gunicorn

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /opt/app/

RUN poetry export --without-hashes --format=requirements.txt > requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/app/requirements.txt

COPY . .

FROM python:3.12.1

COPY --from=build . .