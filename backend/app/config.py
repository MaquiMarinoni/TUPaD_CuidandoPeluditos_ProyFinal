
import os

import certifi
from sqlalchemy.engine import URL

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "clave-secreta-desarrollo-cuidando-peluditos"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'cuidandopeluditos_dev.db')}"
    )


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False

    @staticmethod
    def init_app(app):
        pass

    SQLALCHEMY_DATABASE_URI = (
        URL.create(
            drivername="mysql+pymysql",
            username=os.environ["TIDB_USER"],
            password=os.environ["TIDB_PASSWORD"],
            host=os.environ["TIDB_HOST"],
            port=4000,
            database=os.environ.get("TIDB_DATABASE", "cuidandopeluditos"),
            query={"charset": "utf8mb4"},
        )
        if all(os.environ.get(k) for k in
               ("TIDB_USER", "TIDB_PASSWORD", "TIDB_HOST"))
        else None
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "ssl_ca": certifi.where(),
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
            "connect_timeout": 15,
        },
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


config_by_name = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
