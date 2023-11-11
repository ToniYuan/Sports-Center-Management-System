from flask import Blueprint

web_app_bp = Blueprint('web_app', __name__,
                       template_folder='templates',
                       static_folder='static',
                       static_url_path='/web_app/static')

from web_app import views