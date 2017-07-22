# Import section
from functools import wraps
from flask import request, abort,session
import webapp.config.caconfig as config

# Functions
def process_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        # Checking JSON data within request
        data = request.get_json()
        if not data or data == None:
            abort(config.http_badrequest,{"message":config.error_bad_request}),
        return f(*args, **kwargs)
    return decorated_function