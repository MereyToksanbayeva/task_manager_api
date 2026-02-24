import os
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from database import db
from models import User, Task


def create_app() -> Flask:
    app = Flask(__name__)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-me-in-production")

    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # -------- Auth --------
    @app.post("/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400
        if len(password) < 6:
            return jsonify({"error": "password must be at least 6 characters"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "user already exists"}), 409

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "registered successfully"}), 201

    @app.post("/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid credentials"}), 401

        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token}), 200

    # -------- Tasks (Protected) --------
    @app.get("/tasks")
    @jwt_required()
    def list_tasks():
        user_id = int(get_jwt_identity())
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
        return jsonify([serialize_task(t) for t in tasks]), 200

    @app.post("/tasks")
    @jwt_required()
    def create_task():
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip() or None

        if not title:
            return jsonify({"error": "title is required"}), 400

        task = Task(title=title, description=description, user_id=user_id)
        db.session.add(task)
        db.session.commit()

        return jsonify(serialize_task(task)), 201

    @app.get("/tasks/<int:task_id>")
    @jwt_required()
    def get_task(task_id: int):
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({"error": "task not found"}), 404
        return jsonify(serialize_task(task)), 200

    @app.put("/tasks/<int:task_id>")
    @jwt_required()
    def update_task(task_id: int):
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({"error": "task not found"}), 404

        data = request.get_json(silent=True) or {}

        if "title" in data:
            title = (data.get("title") or "").strip()
            if not title:
                return jsonify({"error": "title cannot be empty"}), 400
            task.title = title

        if "description" in data:
            desc = (data.get("description") or "").strip()
            task.description = desc or None

        if "is_done" in data:
            task.is_done = bool(data.get("is_done"))

        db.session.commit()
        return jsonify(serialize_task(task)), 200

    @app.delete("/tasks/<int:task_id>")
    @jwt_required()
    def delete_task(task_id: int):
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({"error": "task not found"}), 404

        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "deleted"}), 200

    return app


def serialize_task(t: Task) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "is_done": t.is_done,
        "created_at": t.created_at.isoformat() + "Z",
        "updated_at": t.updated_at.isoformat() + "Z",
    }


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
