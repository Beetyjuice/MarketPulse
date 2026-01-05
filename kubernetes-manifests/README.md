# Kubernetes Manifests for GKE Deployment

> **Deploy MarketPulse to Google Kubernetes Engine**

## 📋 Files Overview

| File | Purpose | Type |
|------|---------|------|
| `namespace.yaml` | Create marketpulse namespace | Namespace |
| `configmap.yaml` | Environment configuration | ConfigMap |
| `secrets.yaml.template` | Secrets template (API keys, passwords) | Secret |
| `kafka.yaml` | Kafka broker deployment | Deployment + Service |
| `zookeeper.yaml` | Zookeeper for Kafka | Deployment + Service |
| `cassandra.yaml` | Cassandra database | StatefulSet + Service |
| `redis.yaml` | Redis cache | Deployment + Service |
| `spark.yaml` | Spark streaming processor | Deployment |
| `dashboard.yaml` | Streamlit dashboard | Deployment + LoadBalancer |
| `stock-producer.yaml` | Stock data producer | Deployment |
| `news-producer.yaml` | News data producer | Deployment |
| `prediction-service.yaml` | ML prediction service | Deployment + Service |
| `monitoring.yaml` | Prometheus + Grafana | Deployment + Service |

## 🚀 Quick Deployment

### 1. Update Secrets

```bash
# Copy template
cp secrets.yaml.template secrets.yaml

# Edit with your actual secrets
nano secrets.yaml
```

### 2. Deploy All

```bash
# Deploy in order
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f zookeeper.yaml
kubectl apply -f kafka.yaml
kubectl apply -f cassandra.yaml
kubectl apply -f redis.yaml
kubectl apply -f spark.yaml
kubectl apply -f stock-producer.yaml
kubectl apply -f news-producer.yaml
kubectl apply -f prediction-service.yaml
kubectl apply -f dashboard.yaml
kubectl apply -f monitoring.yaml

# Or deploy all at once
kubectl apply -f .
```

### 3. Check Status

```bash
# Watch pods starting
kubectl get pods -n marketpulse -w

# Check all resources
kubectl get all -n marketpulse

# Get dashboard URL
kubectl get svc dashboard -n marketpulse
```

### 4. Access Dashboard

```bash
# Get external IP
export DASHBOARD_IP=$(kubectl get svc dashboard -n marketpulse -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Dashboard URL: http://$DASHBOARD_IP:8501"
```

## 📊 Resource Requirements

| Service | CPU | Memory | Disk | Replicas |
|---------|-----|--------|------|----------|
| Kafka | 1 | 2Gi | 10Gi | 1 |
| Zookeeper | 0.5 | 1Gi | 5Gi | 1 |
| Cassandra | 2 | 4Gi | 20Gi | 1 |
| Redis | 0.5 | 1Gi | - | 1 |
| Spark | 1 | 2Gi | - | 1 |
| Dashboard | 1 | 2Gi | - | 1 |
| Producers | 0.5 | 1Gi | - | 2 |
| Prediction | 1 | 2Gi | - | 1 |
| **Total** | **8.5** | **17Gi** | **35Gi** | **9** |

**Recommended Cluster:** 3 × n1-standard-4 nodes (4 vCPU, 15GB RAM each)

## 🔧 Customization

### Scale Replicas

```bash
# Scale dashboard
kubectl scale deployment dashboard -n marketpulse --replicas=3

# Scale Cassandra cluster
kubectl scale statefulset cassandra -n marketpulse --replicas=3
```

### Update Image

```bash
# Update dashboard image
kubectl set image deployment/dashboard \
    dashboard=gcr.io/PROJECT_ID/dashboard:v2 \
    -n marketpulse

# Rolling update automatically
```

### Change Resources

```bash
# Edit deployment
kubectl edit deployment dashboard -n marketpulse

# Change:
resources:
  requests:
    cpu: 2
    memory: 4Gi
```

## 📝 Deployment Order

**Important:** Deploy in this order to avoid dependency issues:

1. ✅ **namespace.yaml** - Create namespace
2. ✅ **configmap.yaml** - Configuration
3. ✅ **secrets.yaml** - Secrets
4. ✅ **zookeeper.yaml** - Kafka dependency
5. ✅ **kafka.yaml** - Message broker
6. ✅ **cassandra.yaml** - Database
7. ✅ **redis.yaml** - Cache
8. ✅ **spark.yaml** - Processor (needs Kafka + Cassandra)
9. ✅ **stock-producer.yaml** - Producer (needs Kafka)
10. ✅ **news-producer.yaml** - Producer (needs Kafka)
11. ✅ **prediction-service.yaml** - ML service
12. ✅ **dashboard.yaml** - Frontend (needs all above)
13. ✅ **monitoring.yaml** - Observability

## 🔒 Security Notes

- **secrets.yaml** is in `.gitignore` - never commit with real values
- Use `kubectl create secret` for production
- Enable RBAC for service accounts
- Use Network Policies to restrict traffic
- Enable Pod Security Policies

## 🆘 Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name> -n marketpulse
kubectl logs <pod-name> -n marketpulse
```

### Service not accessible

```bash
kubectl get svc -n marketpulse
kubectl describe svc dashboard -n marketpulse
```

### Delete and redeploy

```bash
kubectl delete -f dashboard.yaml
kubectl apply -f dashboard.yaml
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Helm Charts](https://helm.sh/) - Alternative deployment method
