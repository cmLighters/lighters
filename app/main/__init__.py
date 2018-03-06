from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)


import errors, views


# add Permission to app context, then we can use it in template environment
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
