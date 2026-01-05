#!/bin/bash

# MarketPulse GKE Deployment Script
# This script deploys all Kubernetes resources in the correct order

set -e

echo "🚀 MarketPulse GKE Deployment"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if secrets.yaml exists
if [ ! -f "secrets.yaml" ]; then
    echo "⚠️  secrets.yaml not found!"
    echo "📝 Creating from template..."
    cp secrets.yaml.template secrets.yaml
    echo ""
    echo "${YELLOW}⚠️  IMPORTANT: Edit secrets.yaml with your actual API keys and passwords${NC}"
    echo "Then run this script again."
    echo ""
    echo "nano secrets.yaml"
    exit 1
fi

echo "📦 Deploying resources in order..."
echo ""

# Function to wait for deployment
wait_for_deployment() {
    local deployment=$1
    local namespace=$2
    echo "⏳ Waiting for $deployment to be ready..."
    kubectl rollout status deployment/$deployment -n $namespace --timeout=300s
    echo "${GREEN}✅ $deployment is ready${NC}"
    echo ""
}

# Function to wait for statefulset
wait_for_statefulset() {
    local statefulset=$1
    local namespace=$2
    echo "⏳ Waiting for $statefulset to be ready..."
    kubectl rollout status statefulset/$statefulset -n $namespace --timeout=300s
    echo "${GREEN}✅ $statefulset is ready${NC}"
    echo ""
}

# 1. Namespace
echo "1️⃣  Creating namespace..."
kubectl apply -f namespace.yaml
echo "${GREEN}✅ Namespace created${NC}"
echo ""

# 2. ConfigMap
echo "2️⃣  Creating ConfigMap..."
kubectl apply -f configmap.yaml
echo "${GREEN}✅ ConfigMap created${NC}"
echo ""

# 3. Secrets
echo "3️⃣  Creating Secrets..."
kubectl apply -f secrets.yaml
echo "${GREEN}✅ Secrets created${NC}"
echo ""

# 4. Zookeeper
echo "4️⃣  Deploying Zookeeper..."
kubectl apply -f zookeeper.yaml
wait_for_deployment "zookeeper" "marketpulse"

# 5. Kafka
echo "5️⃣  Deploying Kafka..."
kubectl apply -f kafka.yaml
wait_for_deployment "kafka" "marketpulse"

# Wait a bit for Kafka to be fully ready
echo "⏳ Waiting 30s for Kafka to be fully ready..."
sleep 30
echo "${GREEN}✅ Kafka is ready${NC}"
echo ""

# 6. Cassandra
echo "6️⃣  Deploying Cassandra..."
kubectl apply -f cassandra.yaml
wait_for_statefulset "cassandra" "marketpulse"

# 7. Redis
echo "7️⃣  Deploying Redis..."
kubectl apply -f redis.yaml
wait_for_deployment "redis" "marketpulse"

# 8. Stock Producer (optional - comment out if not ready)
if [ -f "stock-producer.yaml" ]; then
    echo "8️⃣  Deploying Stock Producer..."
    kubectl apply -f stock-producer.yaml
    wait_for_deployment "stock-producer" "marketpulse"
fi

# 9. Dashboard
echo "9️⃣  Deploying Dashboard..."
kubectl apply -f dashboard.yaml
wait_for_deployment "dashboard" "marketpulse"

echo ""
echo "════════════════════════════════════════"
echo "${GREEN}🎉 Deployment Complete!${NC}"
echo "════════════════════════════════════════"
echo ""

# Get dashboard URL
echo "📊 Getting Dashboard URL..."
echo "⏳ Waiting for LoadBalancer IP..."
kubectl get svc dashboard -n marketpulse

echo ""
echo "Run this command to get the dashboard URL:"
echo "${YELLOW}kubectl get svc dashboard -n marketpulse -o jsonpath='{.status.loadBalancer.ingress[0].ip}'${NC}"
echo ""
echo "Or watch for the external IP:"
echo "${YELLOW}kubectl get svc dashboard -n marketpulse -w${NC}"
echo ""

# Show all resources
echo "📦 All Resources:"
kubectl get all -n marketpulse

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Useful commands:"
echo "  kubectl get pods -n marketpulse           # Check pod status"
echo "  kubectl logs -f deployment/dashboard -n marketpulse  # View logs"
echo "  kubectl describe pod <pod-name> -n marketpulse       # Debug issues"
echo ""
