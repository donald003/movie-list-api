import atexit
import signal
import logging
import sys

from flask import Flask
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .config import Config
from .extensions import db, migrate, jwt, api

logger = logging.getLogger(__name__)


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

    from . import models  # pylint: disable=unused-import

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
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok", "database": "ok"}, 200
        except SQLAlchemyError:
            logger.exception("Health check failed: database unreachable")
            return {"status": "degraded", "database": "unavailable"}, 503

    
    def _shutdown(*_args):
        with app.app_context():
            db.session.remove()
            db.engine.dispose()

    def _handle_sigterm(*_args):
        _shutdown()
        sys.exit(0)

    atexit.register(_shutdown)
    signal.signal(signal.SIGTERM, _handle_sigterm)

    return app
