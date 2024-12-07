from flask import Blueprint

new_app1_bp = Blueprint('new_app1', __name__)

@new_app1_bp.route('/new_app1')
def new_app1_route():
    return "This is a route from new_app1"

def init_app(app):
    app.register_blueprint(new_app1_bp)