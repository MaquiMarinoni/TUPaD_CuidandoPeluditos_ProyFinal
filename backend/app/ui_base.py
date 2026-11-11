"""Rutas HTML del prototipo. Separadas del API y del frontend definitivo."""
from pathlib import Path
from flask import Blueprint, send_from_directory

ui_bp = Blueprint("ui_base", __name__)
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


@ui_bp.get("/demo")
def demo():
    return send_from_directory(FRONTEND / "templates", "index.html")


@ui_bp.get("/demo-assets/<path:nombre>")
def demo_assets(nombre):
    return send_from_directory(FRONTEND / "statics", nombre)