"""Flask main file"""
import os
import time
import jwt

from flask import Flask
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from jwt.exceptions import InvalidTokenError
from jwt import PyJWKClient

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("APP_SECRET_KEY")

auth0_domain = os.environ.get("AUTH0_DOMAIN")
auth0_client_id = os.environ.get("AUTH0_CLIENT_ID")
auth0_client_secret = os.environ.get("AUTH0_CLIENT_SECRET")

url = f"https://{auth0_domain}/.well-known/jwks.json"

jwks_client = PyJWKClient(url)


def validate_access_token(access_token, client_id):
    """Validate given access token"""
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)

        decoded_token = jwt.decode(
            access_token,
            key=signing_key.key,
            algorithms=["RS256"],
            issuer=f"https://{auth0_domain}/",
            audience=client_id,
        )

        # Check claims and expiration here
        # For example, checking if the token is expired
        if decoded_token["exp"] < int(time.time()):
            return None  # Token is expired

        # You can perform additional checks here if needed

        return decoded_token
    except InvalidTokenError as e:
        print(f"Error decoding token: {e}")
        return None  # Token is invalid


# Auth0 configuration
oauth = OAuth(app)
oauth.register(
    name="auth0",
    client_id=auth0_client_id,
    client_secret=auth0_client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{auth0_domain}/.well-known/openid-configuration",
)


@app.route("/login")
def login():
    """Login route"""
    return oauth.auth0.authorize_redirect(redirect_uri="http://localhost:5000/callback")


@app.route("/callback", methods=["GET", "POST"])
def callback():
    """Callback route"""
    token = oauth.auth0.authorize_access_token()
    # Store user information in the session or your database as needed
    print(token)
    decoded_token = validate_access_token(token["id_token"], auth0_client_id)
    print(decoded_token)
    return decoded_token


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
