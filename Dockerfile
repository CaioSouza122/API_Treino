FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for layer caching
COPY requirements.txt ./
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Copy project files
COPY . .

# Ensure container uses venv binaries
ENV PATH="/venv/bin:$PATH"

# Expose Flask default port
EXPOSE 5000

# Run production server using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
