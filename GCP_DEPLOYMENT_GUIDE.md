# 🌐 Google Cloud Platform Deployment Guide

> **Deploy MarketPulse from GitHub to Google Cloud**
>
> **Project:** MarketPulse Big Data Platform
> **Services:** 12 Docker containers (Kafka, Spark, Cassandra, Dashboard, etc.)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Option 1: Google Kubernetes Engine (GKE) - Recommended](#option-1-gke-recommended)
4. [Option 2: Compute Engine VM](#option-2-compute-engine-vm-simple)
5. [Option 3: Cloud Run (Dashboard Only)](#option-3-cloud-run-dashboard-only)
6. [Cost Estimation](#cost-estimation)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🎯 Overview

### What You'll Deploy

```
GitHub Repository
      ↓
Google Cloud Platform
      ├── Option 1: GKE (Kubernetes) - Production-grade, scalable
      ├── Option 2: Compute Engine - Simple VM, docker-compose
      └── Option 3: Cloud Run - Dashboard only (serverless)
```

### Architecture on GCP

```
Internet
    ↓
Load Balancer (GCP)
    ↓
┌─────────────────────────────────────────────┐
│  Google Kubernetes Engine (GKE)             │
│  ┌──────────────────────────────────────┐   │
│  │  Streaming Layer                      │   │
│  │  - Kafka (3 replicas)                 │   │
│  │  - Zookeeper                          │   │
│  │  - Spark Streaming                    │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Data Layer                           │   │
│  │  - Cassandra Cluster (3 nodes)       │   │
│  │  - Redis Cache                        │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Application Layer                    │   │
│  │  - Streamlit Dashboard                │   │
│  │  - ML Prediction Service              │   │
│  │  - Data Producers                     │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Monitoring                           │   │
│  │  - Prometheus                         │   │
│  │  - Grafana                            │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         ↓
   Cloud Storage (GCS) - Model storage
   Cloud SQL - Optional metadata
```

---

## ✅ Prerequisites

### 1. Google Cloud Account

```bash
# Sign up at https://cloud.google.com/
# Get $300 free credit for new accounts
```

### 2. Install Google Cloud SDK

```bash
# Linux/macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize
gcloud init
```

### 3. Install Required Tools

```bash
# kubectl (Kubernetes CLI)
gcloud components install kubectl

# Docker (if not already installed)
sudo apt-get install docker.io

# Helm (Kubernetes package manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 4. GitHub Repository Setup

```bash
# Upload your code to GitHub first
cd /home/lol/big_btata/MarketPulse-GitHub
git init
git add .
git commit -m "Initial commit: MarketPulse v2.0"
git remote add origin https://github.com/yourusername/MarketPulse.git
git push -u origin main
```

---

## 🚀 Option 1: GKE (Recommended)

### **Best For:** Production deployment, auto-scaling, high availability

### Step 1: Create GCP Project

```bash
# Set variables
export PROJECT_ID="marketpulse-prod"
export REGION="europe-west1"  # Or us-central1, asia-east1
export ZONE="europe-west1-b"

# Create project
gcloud projects create $PROJECT_ID --name="MarketPulse Production"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (required)
# Go to: https://console.cloud.google.com/billing
```

### Step 2: Enable Required APIs

```bash
# Enable GKE and Container Registry
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
```

### Step 3: Create GKE Cluster

```bash
# Create cluster (3 nodes, n1-standard-4 machines)
gcloud container clusters create marketpulse-cluster \
    --zone=$ZONE \
    --num-nodes=3 \
    --machine-type=n1-standard-4 \
    --disk-size=50GB \
    --enable-autoscaling \
    --min-nodes=3 \
    --max-nodes=6 \
    --enable-autorepair \
    --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials marketpulse-cluster --zone=$ZONE

# Verify
kubectl get nodes
```

### Step 4: Build and Push Docker Images

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Set image prefix
export IMAGE_PREFIX="gcr.io/$PROJECT_ID"

# Build all images
cd /home/lol/big_btata/MarketPulse-GitHub

# Dashboard
docker build -t $IMAGE_PREFIX/dashboard:v1 -f- . <<'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY dashboard/ ./dashboard/
COPY ml_models/ ./ml_models/
COPY config/ ./config/
CMD ["streamlit", "run", "dashboard/enhanced_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

# Stock Producer
docker build -t $IMAGE_PREFIX/stock-producer:v1 -f- . <<'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY producers/ ./producers/
COPY config/ ./config/
COPY files/ ./files/
CMD ["python", "producers/morocco_stock_producer.py"]
EOF

# Spark Processor
docker build -t $IMAGE_PREFIX/spark-processor:v1 -f- . <<'EOF'
FROM bitnami/spark:3.3.0
USER root
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY processors/ ./processors/
COPY config/ ./config/
CMD ["spark-submit", "--master", "local[*]", "processors/spark_processor.py"]
EOF

# Prediction Service
docker build -t $IMAGE_PREFIX/prediction-service:v1 -f- . <<'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ml_models/ ./ml_models/
COPY config/ ./config/
CMD ["python", "ml_models/prediction_service.py"]
EOF

# Push all images
docker push $IMAGE_PREFIX/dashboard:v1
docker push $IMAGE_PREFIX/stock-producer:v1
docker push $IMAGE_PREFIX/spark-processor:v1
docker push $IMAGE_PREFIX/prediction-service:v1
```

### Step 5: Deploy Using Kubernetes Manifests

I'll create the Kubernetes manifests in the next step...

---

## 💻 Option 2: Compute Engine VM (Simple)

### **Best For:** Quick deployment, testing, learning

### Step 1: Create VM Instance

```bash
# Create VM with Docker pre-installed
gcloud compute instances create marketpulse-vm \
    --zone=$ZONE \
    --machine-type=n1-standard-4 \
    --boot-disk-size=100GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server \
    --metadata=startup-script='#!/bin/bash
        apt-get update
        apt-get install -y docker.io docker-compose git
        systemctl start docker
        systemctl enable docker
        usermod -aG docker $USER'

# Create firewall rules
gcloud compute firewall-rules create allow-dashboard \
    --allow=tcp:8501 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server \
    --description="Allow Streamlit dashboard access"

gcloud compute firewall-rules create allow-kafka \
    --allow=tcp:9092 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server \
    --description="Allow Kafka access"
```

### Step 2: SSH and Deploy

```bash
# SSH into VM
gcloud compute ssh marketpulse-vm --zone=$ZONE

# Once inside the VM:
# Clone your GitHub repository
git clone https://github.com/yourusername/MarketPulse.git
cd MarketPulse

# Create .env file
cp .env.example .env
nano .env  # Edit with your API keys

# Start all services
docker-compose -f docker-compose.enhanced.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f dashboard
```

### Step 3: Access Dashboard

```bash
# Get VM external IP
gcloud compute instances describe marketpulse-vm \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Access dashboard at: http://EXTERNAL_IP:8501
```

---

## ☁️ Option 3: Cloud Run (Dashboard Only)

### **Best For:** Dashboard-only deployment, serverless, auto-scaling

```bash
# Build dashboard image
gcloud builds submit --tag gcr.io/$PROJECT_ID/dashboard:v1 \
    --file=- . <<'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY dashboard/ ./dashboard/
COPY ml_models/ ./ml_models/
COPY config/ ./config/
ENV PORT=8080
CMD streamlit run dashboard/enhanced_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
EOF

# Deploy to Cloud Run
gcloud run deploy marketpulse-dashboard \
    --image=gcr.io/$PROJECT_ID/dashboard:v1 \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=1 \
    --max-instances=10

# Get URL
gcloud run services describe marketpulse-dashboard \
    --region=$REGION \
    --format='value(status.url)'
```

---

## 💰 Cost Estimation

### Option 1: GKE Cluster (Production)

| Resource | Specs | Monthly Cost (USD) |
|----------|-------|-------------------|
| **GKE Cluster** | 3 nodes × n1-standard-4 | ~$290 |
| **Persistent Disks** | 150GB SSD | ~$25 |
| **Load Balancer** | 1 instance | ~$20 |
| **Egress Traffic** | ~100GB/month | ~$12 |
| **Container Registry** | Storage | ~$5 |
| **Cloud Logging** | Basic | ~$10 |
| **TOTAL** | | **~$362/month** |

### Option 2: Compute Engine VM (Simple)

| Resource | Specs | Monthly Cost (USD) |
|----------|-------|-------------------|
| **VM Instance** | n1-standard-4 (4 vCPU, 15GB RAM) | ~$120 |
| **Boot Disk** | 100GB SSD | ~$17 |
| **External IP** | Static | ~$7 |
| **Egress Traffic** | ~50GB/month | ~$6 |
| **TOTAL** | | **~$150/month** |

### Option 3: Cloud Run (Dashboard Only)

| Resource | Specs | Monthly Cost (USD) |
|----------|-------|-------------------|
| **Cloud Run** | 2 vCPU, 2GB RAM, always-on | ~$50 |
| **Container Registry** | Storage | ~$5 |
| **TOTAL** | | **~$55/month** |

### 💡 Cost Savings Tips

```bash
# 1. Use preemptible VMs (up to 80% cheaper)
gcloud container clusters create marketpulse-cluster \
    --preemptible \
    --machine-type=n1-standard-2  # Smaller machines

# 2. Stop cluster when not in use
gcloud container clusters resize marketpulse-cluster \
    --num-nodes=0 --zone=$ZONE

# 3. Use committed use discounts (57% off for 1-year)
# Go to: https://console.cloud.google.com/compute/commitments

# 4. Set up budget alerts
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="MarketPulse Budget" \
    --budget-amount=100USD
```

---

## 📊 Monitoring & Maintenance

### Cloud Monitoring Dashboard

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# View metrics
# Go to: https://console.cloud.google.com/monitoring
```

### Logs

```bash
# View logs (GKE)
kubectl logs -f deployment/dashboard

# View logs (Compute Engine)
gcloud compute ssh marketpulse-vm --zone=$ZONE
sudo journalctl -u docker -f

# Cloud Logging
gcloud logging read "resource.type=gce_instance" --limit=50
```

### Automatic Backups

```bash
# Create backup script
cat > backup.sh <<'EOF'
#!/bin/bash
# Backup Cassandra data to Cloud Storage
kubectl exec -it cassandra-0 -- nodetool snapshot marketpulse
gsutil -m cp -r /var/lib/cassandra/data gs://marketpulse-backups/$(date +%Y%m%d)/
EOF

# Schedule with Cloud Scheduler
gcloud scheduler jobs create http cassandra-backup \
    --schedule="0 2 * * *" \
    --uri="https://your-backup-function.run.app" \
    --http-method=POST
```

---

## 🔒 Security Best Practices

### 1. Secrets Management

```bash
# Create secret
kubectl create secret generic marketpulse-secrets \
    --from-literal=KAFKA_PASSWORD=your-password \
    --from-literal=CASSANDRA_PASSWORD=your-password \
    --from-literal=API_KEY=your-api-key

# Use in deployment
# See kubernetes-manifests/deployment.yaml
```

### 2. Network Policies

```bash
# Restrict Kafka access
kubectl apply -f- <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kafka-network-policy
spec:
  podSelector:
    matchLabels:
      app: kafka
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: producer
EOF
```

### 3. IAM Roles

```bash
# Create service account with minimal permissions
gcloud iam service-accounts create marketpulse-sa \
    --display-name="MarketPulse Service Account"

# Grant specific permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:marketpulse-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

---

## 🚀 Quick Start Commands

### For GKE Deployment

```bash
# 1. Create project and cluster (15 min)
export PROJECT_ID="marketpulse-prod"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
gcloud container clusters create marketpulse-cluster \
    --zone=europe-west1-b --num-nodes=3 --machine-type=n1-standard-4

# 2. Build and push images (10 min)
# See Step 4 above

# 3. Deploy Kubernetes manifests (5 min)
kubectl apply -f kubernetes-manifests/

# 4. Get dashboard URL (1 min)
kubectl get service dashboard -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### For VM Deployment

```bash
# 1. Create VM (5 min)
gcloud compute instances create marketpulse-vm \
    --zone=europe-west1-b --machine-type=n1-standard-4

# 2. SSH and deploy (10 min)
gcloud compute ssh marketpulse-vm
git clone https://github.com/yourusername/MarketPulse.git
cd MarketPulse
docker-compose -f docker-compose.enhanced.yml up -d

# 3. Access dashboard
# http://VM_EXTERNAL_IP:8501
```

---

## 📚 Next Steps

1. **Read:** `kubernetes-manifests/README.md` for Kubernetes deployment details
2. **Configure:** Set up Cloud Monitoring alerts
3. **Optimize:** Tune resource limits based on actual usage
4. **Scale:** Enable horizontal pod autoscaling
5. **Secure:** Set up VPC, Cloud Armor, IAM policies

---

## 🆘 Troubleshooting

### Issue: Pods not starting

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Issue: Out of memory

```bash
# Increase resources
kubectl edit deployment dashboard
# Increase memory: 2Gi → 4Gi
```

### Issue: Connection refused

```bash
# Check service
kubectl get svc
kubectl describe svc dashboard

# Check firewall
gcloud compute firewall-rules list
```

---

## 📞 Support

- **GCP Documentation:** https://cloud.google.com/docs
- **GKE Pricing:** https://cloud.google.com/kubernetes-engine/pricing
- **Free Tier:** https://cloud.google.com/free
- **Support:** https://cloud.google.com/support

---

**Status:** Ready for GCP deployment
**Next:** Create Kubernetes manifests → See `kubernetes-manifests/` directory
