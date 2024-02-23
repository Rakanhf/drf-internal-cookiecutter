# Use the specified slim version of Python
FROM python:3.10.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry using the new approach
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory in the container
WORKDIR /app

# Copy only pyproject.toml and poetry.lock* (if exists) to cache them in docker layer
COPY ./pyproject.toml ./poetry.lock* /app/

# Disable virtualenv creation by Poetry and install dependencies
# No need to explicitly source any env file
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

# Copying the project files
COPY . /app

# Expose the port the app runs on
EXPOSE 8000
