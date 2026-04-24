# servidor_web.py

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from juego_difuso import ACCIONES_DISPONIBLES, crear_estado_inicial, resolver_turno


ROOT = Path(__file__).resolve().parent
# Directorio donde se sirven archivos estáticos (HTML, CSS, JS)
STATIC_DIR = ROOT / "web"


class BattleRequestHandler(BaseHTTPRequestHandler):
    # Manejador de peticiones HTTP para el juego de batalla
    server_version = "PixelBattleHTTP/1.0"

    def do_GET(self):
        # Procesa peticiones GET: cargar estado inicial o servir archivos estáticos
        parsed = urlparse(self.path)

        # Endpoint para obtener estado inicial del juego y lista de acciones disponibles
        if parsed.path == "/api/estado":
            self._send_json(
                {
                    "estado": crear_estado_inicial(),
                    "acciones": ACCIONES_DISPONIBLES,
                }
            )
            return

        # Si la ruta es raíz, sirve index.html
        if parsed.path == "/" or parsed.path == "":
            self._serve_file("index.html")
            return

        # Para cualquier otra ruta, sirve el archivo solicitado (CSS, JS, imágenes)
        self._serve_file(parsed.path.lstrip("/"))

    def do_POST(self):
        # Procesa peticiones POST: ejecuta un turno del juego
        parsed = urlparse(self.path)

        # Solo acepta peticiones al endpoint /api/turno
        if parsed.path != "/api/turno":
            self._send_json({"error": "Ruta no encontrada."}, status=HTTPStatus.NOT_FOUND)
            return

        # Lee y parsea el cuerpo JSON de la petición
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            self._send_json({"error": "JSON inválido."}, status=HTTPStatus.BAD_REQUEST)
            return

        # Extrae estado del juego y acción del jugador del payload
        estado = payload.get("estado", {})
        accion = payload.get("accion")

        # Procesa el turno con la lógica difusa
        try:
            resultado = resolver_turno(estado, accion)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        # Retorna el resultado del turno (nuevo estado, registro, animaciones)
        self._send_json(resultado)

    def log_message(self, fmt, *args):
        # Imprime mensajes de log con prefijo [web] para identificar origen
        print(f"[web] {self.address_string()} - {fmt % args}")

    def _serve_file(self, relative_path):
        # Sirve archivos estáticos con protección contra path traversal
        safe_path = (STATIC_DIR / relative_path).resolve()

        # Verifica que la ruta resuelve dentro de STATIC_DIR (previene acceso a archivos fuera)
        if not str(safe_path).startswith(str(STATIC_DIR.resolve())):
            self._send_json({"error": "Acceso denegado."}, status=HTTPStatus.FORBIDDEN)
            return

        # Verifica que el archivo existe y es un archivo regular
        if not safe_path.exists() or not safe_path.is_file():
            self._send_json({"error": "Archivo no encontrado."}, status=HTTPStatus.NOT_FOUND)
            return

        # Detecta el tipo MIME y envía el archivo con headers HTTP apropiados
        content_type, _ = mimetypes.guess_type(str(safe_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        # Lee y envía el contenido del archivo
        self.wfile.write(safe_path.read_bytes())

    def _send_json(self, payload, status=HTTPStatus.OK):
        # Serializa payload a JSON UTF-8 y lo envía con headers apropiados
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        # Envía el JSON como respuesta
        self.wfile.write(data)


def run(host="127.0.0.1", port=8000):
    # Inicia servidor HTTP multihilo que escucha en el host y puerto especificados
    with ThreadingHTTPServer((host, port), BattleRequestHandler) as httpd:
        print(f"Servidor disponible en http://{host}:{port}")
        # Mantiene el servidor activo indefinidamente
        httpd.serve_forever()


if __name__ == "__main__":
    run()
