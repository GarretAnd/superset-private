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
from unittest.mock import MagicMock

import pytest

from superset.css_templates.filters import CssTemplateAllTextFilter


@pytest.fixture
def filter_instance() -> CssTemplateAllTextFilter:
    return CssTemplateAllTextFilter(datamodel=MagicMock(), column_name="template_name")


def test_css_template_all_text_filter_name() -> None:
    assert CssTemplateAllTextFilter.arg_name == "css_template_all_text"


def test_css_template_all_text_filter_returns_query_when_no_value(
    filter_instance: CssTemplateAllTextFilter,
) -> None:
    mock_query = MagicMock()
    result = filter_instance.apply(mock_query, "")
    assert result is mock_query


def test_css_template_all_text_filter_returns_query_when_none_value(
    filter_instance: CssTemplateAllTextFilter,
) -> None:
    mock_query = MagicMock()
    result = filter_instance.apply(mock_query, None)
    assert result is mock_query


def test_css_template_all_text_filter_applies_filter_with_value(
    filter_instance: CssTemplateAllTextFilter,
) -> None:
    mock_query = MagicMock()
    result = filter_instance.apply(mock_query, "test_search")
    mock_query.filter.assert_called_once()
    assert result is mock_query.filter.return_value
