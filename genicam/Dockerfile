# Use an NVIDIA CUDA base image
FROM nvidia/cuda:11.1-base-ubuntu20.04

# Set a label for maintaining metadata
#LABEL maintainer="your-email@example.com"

# Avoid interactive dialogue during build
ARG DEBIAN_FRONTEND=noninteractive

# Update and install system packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstrtspserver-1.0-dev \
    libjansson-dev \
    libcairo2-dev \
    libxt-dev \
    libgirepository1.0-dev \
    gir1.2-gst-rtsp-server-1.0 \
    && rm -rf /var/lib/apt/lists/*



# Install Python dependencies (if any)
COPY requirements.txt /tmp/
RUN pip3 install setuptools wheel
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set the default command for the container
CMD ["python3", "monitor_server.py"]
