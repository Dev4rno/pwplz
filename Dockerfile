# Use the official Python image as a base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Install dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose a default port (optional, helps documentation)
EXPOSE 8000

# Set the environment variable for production mode (optional)
ENV ENVIRONMENT=production

# Use the $PORT variable dynamically
CMD ["sh", "-c", "uvicorn core.app:app --host 0.0.0.0 --port ${PORT:-8000}"]