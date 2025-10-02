FROM python:3.12.0-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP=/app

# Change working directory
WORKDIR $APP

# Install dependencies
COPY requirements.txt $APP
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy project files
COPY . $APP

# Expose port
EXPOSE 8000

# Entrypoint
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

# Run Gunicorn server
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]
