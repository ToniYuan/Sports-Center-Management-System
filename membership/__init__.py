from flask import Blueprint

membership_bp = Blueprint('membership', __name__)

from membership import views