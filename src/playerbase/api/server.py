from __future__ import annotations

import json
import mimetypes
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from playerbase.core.authservice import LoginRequest, MockAuthService, RegisterRequest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def _auth_result_to_dict(result: Any) -> Dict[str, Any]:
    return {
        "user": {
            "user_id": result.user.user_id,
            "username": result.user.username,
            "display_name": result.user.display_name,
        },
        "tokens": {
            "access_token": result.tokens.access_token,
            "refresh_token": result.tokens.refresh_token,
            "token_type": result.tokens.token_type,
        },
    }


class PlayerbaseHandler(BaseHTTPRequestHandler):
    server_version = "PlayerbaseHTTP/0.1"

    def __init__(self, *args: Any, auth_service: MockAuthService, **kwargs: Any) -> None:
        self.auth_service = auth_service
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send_json(HTTPStatus.OK, {"ok": True})
            return

        if self.path == "/api/me":
            token = self._extract_bearer_token()
            if not token:
                self._send_json(
                    HTTPStatus.UNAUTHORIZED,
                    {"error": "Missing Bearer token."},
                )
                return

            try:
                user = self.auth_service.get_current_user(token)
            except ValueError as exc:
                self._send_json(HTTPStatus.UNAUTHORIZED, {"error": str(exc)})
                return

            self._send_json(
                HTTPStatus.OK,
                {
                    "user": {
                        "user_id": user.user_id,
                        "username": user.username,
                        "display_name": user.display_name,
                    }
                },
            )
            return

        self._serve_frontend_asset()

    def do_POST(self) -> None:
        if self.path == "/api/register":
            payload = self._read_json_body()
            if payload is None:
                return

            username = (payload.get("username") or "").strip()
            password = payload.get("password") or ""
            email = (payload.get("email") or "").strip() or None
            if not username or not password:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": "username and password are required."},
                )
                return

            try:
                result = self.auth_service.register(
                    RegisterRequest(username=username, password=password, email=email)
                )
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            self._send_json(HTTPStatus.CREATED, _auth_result_to_dict(result))
            return

        if self.path == "/api/login":
            payload = self._read_json_body()
            if payload is None:
                return

            username = (payload.get("username") or "").strip()
            password = payload.get("password") or ""
            if not username or not password:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": "username and password are required."},
                )
                return

            try:
                result = self.auth_service.login(
                    LoginRequest(username=username, password=password)
                )
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            self._send_json(HTTPStatus.OK, _auth_result_to_dict(result))
            return

        if self.path == "/api/logout":
            token = self._extract_bearer_token()
            if not token:
                self._send_json(
                    HTTPStatus.UNAUTHORIZED,
                    {"error": "Missing Bearer token."},
                )
                return

            try:
                self.auth_service.logout(token)
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            self._send_json(HTTPStatus.OK, {"ok": True})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _extract_bearer_token(self) -> Optional[str]:
        header = self.headers.get("Authorization", "")
        prefix = "Bearer "
        if header.startswith(prefix):
            return header[len(prefix) :].strip()
        return None

    def _read_json_body(self) -> Optional[Dict[str, Any]]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Invalid Content-Length header."},
            )
            return None

        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON body."})
            return None

    def _send_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_frontend_asset(self) -> None:
        relative_path = self.path.lstrip("/") or "index.html"
        asset_path = (FRONTEND_DIR / relative_path).resolve()

        if not str(asset_path).startswith(str(FRONTEND_DIR.resolve())):
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "Forbidden."})
            return

        if asset_path.is_dir():
            asset_path = asset_path / "index.html"

        if not asset_path.exists() or not asset_path.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return

        content_type, _ = mimetypes.guess_type(str(asset_path))
        file_bytes = asset_path.read_bytes()

        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-Type",
            f"{content_type or 'application/octet-stream'}; charset=utf-8",
        )
        self.send_header("Content-Length", str(len(file_bytes)))
        self.end_headers()
        self.wfile.write(file_bytes)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    auth_service = MockAuthService()
    handler = partial(PlayerbaseHandler, auth_service=auth_service)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving playerbase on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
