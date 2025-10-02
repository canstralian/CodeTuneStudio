# syntax=docker/dockerfile:1.4

# Use a build ARG to specify the Python version (default to 3.10)
ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]