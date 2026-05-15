"""Mock Ollama API server for testing benchmark functionality."""

import json
import re
import threading
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional


class MockOllamaServer:
    """Mock Ollama server for testing."""

    def __init__(self, host: str = "127.0.0.1", port: int = 11999):
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._local_models: dict[str, dict] = {}  # model_name -> model_info
        self._running_models: dict[str, dict] = {}  # model_name -> running_info
        self._blobs: dict[str, dict] = {}  # digest -> blob_info
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
                path = self.path.split("?")[0]  # Remove query params
                if path == "/api/tags":
                    self._handle_list_models()
                elif path == "/api/version":
                    self._handle_version()
                elif path == "/api/ps":
                    self._handle_list_running()
                elif path == "/api/blobs/sha256:" + self._get_digest_from_path():
                    self._handle_head_blob()
                else:
                    self._send_error(404, "Not found")

            def do_POST(self):
                path = self.path.split("?")[0]  # Remove query params
                if path == "/api/pull":
                    self._handle_pull()
                elif path == "/api/chat":
                    self._handle_chat()
                elif path == "/api/generate":
                    self._handle_generate()
                elif path == "/api/create":
                    self._handle_create()
                elif path == "/api/show":
                    self._handle_show()
                elif path == "/api/copy":
                    self._handle_copy()
                elif path == "/api/push":
                    self._handle_push()
                elif path == "/api/embed":
                    self._handle_embed()
                elif path == "/api/embeddings":
                    self._handle_embeddings_legacy()
                elif path == "/api/blobs/sha256:" + self._get_digest_from_path():
                    self._handle_post_blob()
                else:
                    self._send_error(404, "Not found")

            def do_DELETE(self):
                path = self.path.split("?")[0]  # Remove query params
                if path == "/api/delete":
                    self._handle_delete()
                else:
                    self._send_error(404, "Not found")

            def do_HEAD(self):
                path = self.path.split("?")[0]  # Remove query params
                if path.startswith("/api/blobs/sha256:"):
                    self._handle_head_blob()
                else:
                    self._send_error(404, "Not found")

            def _get_digest_from_path(self) -> str:
                """Extract digest from path like /api/blobs/sha256:abc123"""
                match = re.search(r"/api/blobs/sha256:([a-f0-9]+)", self.path)
                return match.group(1) if match else ""

            def _read_body(self) -> dict:
                """Read and parse JSON body."""
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                return json.loads(body) if body else {}

            def _handle_list_models(self):
                """GET /api/tags - List local models."""
                with server._lock:
                    models = list(server._local_models.values())
                response = {"models": models}
                self._send_json(response)

            def _handle_version(self):
                """GET /api/version - Get Ollama version."""
                response = {"version": "0.5.0"}
                self._send_json(response)

            def _handle_list_running(self):
                """GET /api/ps - List running models."""
                with server._lock:
                    running = list(server._running_models.values())
                response = {"models": running}
                self._send_json(response)

            def _handle_head_blob(self):
                """HEAD /api/blobs/:digest - Check if blob exists."""
                digest = self._get_digest_from_path()
                with server._lock:
                    exists = digest in server._blobs
                if exists:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", len(digest))
                    self.end_headers()
                else:
                    self._send_error(404, "Blob not found")

            def _handle_post_blob(self):
                """POST /api/blobs/:digest - Push a blob."""
                digest = self._get_digest_from_path()
                content_length = int(self.headers.get("Content-Length", 0))
                
                # Simulate blob upload
                with server._lock:
                    server._blobs[digest] = {
                        "digest": digest,
                        "size": content_length,
                        "created_at": "2026-05-15T00:00:00Z"
                    }
                
                response = {"status": "success", "digest": digest}
                self._send_json(response)

            def _handle_pull(self):
                """POST /api/pull - Pull a model."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                stream = data.get("stream", True)

                # Determine model details
                model_details = {
                    "format": "gguf",
                    "family": "llama",
                    "families": ["llama"],
                    "parameter_size": "7.6B",
                    "quantization_level": "Q4_K_M",
                }

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

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

                    # Add model to local models
                    with server._lock:
                        server._local_models[model_name] = {
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "modified_at": "2026-05-15T00:00:00Z",
                            "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                            "details": model_details,
                        }
                else:
                    # Add model to local models
                    with server._lock:
                        server._local_models[model_name] = {
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "modified_at": "2026-05-15T00:00:00Z",
                            "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                            "details": model_details,
                        }
                    response = {"status": "success"}
                    self._send_json(response)

            def _handle_generate(self):
                """POST /api/generate - Generate a completion."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                prompt = data.get("prompt", "")
                suffix = data.get("suffix", "")
                stream = data.get("stream", True)
                num_predict = data.get("options", {}).get("num_predict", 256)
                keep_alive = data.get("keep_alive", "5m")
                images = data.get("images", [])

                # Check if model is loaded for keep_alive tracking
                is_load_request = prompt == "" and keep_alive == 0
                is_unload_request = prompt == "" and keep_alive == 0

                if is_unload_request:
                    # Unload model
                    with server._lock:
                        if model_name in server._running_models:
                            del server._running_models[model_name]
                    
                    response = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "response": "",
                        "done": True,
                        "done_reason": "unload",
                    }
                    self._send_json(response)
                    return

                if is_load_request:
                    # Load model
                    with server._lock:
                        if model_name not in server._local_models:
                            server._local_models[model_name] = {
                                "name": model_name,
                                "model": model_name,
                                "size": 3500000,
                                "modified_at": "2026-05-15T00:00:00Z",
                                "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                                "details": {
                                    "format": "gguf",
                                    "family": "llama",
                                    "families": ["llama"],
                                    "parameter_size": "7.6B",
                                    "quantization_level": "Q4_K_M",
                                },
                            }
                        server._running_models[model_name] = {
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                            "details": {
                                "format": "gguf",
                                "family": "llama",
                                "families": ["llama"],
                                "parameter_size": "7.6B",
                                "quantization_level": "Q4_K_M",
                            },
                            "expires_at": "2026-05-15T01:00:00Z",
                            "size_vram": 3500000,
                        }
                    
                    response = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "response": "",
                        "done": True,
                    }
                    self._send_json(response)
                    return

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

                    # Generate fake response tokens
                    response_text = ""
                    for i in range(num_predict):
                        token = f" token{i} "
                        response_text += token
                        chunk = {
                            "model": model_name,
                            "created_at": "2026-05-15T00:00:00Z",
                            "response": token,
                            "done": False,
                        }
                        line = json.dumps(chunk) + "\n"
                        self.wfile.write(line.encode())

                    # Final chunk with stats
                    final_chunk = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "response": "",
                        "done": True,
                        "done_reason": "stop",
                        "context": [1, 2, 3, 4, 5],
                        "total_duration": 5000000000,
                        "load_duration": 1000000000,
                        "prompt_eval_count": len(prompt.split()),
                        "prompt_eval_duration": 100000000,
                        "eval_count": num_predict,
                        "eval_duration": num_predict * 10000000,
                    }
                    if suffix:
                        final_chunk["response"] = response_text + suffix
                    line = json.dumps(final_chunk) + "\n"
                    self.wfile.write(line.encode())
                    self.wfile.flush()
                else:
                    # Non-streaming response
                    response_text = " ".join([f"token{i}" for i in range(num_predict)])
                    if suffix:
                        response_text += suffix
                    
                    response = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "response": response_text,
                        "done": True,
                        "done_reason": "stop",
                        "context": [1, 2, 3, 4, 5],
                        "total_duration": 5000000000,
                        "load_duration": 1000000000,
                        "prompt_eval_count": len(prompt.split()),
                        "prompt_eval_duration": 100000000,
                        "eval_count": num_predict,
                        "eval_duration": num_predict * 10000000,
                    }
                    self._send_json(response)

            def _handle_chat(self):
                """POST /api/chat - Generate a chat completion."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                messages = data.get("messages", [])
                tools = data.get("tools", [])
                stream = data.get("stream", True)
                num_predict = data.get("options", {}).get("num_predict", 256)
                keep_alive = data.get("keep_alive", "5m")
                format_type = data.get("format", "json")

                # Handle empty messages (load/unload)
                is_load_request = len(messages) == 0 and keep_alive != 0
                is_unload_request = len(messages) == 0 and keep_alive == 0

                if is_unload_request:
                    with server._lock:
                        if model_name in server._running_models:
                            del server._running_models[model_name]
                    
                    response = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "message": {"role": "assistant", "content": ""},
                        "done": True,
                        "done_reason": "unload",
                    }
                    self._send_json(response)
                    return

                if is_load_request:
                    with server._lock:
                        if model_name not in server._local_models:
                            server._local_models[model_name] = {
                                "name": model_name,
                                "model": model_name,
                                "size": 3500000,
                                "modified_at": "2026-05-15T00:00:00Z",
                                "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                                "details": {
                                    "format": "gguf",
                                    "family": "llama",
                                    "families": ["llama"],
                                    "parameter_size": "7.6B",
                                    "quantization_level": "Q4_K_M",
                                },
                            }
                        server._running_models[model_name] = {
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                            "details": {
                                "format": "gguf",
                                "family": "llama",
                                "families": ["llama"],
                                "parameter_size": "7.6B",
                                "quantization_level": "Q4_K_M",
                            },
                            "expires_at": "2026-05-15T01:00:00Z",
                            "size_vram": 3500000,
                        }
                    
                    response = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "message": {"role": "assistant", "content": ""},
                        "done": True,
                        "done_reason": "load",
                    }
                    self._send_json(response)
                    return

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

                    # Generate fake response tokens
                    message_content = ""
                    for i in range(num_predict):
                        token = f" token{i} "
                        message_content += token
                        chunk = {
                            "model": model_name,
                            "created_at": "2026-05-15T00:00:00Z",
                            "message": {
                                "role": "assistant",
                                "content": token,
                                "images": None,
                            },
                            "done": False,
                        }
                        
                        # Add tool_calls if tools are provided
                        if tools:
                            chunk["message"]["tool_calls"] = [
                                {
                                    "function": {
                                        "name": tools[0]["function"]["name"],
                                        "arguments": {"city": "Tokyo"}
                                    }
                                }
                            ]
                        
                        line = json.dumps(chunk) + "\n"
                        self.wfile.write(line.encode())

                    # Final chunk with stats
                    final_chunk = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "message": {"role": "assistant", "content": ""},
                        "done": True,
                        "done_reason": "stop",
                        "total_duration": 5000000000,
                        "load_duration": 1000000000,
                        "prompt_eval_count": len(messages),
                        "prompt_eval_duration": 100000000,
                        "eval_count": num_predict,
                        "eval_duration": num_predict * 10000000,
                    }
                    line = json.dumps(final_chunk) + "\n"
                    self.wfile.write(line.encode())
                    self.wfile.flush()
                else:
                    # Non-streaming response
                    message_content = " ".join([f"token{i}" for i in range(num_predict)])
                    
                    response = {
                        "model": model_name,
                        "created_at": "2026-05-15T00:00:00Z",
                        "message": {
                            "role": "assistant",
                            "content": message_content,
                            "images": None,
                        },
                        "done": True,
                        "done_reason": "stop",
                        "total_duration": 5000000000,
                        "load_duration": 1000000000,
                        "prompt_eval_count": len(messages),
                        "prompt_eval_duration": 100000000,
                        "eval_count": num_predict,
                        "eval_duration": num_predict * 10000000,
                    }
                    
                    # Add tool_calls if tools are provided
                    if tools:
                        response["message"]["tool_calls"] = [
                            {
                                "function": {
                                    "name": tools[0]["function"]["name"],
                                    "arguments": {"city": "Tokyo"}
                                }
                            }
                        ]
                    
                    self._send_json(response)

            def _handle_create(self):
                """POST /api/create - Create a model."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                from_model = data.get("from", "")
                files = data.get("files", {})
                stream = data.get("status", True)
                quantize = data.get("quantize", "")

                # Default status updates
                statuses = []
                if from_model:
                    statuses = [
                        {"status": "reading model metadata"},
                        {"status": f"copying layer from {from_model}"},
                        {"status": "writing manifest"},
                        {"status": "success"},
                    ]
                elif quantize:
                    statuses = [
                        {"status": f"quantizing F16 model to {quantize}", "digest": "0", "total": 6433687776, "completed": 12302},
                        {"status": f"quantizing F16 model to {quantize}", "digest": "0", "total": 6433687776, "completed": 6433687552},
                        {"status": "verifying conversion"},
                        {"status": "writing manifest"},
                        {"status": "success"},
                    ]
                elif files:
                    statuses = [
                        {"status": "parsing GGUF"},
                        {"status": f"using existing layer {list(files.keys())[0]}"},
                        {"status": "writing manifest"},
                        {"status": "success"},
                    ]
                else:
                    statuses = [
                        {"status": "creating model"},
                        {"status": "writing manifest"},
                        {"status": "success"},
                    ]

                # Add model to local models
                model_details = {
                    "format": "gguf",
                    "family": "llama",
                    "families": ["llama"],
                    "parameter_size": "7.6B",
                    "quantization_level": "Q4_K_M",
                }

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

                    for status in statuses:
                        line = json.dumps(status) + "\n"
                        self.wfile.write(line.encode())
                    self.wfile.flush()
                else:
                    with server._lock:
                        server._local_models[model_name] = {
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "modified_at": "2026-05-15T00:00:00Z",
                            "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                            "details": model_details,
                        }
                    response = {"status": "success"}
                    self._send_json(response)

            def _handle_show(self):
                """POST /api/show - Show model information."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                verbose = data.get("verbose", False)

                with server._lock:
                    if model_name in server._local_models:
                        model = server._local_models[model_name]
                    else:
                        model = {
                            "name": model_name,
                            "model": model_name,
                            "size": 3500000,
                            "modified_at": "2026-05-15T00:00:00Z",
                            "digest": f"sha256:{hash(model_name) % 1000000:06d}",
                            "details": {
                                "parent_model": "",
                                "format": "gguf",
                                "family": "llama",
                                "families": ["llama"],
                                "parameter_size": "7.6B",
                                "quantization_level": "Q4_K_M",
                            },
                        }

                response = {
                    "modelfile": f"FROM {model_name}\nPARAMETER temperature 0.8",
                    "parameters": "temperature 0.8\nnum_ctx 4096",
                    "template": "{{ .Prompt }}",
                    "details": model["details"],
                    "model_info": {
                        "general.architecture": "llama",
                        "general.file_type": 2,
                        "general.parameter_count": 7600000000,
                        "general.quantization_version": 2,
                        "llama.attention.head_count": 32,
                        "llama.attention.head_count_kv": 8,
                        "llama.block_count": 32,
                        "llama.context_length": 8192,
                        "llama.embedding_length": 4096,
                        "llama.vocab_size": 128256,
                    },
                    "capabilities": ["completion", "chat"],
                }

                if verbose:
                    response["model_info"]["tokenizer.ggml.tokens"] = ["<s>", "</s>", "<unk>"]
                    response["model_info"]["tokenizer.ggml.merges"] = ["a b", "c d"]
                    response["model_info"]["tokenizer.ggml.token_type"] = [0, 0, 0]

                self._send_json(response)

            def _handle_copy(self):
                """POST /api/copy - Copy a model."""
                data = self._read_body()
                source = data.get("source", "")
                destination = data.get("destination", "")

                with server._lock:
                    if source in server._local_models:
                        source_model = server._local_models[source]
                        server._local_models[destination] = {
                            "name": destination,
                            "model": destination,
                            "size": source_model.get("size", 3500000),
                            "modified_at": "2026-05-15T00:00:00Z",
                            "digest": f"sha256:{hash(destination) % 1000000:06d}",
                            "details": source_model.get("details", {
                                "format": "gguf",
                                "family": "llama",
                                "families": ["llama"],
                                "parameter_size": "7.6B",
                                "quantization_level": "Q4_K_M",
                            }),
                        }
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "success"}).encode())
                    else:
                        self._send_error(404, f"Source model '{source}' not found")

            def _handle_delete(self):
                """DELETE /api/delete - Delete a model."""
                data = self._read_body()
                model_name = data.get("model", "")

                with server._lock:
                    if model_name in server._local_models:
                        del server._local_models[model_name]
                        # Also remove from running if present
                        if model_name in server._running_models:
                            del server._running_models[model_name]
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "success"}).encode())
                    else:
                        self._send_error(404, f"Model '{model_name}' not found")

            def _handle_push(self):
                """POST /api/push - Push a model."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                stream = data.get("stream", True)

                statuses = [
                    {"status": "retrieving manifest"},
                    {"status": "starting upload", "digest": f"sha256:{hash(model_name) % 1000000:06d}", "total": 1928429856},
                    {"status": "pushing manifest"},
                    {"status": "success"},
                ]

                if stream:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.end_headers()

                    for status in statuses:
                        line = json.dumps(status) + "\n"
                        self.wfile.write(line.encode())
                    self.wfile.flush()
                else:
                    response = {"status": "success"}
                    self._send_json(response)

            def _handle_embed(self):
                """POST /api/embed - Generate embeddings."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                inputs = data.get("input", "")
                dimensions = data.get("dimensions", 384)

                # Handle single input (string) or multiple inputs (list)
                if isinstance(inputs, str):
                    input_list = [inputs]
                else:
                    input_list = list(inputs)

                # Generate mock embeddings
                embeddings = []
                for inp in input_list:
                    # Create deterministic but realistic-looking embeddings
                    seed = hash(inp) % 1000
                    embedding = [
                        round(((seed + i * 17) % 1000) / 1000.0 - 0.5, 7)
                        for i in range(dimensions)
                    ]
                    embeddings.append(embedding)

                response = {
                    "model": model_name,
                    "embeddings": embeddings,
                    "total_duration": 14143917,
                    "load_duration": 1019500,
                    "prompt_eval_count": sum(len(inp.split()) for inp in input_list),
                }
                self._send_json(response)

            def _handle_embeddings_legacy(self):
                """POST /api/embeddings - Legacy embeddings endpoint."""
                data = self._read_body()
                model_name = data.get("model", "unknown")
                prompt = data.get("prompt", "")

                # Generate single embedding vector (legacy format returns single vector, not array)
                seed = hash(prompt) % 1000
                embedding = [
                    round(((seed + i * 17) % 1000) / 1000.0 - 0.5, 7)
                    for i in range(384)
                ]

                response = {
                    "model": model_name,
                    "embedding": embedding,
                    "load_duration": 1019500,
                    "prompt_eval_count": len(prompt.split()),
                }
                self._send_json(response)

            def _send_json(self, data: dict):
                """Send JSON response."""
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def _send_error(self, status: int, message: str = "Not found"):
                """Send error response."""
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": message}).encode())

        return MockHandler

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def add_model(self, name: str, size: int = 3500000, details: Optional[dict] = None):
        """Manually add a model to the local models list."""
        model_details = details or {
            "parent_model": "",
            "format": "gguf",
            "family": "llama",
            "families": ["llama"],
            "parameter_size": "7.6B",
            "quantization_level": "Q4_K_M",
        }
        with self._lock:
            self._local_models[name] = {
                "name": name,
                "model": name,
                "size": size,
                "modified_at": "2026-05-15T00:00:00Z",
                "digest": f"sha256:{hash(name) % 1000000:06d}",
                "details": model_details,
            }

    def remove_model(self, name: str):
        """Remove a model from the local models list."""
        with self._lock:
            if name in self._local_models:
                del self._local_models[name]
            if name in self._running_models:
                del self._running_models[name]

    def is_model_available(self, name: str) -> bool:
        """Check if a model is available locally."""
        with self._lock:
            return name in self._local_models

    def is_model_running(self, name: str) -> bool:
        """Check if a model is currently loaded in memory."""
        with self._lock:
            return name in self._running_models

    def add_blob(self, digest: str, size: int = 1000000):
        """Manually add a blob to the blob storage."""
        with self._lock:
            self._blobs[digest] = {
                "digest": digest,
                "size": size,
                "created_at": "2026-05-15T00:00:00Z"
            }

    def blob_exists(self, digest: str) -> bool:
        """Check if a blob exists."""
        with self._lock:
            return digest in self._blobs