from flask import Flask, jsonify
from flasgger import Swagger
from .routes import user_bp, auth_bp
from .db import init_db

swagger_template = {
    "swagger": "2.0",
    "info": {"title": "User Management API", "version": "1.0.0"},
    "securityDefinitions": {
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Format: Bearer <token>"
        }
    }
}

def create_app():
    app = Flask(__name__)
    Swagger(app, template=swagger_template)
    init_db()
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
