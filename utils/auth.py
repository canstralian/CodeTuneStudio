# SPDX-License-Identifier: MIT
"""
Streamlit authentication gate using streamlit-authenticator.

Environment variables:
  AUTH_ENABLED            — set "false" to bypass auth entirely (e.g. local dev)
  AUTH_USERNAME           — comma-separated usernames (default: "admin")
  AUTH_PASSWORD_HASH      — comma-separated bcrypt hashes, one per username
  AUTH_NAME               — comma-separated display names, one per username
  AUTH_COOKIE_NAME        — session cookie name (default: "codetune_auth")
  AUTH_COOKIE_KEY         — cookie signing key — CHANGE IN PRODUCTION
  AUTH_COOKIE_EXPIRY_DAYS — session lifetime in days (default: "1")

Usage:
    from utils.auth import require_auth

    def run(self) -> None:
        if not require_auth():
            return
        # ... rest of app
"""

import logging
import os

logger = logging.getLogger(__name__)

_AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "true").lower() != "false"

_DEFAULT_COOKIE_KEY = "change-me-in-production"


def _build_credentials() -> dict:
    """Parse env vars into the credential dict expected by streamlit-authenticator."""
    usernames = [
        u.strip()
        for u in os.environ.get("AUTH_USERNAME", "admin").split(",")
        if u.strip()
    ]
    hashes = [
        h.strip()
        for h in os.environ.get("AUTH_PASSWORD_HASH", "").split(",")
        if h.strip()
    ]
    names = [
        n.strip()
        for n in os.environ.get("AUTH_NAME", "").split(",")
        if n.strip()
    ]

    if not hashes:
        logger.warning(
            "AUTH_PASSWORD_HASH is not set — authentication will block all logins. "
            "Generate a hash: python -c \"import bcrypt; "
            "print(bcrypt.hashpw(b'password', bcrypt.gensalt()).decode())\""
        )

    credentials: dict = {"usernames": {}}
    for i, username in enumerate(usernames):
        credentials["usernames"][username] = {
            "name": names[i] if i < len(names) else username.capitalize(),
            "password": hashes[i] if i < len(hashes) else "",
            "email": f"{username}@placeholder.local",
        }
    return credentials


def require_auth() -> bool:
    """
    Render the login gate and return True only when the user is authenticated.

    Call at the top of the Streamlit app's run() method and return early if False.
    """
    if not _AUTH_ENABLED:
        return True

    try:
        import streamlit as st  # noqa: PLC0415
        import streamlit_authenticator as stauth  # noqa: PLC0415

        cookie_name = os.environ.get("AUTH_COOKIE_NAME", "codetune_auth")
        cookie_key = os.environ.get("AUTH_COOKIE_KEY", _DEFAULT_COOKIE_KEY)
        cookie_expiry = int(os.environ.get("AUTH_COOKIE_EXPIRY_DAYS", "1"))

        if cookie_key == _DEFAULT_COOKIE_KEY:
            logger.warning(
                "AUTH_COOKIE_KEY is using the default value. "
                "Set AUTH_COOKIE_KEY to a secret value in production "
                "to prevent session-cookie forgery."
            )

        credentials = _build_credentials()
        authenticator = stauth.Authenticate(
            credentials,
            cookie_name,
            cookie_key,
            cookie_expiry,
        )

        # streamlit-authenticator >=0.3.0: login() takes location as first arg
        name, authentication_status, _username = authenticator.login(location="main")

        if authentication_status is False:
            st.error("Incorrect username or password.")
            return False
        if authentication_status is None:
            st.warning("Please enter your username and password.")
            return False

        # Authenticated — add logout button and identity indicator
        authenticator.logout("Logout", "sidebar")
        st.sidebar.write(f"Logged in as **{name}**")
        return True

    except ImportError:
        import streamlit as st  # noqa: PLC0415

        st.error(
            "Authentication library not installed. "
            "Run: pip install 'streamlit-authenticator>=0.3.0' bcrypt"
        )
        logger.error("streamlit-authenticator not installed; access blocked")
        return False
    except Exception:
        import streamlit as st  # noqa: PLC0415

        logger.exception("Authentication error")
        st.error("Authentication failed unexpectedly. Please reload the page.")
        return False
