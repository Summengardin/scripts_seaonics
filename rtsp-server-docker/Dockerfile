FROM nvidia/cuda:12.3.1-base-ubuntu20.04

# Avoid interactive dialogue during build
ARG DEBIAN_FRONTEND=noninteractive

# Make virtual environment
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository -y ppa:deadsnakes && \
    apt-get update && apt-get install -y \
    python3.10-venv python3.10 python3.10-distutils python3.10-dev

RUN python3.10 -m venv /venv
ENV PATH=/venv/bin:$PATH


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


RUN apt-get update && \
    apt-get install -y \
    kmod \
    wget    


# Install pip for python3.10
RUN apt-get install -y curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
    #pip3 install --upgrade pip


# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install setuptools wheel
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
RUN pip3 install --upgrade six


WORKDIR /pyln
# Install pylon SDK
RUN wget https://www2.baslerweb.com/media/downloads/software/pylon_software/pylon_7_4_0_14900_linux_aarch64_setup.tar.gz && \
    tar -xzf ./pylon_7_4_0_14900_linux_aarch64_setup.tar.gz && \
    mkdir -p /opt/pylon && \
    tar -C /opt/pylon -xzf ./pylon-7.4.0.14900_linux-aarch64.tar.gz && \
    chmod 755 /opt/pylon


# Install pylon gst-plugin dependencies
RUN apt-get update && \
    apt-get install -y git gstreamer1.0-python3-plugin-loader ninja-build cmake && \
    pip3 install meson==0.61


# Build pylon gst-plugin
RUN export PYLON_ROOT=/opt/pylon && \
    git clone https://github.com/basler/gst-plugin-pylon.git && \
    cd gst-plugin-pylon && \
    meson setup builddir --prefix /usr/ && \
    ninja -C builddir && \
    ninja -C builddir install && \
    cd ../

RUN rm -rf /pyln      


WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app


RUN rm ~/.cache/gstreamer-1.0/registry*.bin; exit 0



# Set the default command for the container
CMD ["python3", "monitor_server.py"]

