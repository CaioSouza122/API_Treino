FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for layer caching
COPY requirements.txt ./
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Copy the whole project (excluding .gitignore etc.)
COPY . .

# Ensure .venv not copied (optional) – we rely on container venv
ENV PATH="/venv/bin:$PATH"

# Expose Flask default port
EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "App:app"]
