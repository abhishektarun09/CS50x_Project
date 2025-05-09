# Use the official Python 3.8 slim image as the base
FROM python:3.8-slim

# Install SSH server
RUN apt-get update && apt-get install -y openssh-server && \
    mkdir /var/run/sshd && \
    echo "root:Docker!" | chpasswd  # default root password (optional but useful for debugging)

# Set the working directory inside the container
WORKDIR /app

# Copy your application code and the SSL cert
COPY . /app
COPY cert/DigiCertGlobalRootCA.crt.pem /app/cert/DigiCertGlobalRootCA.crt.pem

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment so that SSH works correctly
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1

# Expose HTTP and SSH ports
EXPOSE 80 2222

# Start SSH server in background and then run the Flask app
CMD service ssh start && python app.py
