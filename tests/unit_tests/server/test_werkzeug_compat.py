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
Smoke tests for Werkzeug / Flask version compatibility.

Werkzeug must be pinned to a range that is compatible with the installed
Flask version.  These tests verify that the pin declared in
``pyproject.toml`` and ``requirements/base.in`` keeps the two packages in
a known-good state, and that the WSGI app object can be created without
import errors.
"""

from __future__ import annotations

from importlib.metadata import version as pkg_version

from packaging.version import Version


def test_werkzeug_version_in_pinned_range() -> None:
    """Installed Werkzeug falls within the declared >=3.1.6, <4.0.0 range."""
    wz_version = Version(pkg_version("werkzeug"))
    assert wz_version >= Version("3.1.6"), (
        f"Werkzeug {wz_version} is below the minimum pinned version 3.1.6"
    )
    assert wz_version < Version("4.0.0"), (
        f"Werkzeug {wz_version} exceeds the pinned upper bound <4.0.0"
    )


def test_flask_werkzeug_import_compatibility() -> None:
    """Flask can import its Werkzeug internals without errors."""
    from flask import Flask

    app = Flask(__name__)
    assert app.test_client() is not None


def test_werkzeug_pin_in_pyproject() -> None:
    """``pyproject.toml`` declares a bounded Werkzeug dependency."""
    from pathlib import Path

    import tomllib

    pyproject = Path(__file__).resolve().parents[3] / "pyproject.toml"
    with open(pyproject, "rb") as fh:
        data = tomllib.load(fh)

    deps: list[str] = data["project"]["dependencies"]
    werkzeug_deps = [d for d in deps if d.lower().startswith("werkzeug")]
    assert len(werkzeug_deps) == 1, (
        f"Expected exactly one werkzeug entry in pyproject.toml dependencies, "
        f"found: {werkzeug_deps}"
    )
    dep = werkzeug_deps[0]
    assert "<" in dep, (
        f"Werkzeug dependency must have an upper bound to prevent "
        f"Flask-incompatible majors: {dep}"
    )
