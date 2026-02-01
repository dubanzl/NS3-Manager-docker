FROM ubuntu:20.04

ARG QEMU_VERSION=4.2.1
ARG GNS3_SERVER_VERSION=2.2.40

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    libglib2.0-dev \
    libpixman-1-dev \
    libssl-dev \
    libgtk-3-dev \
    libsdl2-dev \
    libcap-ng-dev \
    libattr1-dev \
    libfdt-dev \
    zlib1g-dev \
    libtool \
    pkg-config \
    gettext \
    wget \
    curl \
    iproute2 \
    iputils-ping \
    net-tools \
    qemu-utils \
    libaio-dev \
    libspice-server-dev \
    libspice-protocol-dev \
    libusb-1.0-0-dev \
    ninja-build \
    meson \
    cmake \
    libpcap-dev \
 && rm -rf /var/lib/apt/lists/*

# -----------------------
# Build and install uBridge (for GNS3)
# -----------------------
WORKDIR /tmp
RUN git clone https://github.com/GNS3/ubridge.git \
 && cd ubridge \
 && make \
 && make install \
 && chown root:root /usr/local/bin/ubridge \
 && chmod 4755 /usr/local/bin/ubridge

# -----------------------
# Download + build QEMU
# -----------------------
WORKDIR /opt

RUN wget https://download.qemu.org/qemu-${QEMU_VERSION}.tar.xz \
 && tar xf qemu-${QEMU_VERSION}.tar.xz \
 && cd qemu-${QEMU_VERSION} \
 && ./configure \
      --enable-kvm \
      --enable-gtk \
      --enable-sdl \
      --disable-werror \
 && make -j$(nproc) \
 && make install \
 && cd /opt \
 && rm -rf qemu-${QEMU_VERSION} qemu-${QEMU_VERSION}.tar.xz

# Install GNS3 server
RUN pip3 install --no-cache-dir gns3-server==${GNS3_SERVER_VERSION}

EXPOSE 3080
CMD ["gns3server", "--host", "0.0.0.0", "--port", "3080"]
