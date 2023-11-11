from flask import Blueprint

book_bp = Blueprint('booking', __name__)

from booking import views