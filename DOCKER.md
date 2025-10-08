# Docker Setup for Docstrange with CUDA GPU Support

This directory contains Docker configuration files to run docstrange web application with CUDA GPU acceleration.

## Prerequisites

- Docker Engine 19.03 or later
- [NVIDIA Docker runtime](https://github.com/NVIDIA/nvidia-docker) (nvidia-docker2)
- NVIDIA GPU with CUDA 11.8 support
- NVIDIA Driver 450.80.02 or later

### Installing NVIDIA Docker Runtime

**Ubuntu/Debian:**
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**Verify GPU is accessible:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Quick Start

### Using Docker Compose (Recommended)

1. Build and start the container:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the container:
```bash
docker-compose down
```

### Using Docker CLI

1. Build the image:
```bash
docker build -t docstrange-web:latest .
```

2. Run the container with GPU support:
```bash
docker run -d \
  --name docstrange-web \
  --gpus all \
  -p 8000:8000 \
  -v huggingface_cache:/root/.cache/huggingface \
  docstrange-web:latest
```

3. View logs:
```bash
docker logs -f docstrange-web
```

4. Stop and remove the container:
```bash
docker stop docstrange-web
docker rm docstrange-web
```

## Accessing the Application

Once the container is running, access the web interface at:
- **URL:** http://localhost:8000
- **Health Check:** http://localhost:8000/api/health
- **System Info:** http://localhost:8000/api/system-info (shows GPU availability)

## Configuration

### Environment Variables

You can customize the application by setting environment variables:

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e HF_HOME=/app/.cache/huggingface \
  docstrange-web:latest
```

Available environment variables:
- `CUDA_VISIBLE_DEVICES`: Specify which GPU(s) to use (default: 0)
- `HF_HOME`: Hugging Face model cache directory
- `NANONETS_API_KEY`: Optional API key for cloud processing

### Persistent Storage

The docker-compose.yml includes volume mounts for:
- **Model cache:** Persists downloaded AI models between container restarts
- **Data directory:** Optional mount for input/output files

### Port Mapping

By default, the application runs on port 8000. To use a different port:

```bash
docker run -d --gpus all -p 9000:8000 docstrange-web:latest
```

Or modify the `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"
```

## GPU Configuration

### Using Specific GPU(s)

To use a specific GPU or multiple GPUs:

```bash
# Use GPU 0
docker run -d --gpus '"device=0"' -p 8000:8000 docstrange-web:latest

# Use GPUs 0 and 1
docker run -d --gpus '"device=0,1"' -p 8000:8000 docstrange-web:latest

# Use all GPUs
docker run -d --gpus all -p 8000:8000 docstrange-web:latest
```

### Verifying GPU Access

Once the container is running, check GPU availability:

```bash
# Check if GPU is detected in the application
curl http://localhost:8000/api/system-info

# Check GPU usage inside container
docker exec docstrange-web nvidia-smi
```

## Building for Different CUDA Versions

The default Dockerfile uses CUDA 11.8. To use a different version, modify the base image in `Dockerfile`:

```dockerfile
# For CUDA 12.1
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Update PyTorch installation command
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Troubleshooting

### GPU Not Detected

1. Verify NVIDIA Docker runtime is installed:
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

2. Check Docker daemon configuration (`/etc/docker/daemon.json`):
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

3. Restart Docker daemon:
```bash
sudo systemctl restart docker
```

### Container Fails to Start

1. Check logs:
```bash
docker logs docstrange-web
```

2. Verify system requirements:
```bash
nvidia-smi  # Check GPU and driver version
docker --version  # Should be 19.03+
```

### Model Download Issues

The first run will download AI models (~500MB). This may take several minutes. Monitor progress:
```bash
docker logs -f docstrange-web
```

Models are cached in the volume, so subsequent runs are faster.

### Out of Memory Errors

If processing large documents causes OOM errors:

1. Increase Docker memory limits
2. Process smaller documents
3. Use CPU mode (set environment variable or API parameter)

## Performance Tips

1. **Model Caching:** Always use volume mounts for model cache to avoid re-downloading
2. **GPU Selection:** Use `CUDA_VISIBLE_DEVICES` to select the appropriate GPU
3. **Memory:** Ensure sufficient GPU memory for your document sizes
4. **Network:** For large file uploads, consider adjusting Docker network settings

## Development

To mount local code for development:

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/docstrange:/app/docstrange \
  docstrange-web:latest
```

Or use docker-compose with development override:
```yaml
# docker-compose.override.yml
services:
  docstrange:
    volumes:
      - ./docstrange:/app/docstrange
```

## Production Considerations

1. **Reverse Proxy:** Use nginx or traefik for SSL/TLS termination
2. **Resource Limits:** Set memory and CPU limits in docker-compose.yml
3. **Monitoring:** Use Docker health checks and external monitoring
4. **Backup:** Regularly backup the model cache volume
5. **Updates:** Rebuild image periodically for security updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.
