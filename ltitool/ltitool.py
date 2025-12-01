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

# Support voor zowel environment variabelen als Docker secrets
def get_secret(name):
    """Haal secret op van file of environment variabele"""
    secret_file = os.environ.get(f"{name}_FILE")
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()
    return os.environ.get(name, 'default-secret-CHANGE-ME')

app.secret_key = get_secret("SESSION_SECRET")
oauth_secret = get_secret("OAUTH_SECRET")

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

@app.route("/", methods=["GET", "POST"])
def first_learning_tool_step():
    if request.method == "GET":
        return render_template_string(
            """
            <!doctype html>
            <html>
            <head><title>LTI Tool</title></head>
            <body>
                <h1>LTI Tool is running!</h1>
                <p>This endpoint expects a POST request from Moodle LTI.</p>
            </body>
            </html>
            """
        )
    
    orig_state = "XSRF_session_bound_value_{r}".format(r=randint(0, 100000))
    session["xsrf_state"] = orig_state
    oauth_consumer_key = request.form.get("oauth_consumer_key", "")
    return_url = request.form.get("launch_presentation_return_url", "")
    
    app.logger.debug(f"Received LTI launch request")
    app.logger.debug(f"Consumer key: {oauth_consumer_key}")
    app.logger.debug(f"Return URL: {return_url}")
    
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

    if return_url:
        base_string = create_base_string(return_url, oauth_params)
        app.logger.debug(f"base_string is {base_string}")
        signature = create_signature(base_string, oauth_secret)
        oauth_params["oauth_signature"] = signature
        redirect_url = f"{return_url}&{urllib.parse.urlencode(oauth_params)}"
        app.logger.debug(f"redirect_url is {redirect_url}")
    
    return render_template_string(
        r"""
    <!doctype html>
    <html>
    <head>
        <title>LTI Tool - Hallo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }
            .info {
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="info">
            <h1>Hallo, LTI-app!</h1>
            <p><strong>User ID:</strong> {{ user_id }}</p>
            <p><strong>Roles:</strong> {{ roles }}</p>
            <p><strong>Context ID:</strong> {{ context_id }}</p>
            <p>Je hebt succesvol de LTI tool gelanceerd vanuit Moodle!</p>
        </div>
    </body>
    </html>
    """,
        user_id=request.form.get("user_id", "N/A"),
        roles=request.form.get("roles", "N/A"),
        context_id=request.form.get("context_id", "N/A")
    )

def create_base_string(base_url, params):
    sorted_params = sorted(params.items())
    encoded_params = urllib.parse.urlencode(sorted_params)
    return f"POST&{quote(base_url)}&{quote(encoded_params)}"

def create_signature(base_string, secret):
    key = f"{quote(secret)}&"
    hashed = hmac.new(key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode()

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)