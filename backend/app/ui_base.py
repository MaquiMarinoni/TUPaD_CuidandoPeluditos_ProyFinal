"""Rutas HTML del prototipo. Separadas del API y del frontend definitivo."""
from pathlib import Path
from flask import Blueprint, render_template, send_from_directory

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
ui_bp = Blueprint("ui_base", __name__, template_folder=str(FRONTEND / "templates"))


@ui_bp.get("/")
@ui_bp.get("/demo")
def demo():
    return render_template("index.html")


@ui_bp.get("/demo-assets/<path:nombre>")
def demo_assets(nombre):
    return send_from_directory(FRONTEND / "statics", nombre)
