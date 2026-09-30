from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from .routes.movies import movies_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from . import models
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)


    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app