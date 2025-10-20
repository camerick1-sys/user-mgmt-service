from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from .db import SessionLocal
from .models import User
from .schemas import UserCreate, UserUpdate, UserRead
from .security import hash_password, verify_password
from .auth import create_token, require_auth

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/v1/users")

def to_read_model(user: User) -> dict:
    return UserRead(id=user.id, email=user.email, full_name=user.full_name).model_dump()

@user_bp.post("")
def create_user():
    """Create a user
    ---
    tags: [users]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email: {type: string}
              password: {type: string, minLength: 8}
              full_name: {type: string}
    responses:
      201:
        description: Created
      409:
        description: Email already exists
    """
    payload = request.get_json(force=True, silent=True) or {}
    try:
        data = UserCreate(**payload)
    except Exception as e:
        return jsonify({"error": "ValidationError", "detail": str(e)}), 400

    session = SessionLocal()
    try:
        u = User(email=data.email, full_name=data.full_name, password_hash=hash_password(data.password))
        session.add(u)
        session.commit()
        session.refresh(u)
        return jsonify(to_read_model(u)), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Conflict", "detail": "Email already exists"}), 409
    finally:
        session.close()

@user_bp.get("")
def list_users():
    """List users (paginated)
    ---
    tags: [users]
    parameters:
      - in: query
        name: limit
        schema: {type: integer, default: 50}
      - in: query
        name: offset
        schema: {type: integer, default: 0}
    responses:
      200:
        description: A list of users
    """
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
    except ValueError:
        return jsonify({"error": "BadRequest", "detail": "limit/offset must be integers"}), 400

    session = SessionLocal()
    try:
        q = session.execute(select(User).limit(limit).offset(offset)).scalars().all()
        return jsonify([to_read_model(u) for u in q]), 200
    finally:
        session.close()

@user_bp.get("/<int:user_id>")
def get_user(user_id: int):
    """Get a user by id
    ---
    tags: [users]
    responses:
      200:
        description: OK
      404:
        description: Not found
    """
    session = SessionLocal()
    try:
        u = session.get(User, user_id)
        if not u:
            return jsonify({"error": "NotFound"}), 404
        return jsonify(to_read_model(u)), 200
    finally:
        session.close()

@user_bp.patch("/<int:user_id>")
@require_auth
def update_user(user_id: int):
    """Update a user (auth required)
    ---
    tags: [users]
    security:
      - bearerAuth: []
    requestBody:
      required: true
    responses:
      200:
        description: Updated
      401:
        description: Unauthorized
      404:
        description: Not found
    """
    payload = request.get_json(force=True, silent=True) or {}
    try:
        data = UserUpdate(**payload)
    except Exception as e:
        return jsonify({"error": "ValidationError", "detail": str(e)}), 400

    session = SessionLocal()
    try:
        u = session.get(User, user_id)
        if not u:
            return jsonify({"error": "NotFound"}), 404
        if data.email is not None:
            u.email = data.email
        if data.full_name is not None:
            u.full_name = data.full_name
        if data.password is not None:
            u.password_hash = hash_password(data.password)
        session.commit()
        session.refresh(u)
        return jsonify(to_read_model(u)), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Conflict", "detail": "Email already exists"}), 409
    finally:
        session.close()

@user_bp.delete("/<int:user_id>")
@require_auth
def delete_user(user_id: int):
    """Delete a user (auth required)
    ---
    tags: [users]
    security:
      - bearerAuth: []
    responses:
      200:
        description: Deleted
      401:
        description: Unauthorized
      404:
        description: Not found
    """
    session = SessionLocal()
    try:
        u = session.get(User, user_id)
        if not u:
            return jsonify({"error": "NotFound"}), 404
        session.delete(u)
        session.commit()
        return jsonify({"status": "deleted"}), 200
    finally:
        session.close()

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

@auth_bp.post("/login")
def login():
    """Login to get JWT
    ---
    tags: [auth]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email: {type: string}
              password: {type: string}
    responses:
      200:
        description: JWT token
      401:
        description: Invalid credentials
    """
    payload = request.get_json(force=True, silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "BadRequest"}), 400

    session = SessionLocal()
    try:
        user = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Unauthorized", "detail": "Invalid credentials"}), 401
        token = create_token(user.id, user.email)
        return jsonify({"access_token": token, "token_type": "Bearer"}), 200
    finally:
        session.close()
