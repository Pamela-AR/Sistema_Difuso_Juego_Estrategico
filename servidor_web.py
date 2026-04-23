# servidor_web.py

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from juego_difuso import ACCIONES_DISPONIBLES, crear_estado_inicial, resolver_turno


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "web"


class BattleRequestHandler(BaseHTTPRequestHandler):
    server_version = "PixelBattleHTTP/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/estado":
            self._send_json(
                {
                    "estado": crear_estado_inicial(),
                    "acciones": ACCIONES_DISPONIBLES,
                }
            )
            return

        if parsed.path == "/api/procesamiento":
            # Retorna datos de ejemplo del procesamiento difuso
            try:
                import json
                with open("estado_difuso.json", "r") as f:
                    datos = json.load(f)
                    self._send_json(datos)
                    return
            except (FileNotFoundError, json.JSONDecodeError):
                self._send_json({"error": "No hay datos de procesamiento disponibles"}, status=HTTPStatus.NOT_FOUND)
                return

        if parsed.path == "/" or parsed.path == "":
            self._serve_file("index.html")
            return

        self._serve_file(parsed.path.lstrip("/"))

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path != "/api/turno":
            self._send_json({"error": "Ruta no encontrada."}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            self._send_json({"error": "JSON inválido."}, status=HTTPStatus.BAD_REQUEST)
            return

        estado = payload.get("estado", {})
        accion = payload.get("accion")

        try:
            resultado = resolver_turno(estado, accion)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._send_json(resultado)

    def log_message(self, fmt, *args):
        print(f"[web] {self.address_string()} - {fmt % args}")

    def _serve_file(self, relative_path):
        safe_path = (STATIC_DIR / relative_path).resolve()

        if not str(safe_path).startswith(str(STATIC_DIR.resolve())):
            self._send_json({"error": "Acceso denegado."}, status=HTTPStatus.FORBIDDEN)
            return

        if not safe_path.exists() or not safe_path.is_file():
            self._send_json({"error": "Archivo no encontrado."}, status=HTTPStatus.NOT_FOUND)
            return

        content_type, _ = mimetypes.guess_type(str(safe_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(safe_path.read_bytes())

    def _send_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def run(host="127.0.0.1", port=8000):
    with ThreadingHTTPServer((host, port), BattleRequestHandler) as httpd:
        print(f"Servidor disponible en http://{host}:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    run()
