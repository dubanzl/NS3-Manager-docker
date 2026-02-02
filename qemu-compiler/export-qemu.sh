#!/bin/bash

cid=$(docker create qemu421:build)

sudo rm -rf /opt/qemu421
sudo docker cp "$cid":/opt/qemu421 /opt/qemu421

docker rm "$cid"

echo "QEMU exported to /opt/qemu421"