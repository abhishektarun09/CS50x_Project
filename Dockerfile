# Use the official Python 3.8 slim image as the base
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the local directory to /app in the container
COPY . /app

# Install the dependencies from requirements.txt
RUN pip install -r requirements.txt

EXPOSE 80

# Set the default command to run the Flask app
CMD ["python", "app.py"]