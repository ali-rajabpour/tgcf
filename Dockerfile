# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app
ENV VENV_PATH="/venv"
ENV PATH="$VENV_PATH/bin:$PATH"

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv $VENV_PATH

# Install poetry
RUN /venv/bin/pip install --upgrade pip wheel setuptools poetry

# Copy only requirements first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN /venv/bin/poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application
COPY . .

# Build the package
RUN /venv/bin/poetry build

# Install the package
RUN /venv/bin/pip install dist/*.whl

# Runtime stage
FROM python:3.10-slim

WORKDIR /app
ENV VENV_PATH="/venv"
ENV PATH="$VENV_PATH/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder $VENV_PATH $VENV_PATH

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8501

# Using JSON array format for proper signal handling
CMD ["tgcf-web"]