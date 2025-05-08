# Use the official Python 3.8 slim image as the base
FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the local directory to /app in the container
COPY . /app

# Update and install system dependencies, then install Python packages
RUN apt update -y

# Install the dependencies from requirements.txt
RUN apt-get update && pip install -r requirements.txt

# Set the default command to run the Flask app
CMD ["python3", "app.py"]