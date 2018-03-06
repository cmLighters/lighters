from flask_login import current_user
from flask import abort
from functools import wraps
from .models import Permission


def permission_require(permission):
    def func(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return func


def admin_require(f):
    return permission_require(Permission.ADMIN)(f)