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
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from werkzeug.exceptions import Forbidden, NotFound

from superset.embedded.view import EmbeddedView


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config["GUEST_TOKEN_HEADER_NAME"] = "X-GuestToken"  # noqa: S105
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "test-secret"  # noqa: S105
    return app


def test_embedded_view_route_base() -> None:
    assert EmbeddedView.route_base == "/embedded"


@patch("superset.embedded.view.is_feature_enabled")
@patch("superset.embedded.view.EmbeddedDashboardDAO")
def test_embedded_view_404_when_feature_disabled(
    mock_dao: MagicMock, mock_feature: MagicMock, app: Flask
) -> None:
    mock_feature.return_value = False
    view = EmbeddedView()
    with app.test_request_context("/embedded/test-uuid"):
        with pytest.raises(NotFound):
            view.embedded("test-uuid")


@patch("superset.embedded.view.is_feature_enabled")
@patch("superset.embedded.view.EmbeddedDashboardDAO")
def test_embedded_view_404_when_dashboard_not_found(
    mock_dao: MagicMock, mock_feature: MagicMock, app: Flask
) -> None:
    mock_feature.return_value = True
    mock_dao.find_by_id.return_value = None
    view = EmbeddedView()
    with app.test_request_context("/embedded/test-uuid"):
        with pytest.raises(NotFound):
            view.embedded("test-uuid")


@patch("superset.embedded.view.is_feature_enabled")
@patch("superset.embedded.view.EmbeddedDashboardDAO")
def test_embedded_view_403_when_referrer_not_allowed(
    mock_dao: MagicMock, mock_feature: MagicMock, app: Flask
) -> None:
    mock_feature.return_value = True
    mock_embedded = MagicMock()
    mock_embedded.allowed_domains = ["https://allowed.example.com"]
    mock_embedded.dashboard_id = 1
    mock_dao.find_by_id.return_value = mock_embedded
    view = EmbeddedView()
    with app.test_request_context(
        "/embedded/test-uuid",
        headers={"Referer": "https://evil.example.com/page"},
    ):
        with pytest.raises(Forbidden):
            view.embedded("test-uuid")


@patch("superset.embedded.view.is_feature_enabled")
@patch("superset.embedded.view.EmbeddedDashboardDAO")
def test_embedded_view_403_on_invalid_sec_fetch_dest(
    mock_dao: MagicMock, mock_feature: MagicMock, app: Flask
) -> None:
    mock_feature.return_value = True
    mock_embedded = MagicMock()
    mock_embedded.allowed_domains = []
    mock_embedded.dashboard_id = 1
    mock_dao.find_by_id.return_value = mock_embedded
    view = EmbeddedView()
    with app.test_request_context(
        "/embedded/test-uuid",
        headers={"Sec-Fetch-Dest": "script"},
    ):
        with pytest.raises(Forbidden):
            view.embedded("test-uuid")
