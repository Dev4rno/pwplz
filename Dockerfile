# Use the official Python image as a base image
FROM python:3-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to install dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . /app

# Ensure static files are included
COPY ./static /app/static

# Expose the default port
EXPOSE 8000

# Set environment variables (optional)
ENV ENVIRONMENT=production

# Run the application with static file handling
CMD ["sh", "-c", "uvicorn core.app:app --host 0.0.0.0 --port ${PORT:-8000}"]