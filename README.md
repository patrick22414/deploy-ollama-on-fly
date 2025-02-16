# Deploy Ollama on Fly.io

> (Definitely did not create this to prepare for an interview.)

This project demonstrates how to deploy Ollama (a local LLM server) on Fly.io using a two-app architecture:

1. `flying-ollama-model`: Runs the Ollama server
2. `flying-ollama`: A Flask web service that communicates with the Ollama server

## Architecture

- The model service (`flying-ollama-model`) runs the Ollama server with 4 CPUs and 4GB RAM
- The web service (`flying-ollama`) is a lightweight Flask app that forwards requests to the model service
- Communication between services uses Fly.io's internal networking via Flycast

## Deployment

### Prerequisites

1. Install the [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Log in to Fly.io: `fly auth login`

### Manual Deployment

#### Deploy the Model Service

```bash
fly launch --config fly.model.toml
fly volumes create ollama_models --size 2
fly deploy --config fly.model.toml
```

#### Deploy the Web Service

```bash
fly launch
fly deploy
```

### CI/CD Setup

The project uses GitHub Actions for continuous deployment. On every push to the main branch, it will:
1. Deploy the Ollama model service first
2. Once the model is deployed, deploy the web service

To set this up:

1. Get your Fly.io API token:
   ```bash
   fly tokens create deploy -x 999999h
   ```

2. Add the token as a GitHub secret:
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables > Actions
   - Create a new secret named `FLY_API_TOKEN` with your token

The deployments will now run automatically on every push to main.

## Usage
Example chat request:

```bash
curl -X POST https://your-app-name.fly.dev/chat \
  -H "Content-Type: text/plain" \
  -d "What is the meaning of life?"
```

## Local Development

Run with Docker Compose:
   ```bash
   docker compose up --build
   ```

This will start both the Ollama server and the Flask server locally.
