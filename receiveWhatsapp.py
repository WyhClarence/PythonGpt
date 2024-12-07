from flask import Blueprint
from app import logger

new_app1_bp = Blueprint('new_app1', __name__)

@new_app1_bp.route('/receiveMsg', methods=['POST'])
def new_app1_route(json):
    logger.debug(f"receiveMsg: {json}")

def init_app(app):
    app.register_blueprint(new_app1_bp)
