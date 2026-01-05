# MarketPulse - Quick Start Guide

## 🚀 One-Command Startup

To start the entire MarketPulse platform, simply run:

```bash
./start-marketpulse.sh
```

## 📋 What the Script Does

The automated startup script will:

1. **Check Prerequisites**
   - Verify Docker and Docker Compose are installed
   - Confirm Docker daemon is running
   - Check for Python (optional)

2. **Setup Environment**
   - Create `.env` file from `.env.example` if needed
   - Allow you to configure API keys and settings

3. **Network Configuration**
   - Create Docker network for MarketPulse services

4. **Start Services**
   - Pull latest Docker images
   - Start all services (Kafka, Cassandra, Spark, Dashboard, etc.)
   - Run health checks on all containers

5. **Display Access Information**
   - Show URLs for dashboards and monitoring tools
   - Provide useful commands for managing the platform

## 🌐 Access Points

Once started, access the platform at:

- **Main Dashboard**: http://localhost:8501
- **Enhanced Dashboard**: http://localhost:8502
- **Grafana Monitoring**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Spark Master UI**: http://localhost:8080

## 🛠️ Useful Commands

```bash
# Start the platform
./start-marketpulse.sh

# View logs
docker-compose -f docker-compose.enhanced.yml logs -f

# Stop all services
docker-compose -f docker-compose.enhanced.yml down

# Restart specific service
docker-compose -f docker-compose.enhanced.yml restart <service-name>

# Check service status
docker-compose -f docker-compose.enhanced.yml ps
```

## ⚙️ Configuration

Before first run, update the `.env` file with your API keys:

```bash
# Edit environment file
nano .env
```

Required API keys:
- **Alpha Vantage**: Get from https://www.alphavantage.co/support/#api-key
- **Finnhub**: Get from https://finnhub.io/register

## 📦 Manual Installation (Alternative)

If you prefer manual setup:

```bash
# 1. Setup environment
cp .env.example .env
nano .env  # Add your API keys

# 2. Start services
docker-compose -f docker-compose.enhanced.yml up -d

# 3. Check logs
docker-compose -f docker-compose.enhanced.yml logs -f
```

## 🔧 Troubleshooting

### Services won't start
```bash
# Clean up old containers
docker-compose -f docker-compose.enhanced.yml down -v

# Remove dangling images
docker system prune -f

# Restart
./start-marketpulse.sh
```

### Port conflicts
If ports are already in use, modify `docker-compose.enhanced.yml` to use different ports.

### Out of memory
Increase Docker memory allocation in Docker Desktop settings (minimum 4GB recommended, 8GB optimal).

## 📚 More Documentation

- `README_ENHANCED.md` - Detailed feature documentation
- `DEPLOYMENT_GUIDE.md` - Production deployment guide
- `GCP_DEPLOYMENT_GUIDE.md` - Google Cloud Platform deployment
- `START_HERE.md` - Complete project overview

## 🆘 Support

For issues or questions:
1. Check the logs: `docker-compose -f docker-compose.enhanced.yml logs`
2. Review documentation in the project folder
3. Verify all prerequisites are met
