# ⚡ GCP Quick Start - MarketPulse

> **Deploy your project to Google Cloud in 30 minutes**

---

## 🎯 Choose Your Path

### Path A: Simple VM (Easiest) ⭐ Recommended for Testing
- **Time:** 15 minutes
- **Cost:** ~$150/month
- **Best for:** Testing, demos, learning
- **Complexity:** ⭐☆☆☆☆

### Path B: GKE (Production)
- **Time:** 45 minutes
- **Cost:** ~$360/month
- **Best for:** Production, scaling, high availability
- **Complexity:** ⭐⭐⭐⭐☆

### Path C: Dashboard Only (Cheapest)
- **Time:** 10 minutes
- **Cost:** ~$55/month
- **Best for:** Just showing the dashboard
- **Complexity:** ⭐☆☆☆☆

---

# 🚀 PATH A: Simple VM Deployment (Recommended)

## Step 1: Install Google Cloud SDK (5 min)

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login and initialize
gcloud init

# Follow the prompts:
# - Login with your Google account
# - Create a new project: "marketpulse-prod"
# - Choose region: europe-west1 (or closest to you)
```

## Step 2: Create and Configure VM (5 min)

```bash
# Set variables
export PROJECT_ID="marketpulse-prod"
export ZONE="europe-west1-b"

# Set project
gcloud config set project $PROJECT_ID

# Create VM with Docker pre-installed
gcloud compute instances create marketpulse-vm \
    --zone=$ZONE \
    --machine-type=n1-standard-4 \
    --boot-disk-size=100GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server \
    --metadata=startup-script='#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose git
systemctl start docker
systemctl enable docker
usermod -aG docker $USER'

# Create firewall rule for dashboard
gcloud compute firewall-rules create allow-streamlit \
    --allow=tcp:8501 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server

# Wait 2 minutes for VM to start
echo "⏳ Waiting for VM to initialize..."
sleep 120
```

## Step 3: Deploy Application (5 min)

```bash
# SSH into VM
gcloud compute ssh marketpulse-vm --zone=$ZONE

# Once inside the VM, run these commands:

# Clone your GitHub repository
git clone https://github.com/yourusername/MarketPulse.git
cd MarketPulse

# Create .env file
cat > .env <<'EOF'
# API Keys
FINNHUB_API_KEY=your-finnhub-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# Kafka
KAFKA_BROKER=kafka:9092

# Cassandra
CASSANDRA_HOST=cassandra
CASSANDRA_PORT=9042

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
EOF

# Edit .env with your actual API keys
nano .env

# Start all services
docker-compose -f docker-compose.enhanced.yml up -d

# Check status
docker-compose ps

# View dashboard logs
docker-compose logs -f dashboard
```

## Step 4: Access Your Dashboard (1 min)

```bash
# Exit SSH (press Ctrl+D)

