from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    app.config["API_TITLE"] = "Movie List API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from . import models
    
    api.init_app(app)
    api.spec.components.security_scheme(
    "bearerAuth",
    {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
)
    
    from .routes.auth import auth_bp
    from .routes.movies import movies_bp
    api.register_blueprint(auth_bp)
    api.register_blueprint(movies_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app