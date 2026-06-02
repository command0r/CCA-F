"""Minimal Flask user-management API with in-memory storage."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from flask import Flask, abort, jsonify, request


@dataclass(frozen=True)
class User:
    id: int
    email: str
    name: str
    roles: list[str] = field(default_factory=list)


_users: dict[int, User] = {
    1: User(1, "ada@example.com", "Ada Lovelace", ["admin"]),
    2: User(2, "alan@example.com", "Alan Turing", ["editor"]),
}
_next_id = 3


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/healthz")
    def healthz() -> tuple[Any, int]:
        return jsonify({"status": "ok"}), 200

    @app.get("/users")
    def list_users() -> tuple[Any, int]:
        return jsonify([asdict(u) for u in _users.values()]), 200

    @app.get("/users/<int:user_id>")
    def get_user(user_id: int) -> tuple[Any, int]:
        user = _users.get(user_id)
        if user is None:
            abort(404)
        return jsonify(asdict(user)), 200

    @app.post("/users")
    def create_user() -> tuple[Any, int]:
        global _next_id
        payload = request.get_json(silent=True) or {}
        email = payload.get("email")
        name = payload.get("name")
        if not email or not name:
            abort(400, description="email and name are required")
        user = User(id=_next_id, email=email, name=name, roles=payload.get("roles", []))
        _users[_next_id] = user
        _next_id += 1
        return jsonify(asdict(user)), 201

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
