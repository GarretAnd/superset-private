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
import pytest
from marshmallow.exceptions import ValidationError

from superset.cachekeys.schemas import CacheInvalidationRequestSchema, Datasource


def test_datasource_schema_valid_with_required_type() -> None:
    result = Datasource().load({"datasource_type": "table"})
    assert result["datasource_type"] == "table"


def test_datasource_schema_valid_with_all_fields() -> None:
    data = {
        "database_name": "my_db",
        "datasource_name": "my_table",
        "catalog": "my_catalog",
        "schema": "public",
        "datasource_type": "table",
    }
    result = Datasource().load(data)
    assert result["database_name"] == "my_db"
    assert result["datasource_name"] == "my_table"
    assert result["catalog"] == "my_catalog"
    assert result["schema"] == "public"
    assert result["datasource_type"] == "table"


def test_datasource_schema_allows_none_catalog() -> None:
    result = Datasource().load({"datasource_type": "table", "catalog": None})
    assert result["catalog"] is None


def test_datasource_schema_invalid_type() -> None:
    with pytest.raises(ValidationError):
        Datasource().load({"datasource_type": "invalid_type"})


def test_datasource_schema_missing_required_type() -> None:
    with pytest.raises(ValidationError):
        Datasource().load({"database_name": "my_db"})


def test_cache_invalidation_request_schema_with_uids() -> None:
    result = CacheInvalidationRequestSchema().load(
        {"datasource_uids": ["uid1", "uid2"]}
    )
    assert result["datasource_uids"] == ["uid1", "uid2"]


def test_cache_invalidation_request_schema_with_datasources() -> None:
    result = CacheInvalidationRequestSchema().load(
        {
            "datasources": [
                {"datasource_type": "table", "database_name": "my_db"},
            ]
        }
    )
    assert len(result["datasources"]) == 1
    assert result["datasources"][0]["datasource_type"] == "table"


def test_cache_invalidation_request_schema_empty() -> None:
    result = CacheInvalidationRequestSchema().load({})
    assert result == {}


def test_cache_invalidation_request_schema_with_both() -> None:
    result = CacheInvalidationRequestSchema().load(
        {
            "datasource_uids": ["uid1"],
            "datasources": [{"datasource_type": "table"}],
        }
    )
    assert result["datasource_uids"] == ["uid1"]
    assert len(result["datasources"]) == 1
