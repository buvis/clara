# Kubernetes Deployment

## Required Secrets

Set these environment variables before deploying:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | FastAPI secret key for signing tokens/cookies |
| `DB_PASSWORD` | PostgreSQL password for the `clara` user |

## Deploy with envsubst

```bash
export SECRET_KEY="your-secret-key"
export DB_PASSWORD="your-db-password"

# Apply all manifests with secret substitution
for f in secret.yml configmap.yml; do
  envsubst < "k8s/$f" | kubectl apply -f -
done

# Apply remaining manifests (no substitution needed)
kubectl apply -f k8s/postgres.yml
kubectl apply -f k8s/redis.yml
kubectl apply -f k8s/backend.yml
kubectl apply -f k8s/worker.yml
```

## Generate secrets

```bash
export SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -hex 16)
```
