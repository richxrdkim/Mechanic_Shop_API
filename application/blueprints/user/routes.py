from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

from application.extensions import db, limiter
from application.models import User
from application.schemas import user_schema, users_schema
from application.util import token_required
from . import user_bp


# SIGNUP — allow POST to both /users/ and /users/signup (and /users/signup/)
@user_bp.route("/", methods=["POST"])
@user_bp.route("/signup", methods=["POST"])
@user_bp.route("/signup/", methods=["POST"])
@limiter.limit("10 per hour")
def signup():
    """
    ---
    tags: [Users]
    summary: Create a user
    description: Registers a user by name (optional), email, and password.
    parameters:
      - in: body
        name: payload
        schema: { $ref: '#/definitions/SignupPayload' }
        examples:
          application/json:
            name: Alice
            email: alice@example.com
            password: password123
    responses:
      201:
        description: Created
        schema: { $ref: '#/definitions/UserResponse' }
        examples:
          application/json: { "id": 1, "email": "alice@example.com" }
      400:
        description: Missing required fields
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "email and password are required" }
      409:
        description: Email already exists
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Email already exists" }
    """
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    u = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(u)
    db.session.commit()
    return user_schema.jsonify(u), 201


# LOGIN — accept /users/login and /users/login/
@user_bp.route("/login", methods=["POST"])
@user_bp.route("/login/", methods=["POST"])
@limiter.limit("50 per hour")
def login():
    """
    ---
    tags: [Users]
    summary: Log in
    description: Returns a JWT for subsequent authenticated requests.
    parameters:
      - in: body
        name: payload
        schema: { $ref: '#/definitions/LoginPayload' }
        examples:
          application/json:
            email: alice@example.com
            password: password123
    responses:
      200:
        description: OK
        schema: { $ref: '#/definitions/AuthResponse' }
        examples:
          application/json: { "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..." }
      400:
        description: Missing required fields
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "email and password required" }
      401:
        description: Unauthorized
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Invalid credentials" }
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "user_id": user.id,
        "role": "user",
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
    }
    token = jwt.encode(
        payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return jsonify({"token": token}), 200


# LIST (GET /users) — requires auth
@user_bp.route("/", methods=["GET"])
@token_required
def list_users(*, user_id, role):
    """
    ---
    tags: [Users]
    summary: List users (auth)
    description: Returns all users.
    security: [{Bearer: []}]
    responses:
      200:
        description: OK
        schema:
          type: array
          items: { $ref: '#/definitions/UserResponse' }
        examples:
          application/json:
            - { "id": 2, "email": "bob@example.com" }
            - { "id": 1, "email": "alice@example.com" }
      401:
        description: Unauthorized
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Unauthorized" }
    """
    users = User.query.order_by(User.id.desc()).all()
    return jsonify(users_schema.dump(users)), 200


# READ (GET /users/<id>) — requires auth
@user_bp.route("/<int:uid>", methods=["GET"])
@token_required
def get_user(uid, *, user_id, role):
    """
    ---
    tags: [Users]
    summary: Get user by id (auth)
    security: [{Bearer: []}]
    responses:
      200:
        description: OK
        schema: { $ref: '#/definitions/UserResponse' }
        examples:
          application/json: { "id": 1, "email": "alice@example.com" }
      401:
        description: Unauthorized
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Unauthorized" }
      404:
        description: Not found
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Not found" }
    """
    u = User.query.get_or_404(uid)
    return user_schema.jsonify(u), 200


# UPDATE (PUT /users/<id>) — requires auth
@user_bp.route("/<int:uid>", methods=["PUT"])
@token_required
def update_user(uid, *, user_id, role):
    """
    ---
    tags: [Users]
    summary: Update a user (auth)
    description: Currently supports updating the email.
    security: [{Bearer: []}]
    parameters:
      - in: body
        name: payload
        schema:
          type: object
          properties:
            email: { type: string, example: "new@example.com" }
        examples:
          application/json:
            email: new@example.com
    responses:
      200:
        description: Updated
        schema: { $ref: '#/definitions/UserResponse' }
        examples:
          application/json: { "id": 1, "email": "new@example.com" }
      401:
        description: Unauthorized
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Unauthorized" }
      404:
        description: Not found
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Not found" }
    """
    u = User.query.get_or_404(uid)
    data = request.get_json() or {}
    if "email" in data:
        u.email = data["email"]
    db.session.commit()
    return user_schema.jsonify(u), 200


# DELETE (DELETE /users/<id>) — requires auth
@user_bp.route("/<int:uid>", methods=["DELETE"])
@limiter.limit("10 per hour")
@token_required
def delete_user(uid, *, user_id, role):
    """
    ---
    tags: [Users]
    summary: Delete a user (auth)
    security: [{Bearer: []}]
    responses:
      200:
        description: Deleted
        schema:
          type: object
          properties:
            deleted: { type: integer, example: 3 }
        examples:
          application/json: { "deleted": 3 }
      401:
        description: Unauthorized
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Unauthorized" }
      404:
        description: Not found
        schema: { $ref: '#/definitions/ErrorResponse' }
        examples:
          application/json: { "error": "Not found" }
    """
    u = User.query.get_or_404(uid)
    db.session.delete(u)
    db.session.commit()
    return jsonify({"deleted": uid}), 200
