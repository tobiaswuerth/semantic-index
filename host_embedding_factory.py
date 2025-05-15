from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import traceback

from semantic_index import GTEEmbeddingModel


embedding_model: GTEEmbeddingModel = GTEEmbeddingModel()


class EmbeddingFactoryRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(message).encode())

    def _send_error(self, code, message):
        self._send_response(code, {"error": message})

    def do_POST(self):
        try:
            if self.path != "/generate_embedding":
                return self._send_error(404, "Endpoint not found")

            content_type = self.headers.get("Content-Type", "")
            if content_type != "application/json":
                return self._send_error(400, "Content-Type must be application/json")

            # Parse JSON body
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                return self._send_error(400, "Invalid JSON format")

            batch = data.get("batch", "")
            if not batch:
                return self._send_error(400, "Missing 'batch' field in JSON")

            embeddings = embedding_model._encode_batch(batch)
            return self._send_response(200, embeddings.tolist())
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
            return self._send_error(500, "Internal Server Error")


def run_server():
    host = "0.0.0.0"
    port = 8000
    httpd = HTTPServer((host, port), EmbeddingFactoryRequestHandler)
    print(f"Starting embedding server at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
