FROM python:3.12-alpine

RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --without=dev
COPY . /app
CMD poetry run python main.py $SLAVIC_ORACLE_TOKEN
