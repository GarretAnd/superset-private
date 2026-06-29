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

"""Tests that outbound HTTP requests include a timeout parameter."""

import importlib.util
import sys
from unittest.mock import MagicMock, patch


def test_verify_key_passes_timeout() -> None:
    """verify_key() must call requests.get with a timeout."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "some-key some-email@example.com"

    with patch("requests.get", return_value=mock_response) as mock_get:
        # Import inline so the module-level code doesn't need full env
        sys.modules.pop("RELEASING.verify_release", None)
        spec = importlib.util.spec_from_file_location(
            "verify_release",
            "RELEASING/verify_release.py",
        )
        assert spec is not None
        assert spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.verify_key("some-key", "some-email@example.com")

        mock_get.assert_called_once()
        _args, kwargs = mock_get.call_args
        assert "timeout" in kwargs, "requests.get must be called with a timeout"
        assert kwargs["timeout"] == 30
        assert "verified" in result.lower()


def test_generate_code_sample_includes_timeout() -> None:
    """Generated Python code samples must include timeout= in every request."""
    spec = importlib.util.spec_from_file_location(
        "fix_openapi_spec",
        "docs/scripts/fix-openapi-spec.py",
    )
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for method in ("get", "post", "put", "delete", "patch"):
        samples = mod.generate_code_sample(method, "/api/v1/chart/{pk}")
        python_samples = [s for s in samples if s["lang"] == "Python"]
        assert python_samples, f"No Python sample for {method}"
        source = python_samples[0]["source"]
        assert "timeout=" in source, (
            f"Python code sample for {method.upper()} must include timeout="
        )
