#authentication blueprint creation-----------------------------
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
#---------------------------------------------------------------

