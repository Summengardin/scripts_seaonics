# docker run -it --rm -p 8554:8554 rtspserver:latest
# docker run -it --rm --net=host --runtime nvidia rtspserver:latest



# Use an NVIDIA CUDA base image
FROM nvidia/cuda:12.3.1-base-ubuntu20.04

# Set a label for maintaining metadata
#LABEL maintainer="your-email@example.com"

# Avoid interactive dialogue during build
ARG DEBIAN_FRONTEND=noninteractive


# Install python3.10
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils python3.10-dev && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Install pip for python3.10
RUN apt-get install -y curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Update and install system packages
RUN apt-get update && apt-get install -y \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    #gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    #gstreamer1.0-gtk3 \
    #gstreamer1.0-pulseaudio \
    libgstrtspserver-1.0-dev \
    libcairo2-dev \
    libxt-dev \
    libgirepository1.0-dev \
    gir1.2-gst-rtsp-server-1.0 \
    && rm -rf /var/lib/apt/lists/*



# Install Python dependencies (if any)
COPY requirements.txt /tmp/
RUN pip install setuptools wheel
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set the working directory in the container
WORKDIR /app

COPY /data/producer /app/producer

# Copy the current directory contents into the container at /app
COPY . /app

RUN gst-inspect-1.0 --version
# Set the default command for the container
CMD ["python3", "monitor_server.py", "-c", "producer/ProducerGEV.cti"]
