# GNS3 QEMU Docker

Docker container for GNS3 server with custom QEMU build.

## Configuration

To update versions, manually edit the configuration files:

### Update Versions

Edit `docker-compose.yml` and update both the build args and image name:

```yaml
image: gns3-qemu:4.2.1-server-2.2.40
```

**Important**: When updating versions, make sure to update the `image` name to match the new version numbers.

Or modify the default values in `Dockerfile`:

```dockerfile
ARG QEMU_VERSION=4.2.1
ARG GNS3_SERVER_VERSION=2.2.40
```

**Note**: If you change values in `Dockerfile`, you should also update `docker-compose.yml` to match, or the build args in `docker-compose.yml` will override the Dockerfile defaults.

## Usage

### Build the image

```bash
docker-compose build
```

### Start the GNS3 server

```bash
docker-compose up -d
```

### View logs

```bash
docker-compose logs -f
```

### Stop the server

```bash
docker-compose down
```

### Access the server

The GNS3 server API is available at:
- **API**: http://localhost:3080/api

## Features

- Custom QEMU build (version configurable)
- GNS3 server (version configurable)
- uBridge for network bridging
- Persistent data volume for GNS3 projects
