FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ARG QEMU_VERSION=4.2.1

RUN apt-get update && apt-get install -y \
  build-essential git python3 python3-pip python3-setuptools \
  ninja-build pkg-config \
  libglib2.0-dev libpixman-1-dev zlib1g-dev \
  libfdt-dev libaio-dev libcap-ng-dev \
  libssl-dev \
  ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /src

RUN curl -L -o qemu.tar.xz https://download.qemu.org/qemu-${QEMU_VERSION}.tar.xz \
  && tar -xf qemu.tar.xz \
  && rm qemu.tar.xz

WORKDIR /src/qemu-${QEMU_VERSION}

# Build minimal + stable features for GNS3 Cisco labs:
# - x86_64-softmmu target
# - KVM enabled (host will provide /dev/kvm)
# - disable some optional stuff that often causes pain
RUN ./configure \
  --prefix=/opt/qemu421 \
  --target-list=x86_64-softmmu \
  --enable-kvm \
  --disable-werror \
  --disable-docs \
  --disable-sdl \
  --disable-gtk \
  --disable-vnc \
  --disable-curses

RUN make -j"$(nproc)" && make install

# helper: show version quickly
CMD ["/opt/qemu421/bin/qemu-system-x86_64", "--version"]
