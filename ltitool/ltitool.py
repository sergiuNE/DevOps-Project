from flask import Flask, request, redirect, session, render_template_string
from logging.config import dictConfig
from random import randint
import os
import urllib.parse
import time
import hmac
import hashlib
import base64
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = os.environ["SESSION_SECRET"]

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)


@app.route("/", methods=["POST"])
def first_learning_tool_step():
    orig_state = "XSRF_session_bound_value_{r}".format(r=randint(0, 100000))
    session["xsrf_state"] = orig_state
    oauth_consumer_key = request.form["oauth_consumer_key"]
    return_url = request.form["launch_presentation_return_url"]
    oauth_params = {
        "lti_message_type": "basic-lti-launch-request",
        "lti_version": "LTI-1p0",
        "oauth_consumer_key": oauth_consumer_key,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": orig_state,
        "oauth_version": "1.0",
        "resource_link_id": request.form.get("resource_link_id", ""),
        "user_id": request.form.get("user_id", ""),
        "roles": request.form.get("roles", ""),
        "context_id": request.form.get("context_id", ""),
    }

    base_string = create_base_string(return_url, oauth_params)
    app.logger.debug(f"base_string is {base_string}")
    signature = create_signature(base_string, os.environ["OAUTH_SECRET"])
    oauth_params["oauth_signature"] = signature
    redirect_url = f"{return_url}&{urllib.parse.urlencode(oauth_params)}"
    app.logger.debug(f"redirect_url is {redirect_url}")
    return render_template_string(
        r"""
    <!doctype html>
   <head><link rel="stylesheet" href="{{ url_for('static', filename='roadmapstyle.css') }}"></link></head>
   <body>
    <h1>Hallo, LTI-app!</h1>
</body>"""
    )


def create_base_string(base_url, params):
    sorted_params = sorted(params.items())
    encoded_params = urllib.parse.urlencode(sorted_params)
    return f"POST&{quote(base_url)}&{quote(encoded_params)}"


def create_signature(base_string, secret):
    key = f"{quote(secret)}&"
    hashed = hmac.new(key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode()
