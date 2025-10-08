# Quick Start: Docker Deployment

This is a minimal quick-start guide for running docstrange with Docker and GPU support.

## Prerequisites

1. **Install Docker**: https://docs.docker.com/get-docker/
2. **Install NVIDIA Docker Runtime**:
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

3. **Verify GPU Access**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

## Run with Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

Access at: http://localhost:8000

## Run with Docker CLI

```bash
# Build the image
docker build -t docstrange-web .

# Run the container
docker run -d \
  --name docstrange-web \
  --gpus all \
  -p 8000:8000 \
  -v docstrange-models:/root/.cache/huggingface \
  docstrange-web:latest

# View logs
docker logs -f docstrange-web

# Stop and remove
docker stop docstrange-web && docker rm docstrange-web
```

## First Run

The first startup will download AI models (~500MB). This takes 5-10 minutes depending on your internet connection. Progress is shown in the logs.

## Testing

Run the validation script:
```bash
./test_docker.sh
```

## Troubleshooting

**GPU not detected:**
- Check: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`
- Ensure NVIDIA Docker runtime is installed
- Verify NVIDIA driver version: `nvidia-smi`

**Port already in use:**
```bash
# Use a different port
docker run -d --gpus all -p 9000:8000 docstrange-web
```

**Container fails to start:**
```bash
# Check logs for errors
docker logs docstrange-web
```

## For More Details

See [DOCKER.md](DOCKER.md) for comprehensive documentation including:
- Production deployment
- Environment variables
- Volume management
- Performance tuning
- Security considerations

## Support

- 📝 Documentation: [README.md](README.md)
- 🐛 Issues: https://github.com/nanonets/docstrange/issues
- 💬 Discussions: https://github.com/nanonets/docstrange/discussions
