FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY . .

RUN pip install -e .

CMD ["bash", "start.sh"]