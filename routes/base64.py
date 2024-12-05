import base64
from flask import Blueprint

template_filter_blueprint = Blueprint('base64', __name__)

def b64encode_filter(img):
    """Codifica uma imagem em Base64."""
    if img:
        return base64.b64encode(img).decode('utf-8')
    return None

# Registra o filtro no Blueprint
template_filter_blueprint.app_template_filter('b64encode')(b64encode_filter)