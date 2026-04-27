FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY . .

RUN pip install -e .
RUN apt-get update && apt-get install -y cron
COPY crontab /etc/cron.d/pipeline
RUN chmod 0644 /etc/cron.d/pipeline
RUN crontab /etc/cron.d/pipeline

CMD ["bash", "start.sh"]