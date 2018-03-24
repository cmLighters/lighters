from flask import Blueprint

inner_api = Blueprint('inner_api', __name__)

from . import views

