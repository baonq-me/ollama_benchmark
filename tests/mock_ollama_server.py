"""Mock Ollama API server for testing benchmark functionality."""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional


class MockOllamaServer:
    """Mock Ollama server for testing."""

    def __init__(self, host: str = "127.0.0.1", port: int = 11999):
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._local_models: list[dict] = []
        self._lock = threading.Lock()

    def start(self):
        """Start the mock server in a background thread."""
        handler = self._create_handler()
        self._server = HTTPServer((self.host, self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the mock server."""
        if self._server:
            self._server.shutdown()
            self._server = None
            self._thread = None

    def _create_handler(self):
        """Create a request handler with access to this server instance."""
        server = self
        
        class MockHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress logging

            def do_GET(self):
                if self.path == "/api/tags":
                    self._handle_list_models()
                elif self.path == "/api/version":
                    self._handle_version()
                else:
                    self._send_error(404)

            def do_POST(self):
                if self.path == "/api/pull":
                    self._handle_pull()
                elif self.path == "/api/chat":
                    self._handle_chat()
                else:
                    self._send_error(404)

            def _handle_list_models(self):
                with server._lock:
                    models = server._local_models.copy()
                response = {"models": models}
                self._send_json(response)

            def _handle_pull(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                model_name = data.get("model", "unknown")
                stream = data.get("stream", True)

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

                    # Simulate pull progress
                    steps = [
                        {"status": "pulling manifest"},
                        {"status": "pulling layer 1/3", "digest": "sha256:abc123", "total": 1000000, "completed": 500000},
                        {"status": "pulling layer 1/3", "digest": "sha256:abc123", "total": 1000000, "completed": 1000000},
                        {"status": "pulling layer 2/3", "digest": "sha256:def456", "total": 2000000, "completed": 1000000},
                        {"status": "pulling layer 2/3", "digest": "sha256:def456", "total": 2000000, "completed": 2000000},
                        {"status": "pulling layer 3/3", "digest": "sha256:ghi789", "total": 500000, "completed": 500000},
                        {"status": "verifying sha256 digest"},
                        {"status": "writing manifest"},
                        {"status": "success"},
                    ]

                    for step in steps:
                        line = json.dumps(step) + "\n"
                        self.wfile.write(line.encode())
                    self.wfile.flush()

                    # Add model to local models list
                    with server._lock:
                        server._local_models.append({
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "modified_at": "2026-05-15T00:00:00Z",
                            "digest": "sha256:test123",
                        })
                else:
                    response = {"status": "success"}
                    self._send_json(response)

            def _handle_chat(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                stream = data.get("stream", True)
                gen_tokens = data.get("options", {}).get("num_predict", 256)

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

                    # Generate fake response tokens
                    for i in range(gen_tokens):
                        chunk = {
                            "model": data.get("model", "test-model"),
                            "message": {
                                "role": "assistant",
                                "content": f" token{i} ",
                            },
                            "done": False,
                        }
                        line = json.dumps(chunk) + "\n"
                        self.wfile.write(line.encode())

                    # Final chunk with stats
                    final_chunk = {
                        "model": data.get("model", "test-model"),
                        "message": {"role": "assistant", "content": ""},
                        "done": True,
                        "done_reason": "stop",
                        "prompt_eval_count": data.get("messages", [{}])[0].get("content", "").count(" ") + 10,
                        "prompt_eval_duration": 100000000,  # 100ms in ns
                        "eval_count": gen_tokens,
                        "eval_duration": gen_tokens * 10000000,  # ~10ms per token
                    }
                    line = json.dumps(final_chunk) + "\n"
                    self.wfile.write(line.encode())
                    self.wfile.flush()
                else:
                    response = {
                        "model": data.get("model", "test-model"),
                        "message": {
                            "role": "assistant",
                            "content": " ".join([f"token{i}" for i in range(gen_tokens)]),
                        },
                        "done": True,
                        "prompt_eval_count": 20,
                        "prompt_eval_duration": 100000000,
                        "eval_count": gen_tokens,
                        "eval_duration": gen_tokens * 10000000,
                    }
                    self._send_json(response)

            def _handle_version(self):
                response = {"version": "0.5.0"}
                self._send_json(response)

            def _send_json(self, data: dict):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def _send_error(self, status: int):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())

        return MockHandler

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def add_model(self, name: str, size: int = 3500000):
        """Manually add a model to the local models list."""
        with self._lock:
            self._local_models.append({
                "name": name,
                "model": name,
                "size": size,
                "modified_at": "2026-05-15T00:00:00Z",
                "digest": f"sha256:{hash(name) % 1000000:06d}",
            })

    def remove_model(self, name: str):
        """Remove a model from the local models list."""
        with self._lock:
            self._local_models = [m for m in self._local_models if m["name"] != name]

    def is_model_available(self, name: str) -> bool:
        """Check if a model is available locally."""
        with self._lock:
            return any(m["name"] == name for m in self._local_models)