FROM python:3.7

WORKDIR /usr/src/app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - \
    && export PATH="/root/.local/bin:$PATH"
ENV PATH "/root/.local/bin:$PATH"

COPY . .

RUN poetry install
