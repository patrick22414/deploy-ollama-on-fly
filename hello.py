import logging
import logging.config
import os

import flask
import requests
from flask import Flask, jsonify, request

# Dictionary for logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://model:11434")
print(f"Using Ollama at {OLLAMA_URL}")

MODEL = "llama3.2:1b"


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        DEBUG=os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    )

    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)

    # Middleware: log each incoming request
    @app.before_request
    def log_request():
        app.logger.info("Request: %s %s", request.method, request.url)

    # Start pulling model
    try:
        response = requests.post(f"{OLLAMA_URL}/api/pull", json={"model": MODEL})
        response.raise_for_status()
    except requests.RequestException as ex:
        app.logger.error(f"Error pulling model {MODEL} with Ollama: {ex}")
    else:
        app.logger.info(f"Success pulled {MODEL}: {response.elapsed.total_seconds()}s")

    @app.route("/")
    def index():
        return "Ollama is running on fly.io"

    @app.route("/echo", methods=["POST"])
    def echo():
        data = request.get_json()
        return jsonify(data)

    @app.route("/chat", methods=["POST"])
    def chat():
        text = request.get_data(as_text=True)

        payload = {
            "model": MODEL,
            "prompt": text + " (be very brief)",
            "stream": False,
        }

        # Send the request to the model container.
        try:
            response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()

        except requests.RequestException as ex:
            app.logger.error("Error communicating with Ollama: %s", ex)
            return jsonify({"error": "Failed to communicate with model service"}), 500

        try:
            answer = response.json()["response"] + "\n"
        except Exception as ex:
            app.logger.error("Error parsing response from Ollama: %s", ex)
            return (
                jsonify({"error": "Failed to parse response from model service"}),
                500,
            )

        return flask.Response(answer, mimetype="text/plain")

    return app


app = create_app()

if __name__ == "__main__":
    app.run()