# Get VM external IP
export VM_IP=$(gcloud compute instances describe marketpulse-vm \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "🎉 Dashboard URL: http://$VM_IP:8501"

# Open in browser
xdg-open "http://$VM_IP:8501"  # Linux
open "http://$VM_IP:8501"       # macOS
```

**✅ Done! Your MarketPulse is now live on Google Cloud!**

---

# 🌐 PATH B: GKE Production Deployment

## Step 1: Setup GCP (10 min)

```bash
# Set variables
export PROJECT_ID="marketpulse-prod"
export REGION="europe-west1"
export ZONE="europe-west1-b"

# Create project
gcloud projects create $PROJECT_ID

# Set as active
gcloud config set project $PROJECT_ID

# Enable billing at: https://console.cloud.google.com/billing

# Enable APIs
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 2: Create GKE Cluster (15 min)

```bash
# Create cluster
gcloud container clusters create marketpulse-cluster \
    --zone=$ZONE \
    --num-nodes=3 \
    --machine-type=n1-standard-4 \
    --disk-size=50GB \
    --enable-autoscaling \
    --min-nodes=3 \
    --max-nodes=6

# Get credentials
gcloud container clusters get-credentials marketpulse-cluster --zone=$ZONE

# Verify
kubectl get nodes
```

## Step 3: Build and Push Images (10 min)

```bash
# Configure Docker
gcloud auth configure-docker

# Clone your repo locally
git clone https://github.com/yourusername/MarketPulse.git
cd MarketPulse

# Build dashboard image
docker build -t gcr.io/$PROJECT_ID/dashboard:v1 \
    --build-arg PORT=8501 \
    -f- . <<'DOCKERFILE'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard/ ./dashboard/
COPY ml_models/ ./ml_models/
COPY config/ ./config/
ENV PORT=8501
EXPOSE 8501
CMD streamlit run dashboard/enhanced_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
DOCKERFILE

# Push image
docker push gcr.io/$PROJECT_ID/dashboard:v1
```

## Step 4: Deploy to Kubernetes (10 min)

```bash
# Navigate to kubernetes manifests
cd kubernetes-manifests

# Update PROJECT_ID in YAML files
sed -i "s/PROJECT_ID/$PROJECT_ID/g" *.yaml

# Create secrets
cp secrets.yaml.template secrets.yaml
nano secrets.yaml  # Add your API keys

# Deploy all
./deploy-all.sh

# Watch deployment
kubectl get pods -n marketpulse -w

# Get dashboard URL (wait for EXTERNAL-IP)
kubectl get svc dashboard -n marketpulse
```

## Step 5: Access Dashboard

```bash
# Get external IP
export DASHBOARD_IP=$(kubectl get svc dashboard -n marketpulse \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "🎉 Dashboard URL: http://$DASHBOARD_IP"
```

**✅ Production deployment complete!**

---

# 💰 PATH C: Dashboard Only (Cloud Run)

## Deploy Dashboard to Cloud Run (Serverless)

```bash
# Set variables
export PROJECT_ID="marketpulse-prod"
export REGION="europe-west1"

# Build and deploy in one command
gcloud run deploy marketpulse-dashboard \
    --source . \
    --platform managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars="STREAMLIT_SERVER_HEADLESS=true"

# Get URL
gcloud run services describe marketpulse-dashboard \
    --region=$REGION \
    --format='value(status.url)'
```

**✅ Dashboard deployed! Auto-scales from 0 to 10 instances.**

---

# 📊 Comparison Table

| Feature | VM (Path A) | GKE (Path B) | Cloud Run (Path C) |
|---------|-------------|--------------|-------------------|
| **Setup Time** | 15 min | 45 min | 10 min |
| **Monthly Cost** | $150 | $360 | $55 |
| **Full System** | ✅ Yes | ✅ Yes | ❌ Dashboard only |
| **Auto-scaling** | ❌ No | ✅ Yes | ✅ Yes |
| **High Availability** | ❌ No | ✅ Yes | ✅ Yes |
| **Complexity** | Low | High | Low |
| **Best For** | Testing/Demo | Production | Just Dashboard |

---

# 🛠️ Common Operations

## View Logs

**VM:**
```bash
gcloud compute ssh marketpulse-vm --zone=$ZONE
docker-compose logs -f
```

**GKE:**
```bash
kubectl logs -f deployment/dashboard -n marketpulse
```

**Cloud Run:**
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

## Stop to Save Costs

**VM:**
```bash
gcloud compute instances stop marketpulse-vm --zone=$ZONE
```

**GKE:**
```bash
gcloud container clusters resize marketpulse-cluster --num-nodes=0 --zone=$ZONE
```

**Cloud Run:**
```bash
# Automatically scales to 0 when not in use
```

## Restart

**VM:**
```bash
gcloud compute instances start marketpulse-vm --zone=$ZONE
```

**GKE:**
```bash
gcloud container clusters resize marketpulse-cluster --num-nodes=3 --zone=$ZONE
```

## Delete Everything

**VM:**
```bash
gcloud compute instances delete marketpulse-vm --zone=$ZONE
gcloud compute firewall-rules delete allow-streamlit
```

**GKE:**
```bash
gcloud container clusters delete marketpulse-cluster --zone=$ZONE
```

**Cloud Run:**
```bash
gcloud run services delete marketpulse-dashboard --region=$REGION
```

---

# ✅ Success Checklist

After deployment, verify:

- [ ] VM/Cluster is running
- [ ] Dashboard is accessible
- [ ] All Docker containers are up (VM) or pods are running (GKE)
- [ ] Can select Morocco stocks
- [ ] Charts are displaying
- [ ] No errors in logs

---

# 🆘 Troubleshooting

## Issue: Can't access dashboard

**VM:**
```bash
# Check firewall
gcloud compute firewall-rules list

# Check if container is running
gcloud compute ssh marketpulse-vm --zone=$ZONE
docker ps
docker logs marketpulse_dashboard_1
```

**GKE:**
```bash
# Check service
kubectl get svc dashboard -n marketpulse

# Check pods
kubectl get pods -n marketpulse
kubectl describe pod <pod-name> -n marketpulse
```

## Issue: Out of quota

```bash
# Check quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Request quota increase:
# https://console.cloud.google.com/iam-admin/quotas
```

## Issue: Billing not enabled

```bash
# Enable billing at:
# https://console.cloud.google.com/billing
```

---

# 📚 Next Steps

1. **Add domain name:** Use Cloud DNS
2. **Enable HTTPS:** Use Cloud Load Balancer with SSL
3. **Set up monitoring:** Cloud Monitoring dashboard
4. **Configure alerts:** Budget alerts, uptime alerts
5. **Add CI/CD:** Cloud Build for auto-deployment

---

# 💡 Pro Tips

1. **Free Tier:** New accounts get $300 free credit
2. **Stop when not in use:** Save 70% by stopping nights/weekends
3. **Preemptible VMs:** Save 80% (but can be shut down anytime)
4. **Budget alerts:** Set at $50, $100, $150 to avoid surprises
5. **Committed use:** Save 57% with 1-year commit

---

**📖 Full Documentation:** See `GCP_DEPLOYMENT_GUIDE.md`

**🎯 Recommended:** Start with Path A (VM), migrate to Path B (GKE) for production
