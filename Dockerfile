FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ocaml \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["python3", "-u", "web_app.py"]