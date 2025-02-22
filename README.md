# Deploy Ollama on Fly.io or k8s

> (Definitely did not create this to prepare for an interview.)

This project demonstrates how to deploy Ollama (a local LLM server) on Fly.io using a two-app architecture:

1. `flying-ollama-model`: Runs the Ollama server
2. `flying-ollama`: A Flask web service that communicates with the Ollama server

On k8s, the names are `kollama` instead of `flying-ollama`

## Architecture

- The model service (`flying-ollama-model`) runs the Ollama server
- The web service (`flying-ollama`) is a lightweight Flask app that forwards requests to the model service
- Communication between services uses Fly.io's internal networking via Flycast

## Local Development

Run with Docker Compose:
   ```bash
   docker compose up --build
   ```

This will start both the Ollama server and the Flask server locally.

## Fly.io Deployment

### CI/CD Setup

The project uses GitHub Actions for continuous deployment. On every push to the master branch, it will:
1. Deploy the Ollama model service first
2. Once the model is deployed, deploy the web service

To set this up:

1. Create deploy tokens for both services:
   ```bash
   # For the model service
   fly tokens create deploy -x 999999h --config fly.model.toml
   # For the web service
   fly tokens create deploy -x 999999h --config fly.toml
   ```

2. Add the tokens as GitHub secrets:
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables > Actions
   - Create two secrets:
     - `FLY_DEPLOY_TOKEN_MODEL` for the model service
     - `FLY_API_TOKEN` for the web service

The deployments will now run automatically on every push to master.

## Kubernetes Deployment

To deploy the services on Kubernetes:

1. Create the resources:
   ```bash
   kubectl apply -f k8s
   ```

1. Get the external IP of the web service:
   ```bash
   kubectl get service kollama-web-service
   ```

1. Tear everything down.
   ```bash
   kubectl delete -f k8s
   ```

The web service is exposed via LoadBalancer, while the model service remains internal to the cluster.

## Usage
Example chat request:

```bash
curl -X POST https://your-app-name.fly.dev/chat \
  -H "Content-Type: text/plain" \
  -d "What is the meaning of life?"
```
