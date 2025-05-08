# Use the official Python 3.8 slim image as the base
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the local directory to /app in the container
COPY . /app

# Update and install system dependencies, then install Python packages
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends gcc # install gcc if needed (you can add other dependencies if required)

# Install the dependencies from requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set the default command to run the Flask app
CMD ["python3", "app.py"]