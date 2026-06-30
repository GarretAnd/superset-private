# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Regression tests for B113 (requests without timeout) in the alerts/reports
notification layer.  These tests verify that every outbound HTTP call path
carries a configurable timeout so that hung targets cannot block workers
indefinitely.
"""

import ast
import pathlib
from unittest.mock import MagicMock, patch

import pytest

NOTIFICATIONS_DIR = (
    pathlib.Path(__file__).resolve().parents[4]
    / "superset"
    / "reports"
    / "notifications"
)


def test_no_requests_call_without_timeout_kwarg() -> None:
    """
    Static regression guard: scan every .py file under
    superset/reports/notifications/ and assert that every call to
    requests.post / requests.get / requests.put / requests.delete /
    requests.patch includes a `timeout` keyword argument.

    This mirrors the Bandit B113 check but runs as a fast unit test so CI
    catches regressions without needing a full Bandit invocation.
    """
    violations: list[str] = []
    request_methods = {"get", "post", "put", "delete", "patch", "head", "options"}

    for py_file in NOTIFICATIONS_DIR.glob("*.py"):
        source = py_file.read_text()
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Match requests.<method>(...) calls
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr in request_methods
                and isinstance(func.value, ast.Name)
                and func.value.id == "requests"
            ):
                kwarg_names = {kw.arg for kw in node.keywords}
                if "timeout" not in kwarg_names:
                    violations.append(
                        f"{py_file.name}:{node.lineno} - "
                        f"requests.{func.attr}() missing timeout"
                    )

    assert not violations, (
        "Found requests calls without timeout (B113 violation):\n"
        + "\n".join(violations)
    )


def test_slack_client_receives_configured_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that get_slack_client() passes SLACK_API_TIMEOUT from app config
    to the WebClient constructor, preventing indefinite hangs on Slack API calls.
    """
    mock_app = MagicMock()
    mock_app.config = {
        "SLACK_API_TOKEN": "xoxb-test-token",
        "SLACK_PROXY": None,
        "SLACK_API_TIMEOUT": 45,
        "SLACK_API_RATE_LIMIT_RETRY_COUNT": 2,
    }

    with (
        patch("superset.utils.slack.app", mock_app),
        patch("superset.utils.slack.WebClient") as mock_web_client,
    ):
        mock_web_client.return_value.retry_handlers = []

        from superset.utils.slack import get_slack_client

        get_slack_client()

        mock_web_client.assert_called_once_with(
            token="xoxb-test-token",  # noqa: S106
            proxy=None,
            timeout=45,
        )


def test_slack_client_callable_token_with_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    When SLACK_API_TOKEN is a callable, verify timeout is still forwarded.
    """
    mock_app = MagicMock()
    mock_app.config = {
        "SLACK_API_TOKEN": lambda: "xoxb-dynamic-token",
        "SLACK_PROXY": "http://proxy:8080",
        "SLACK_API_TIMEOUT": 120,
        "SLACK_API_RATE_LIMIT_RETRY_COUNT": 3,
    }

    with (
        patch("superset.utils.slack.app", mock_app),
        patch("superset.utils.slack.WebClient") as mock_web_client,
    ):
        mock_web_client.return_value.retry_handlers = []

        from superset.utils.slack import get_slack_client

        get_slack_client()

        mock_web_client.assert_called_once_with(
            token="xoxb-dynamic-token",  # noqa: S106
            proxy="http://proxy:8080",
            timeout=120,
        )


def test_smtp_timeout_forwarded_to_smtplib(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify that send_mime_email passes SMTP_TIMEOUT from config to the
    smtplib.SMTP / SMTP_SSL constructor, preventing indefinite hangs when
    the mail server is unreachable.
    """
    config = {
        "SMTP_HOST": "mail.example.com",
        "SMTP_PORT": 587,
        "SMTP_USER": "user",
        "SMTP_PASSWORD": "pass",
        "SMTP_STARTTLS": True,
        "SMTP_SSL": False,
        "SMTP_SSL_SERVER_AUTH": False,
        "SMTP_TIMEOUT": 42,
    }

    with patch("superset.utils.core.smtplib.SMTP") as mock_smtp:
        mock_instance = MagicMock()
        mock_smtp.return_value = mock_instance
        mock_instance.starttls.return_value = None
        mock_instance.login.return_value = None
        mock_instance.sendmail.return_value = {}
        mock_instance.quit.return_value = None

        from email.mime.multipart import MIMEMultipart

        from superset.utils.core import send_mime_email

        msg = MIMEMultipart()
        msg["Subject"] = "Test"
        msg["From"] = "from@example.com"
        msg["To"] = "to@example.com"

        send_mime_email("from@example.com", ["to@example.com"], msg, config)

        mock_smtp.assert_called_once_with("mail.example.com", 587, timeout=42)


def test_smtp_ssl_timeout_forwarded(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Same as above but for the SMTP_SSL path.
    """
    config = {
        "SMTP_HOST": "mail.example.com",
        "SMTP_PORT": 465,
        "SMTP_USER": "user",
        "SMTP_PASSWORD": "pass",
        "SMTP_STARTTLS": False,
        "SMTP_SSL": True,
        "SMTP_SSL_SERVER_AUTH": True,
        "SMTP_TIMEOUT": 55,
    }

    with (
        patch("superset.utils.core.smtplib.SMTP_SSL") as mock_smtp_ssl,
        patch("superset.utils.core.ssl.create_default_context") as mock_ssl_ctx,
    ):
        mock_instance = MagicMock()
        mock_smtp_ssl.return_value = mock_instance
        mock_instance.login.return_value = None
        mock_instance.sendmail.return_value = {}
        mock_instance.quit.return_value = None

        from email.mime.multipart import MIMEMultipart

        from superset.utils.core import send_mime_email

        msg = MIMEMultipart()
        msg["Subject"] = "Test"
        msg["From"] = "from@example.com"
        msg["To"] = "to@example.com"

        send_mime_email("from@example.com", ["to@example.com"], msg, config)

        mock_smtp_ssl.assert_called_once_with(
            "mail.example.com",
            465,
            context=mock_ssl_ctx.return_value,
            timeout=55,
        )
