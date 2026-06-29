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

from superset.sqllab.schemas import (
    EstimateQueryCostSchema,
    ExecutePayloadSchema,
    FormatQueryPayloadSchema,
    sql_lab_get_results_schema,
    tmp_table_name_validator,
)


def test_sql_lab_get_results_schema_structure() -> None:
    assert sql_lab_get_results_schema["type"] == "object"
    assert "key" in sql_lab_get_results_schema["properties"]
    assert sql_lab_get_results_schema["required"] == ["key"]


def test_estimate_query_cost_schema_valid() -> None:
    result = EstimateQueryCostSchema().load({"database_id": 1, "sql": "SELECT 1"})
    assert result["database_id"] == 1
    assert result["sql"] == "SELECT 1"


def test_estimate_query_cost_schema_with_optional_fields() -> None:
    result = EstimateQueryCostSchema().load(
        {
            "database_id": 1,
            "sql": "SELECT 1",
            "template_params": {"param1": "value1"},
            "catalog": "my_catalog",
            "schema": "public",
        }
    )
    assert result["template_params"] == {"param1": "value1"}
    assert result["catalog"] == "my_catalog"
    assert result["schema"] == "public"


def test_estimate_query_cost_schema_missing_database_id() -> None:
    with pytest.raises(ValidationError):
        EstimateQueryCostSchema().load({"sql": "SELECT 1"})


def test_estimate_query_cost_schema_missing_sql() -> None:
    with pytest.raises(ValidationError):
        EstimateQueryCostSchema().load({"database_id": 1})


def test_format_query_payload_schema_valid_minimal() -> None:
    result = FormatQueryPayloadSchema().load({"sql": "SELECT 1"})
    assert result["sql"] == "SELECT 1"


def test_format_query_payload_schema_with_engine() -> None:
    result = FormatQueryPayloadSchema().load(
        {"sql": "SELECT 1", "engine": "postgresql"}
    )
    assert result["engine"] == "postgresql"


def test_format_query_payload_schema_with_database_id() -> None:
    result = FormatQueryPayloadSchema().load({"sql": "SELECT 1", "database_id": 5})
    assert result["database_id"] == 5


def test_format_query_payload_schema_missing_sql() -> None:
    with pytest.raises(ValidationError):
        FormatQueryPayloadSchema().load({"engine": "postgresql"})


def test_execute_payload_schema_valid_minimal() -> None:
    result = ExecutePayloadSchema().load({"database_id": 1, "sql": "SELECT 1"})
    assert result["database_id"] == 1
    assert result["sql"] == "SELECT 1"


def test_execute_payload_schema_with_all_fields() -> None:
    result = ExecutePayloadSchema().load(
        {
            "database_id": 1,
            "sql": "SELECT 1",
            "client_id": "abc123",
            "queryLimit": 100,
            "sql_editor_id": "editor1",
            "catalog": "my_catalog",
            "schema": "public",
            "tab": "tab1",
            "ctas_method": "TABLE",
            "templateParams": '{"p": 1}',
            "tmp_table_name": "my_tmp_table",
            "select_as_cta": True,
            "runAsync": False,
            "expand_data": True,
        }
    )
    assert result["client_id"] == "abc123"
    assert result["queryLimit"] == 100
    assert result["tmp_table_name"] == "my_tmp_table"
    assert result["select_as_cta"] is True
    assert result["runAsync"] is False


def test_execute_payload_schema_missing_database_id() -> None:
    with pytest.raises(ValidationError):
        ExecutePayloadSchema().load({"sql": "SELECT 1"})


def test_execute_payload_schema_missing_sql() -> None:
    with pytest.raises(ValidationError):
        ExecutePayloadSchema().load({"database_id": 1})


def test_tmp_table_name_validator_valid_names() -> None:
    assert tmp_table_name_validator("my_table") == "my_table"
    assert tmp_table_name_validator("_leading_underscore") == "_leading_underscore"
    assert tmp_table_name_validator("Table123") == "Table123"
    assert tmp_table_name_validator("a") == "a"


def test_tmp_table_name_validator_empty_string() -> None:
    assert tmp_table_name_validator("") == ""


def test_tmp_table_name_validator_invalid_names() -> None:
    with pytest.raises(ValidationError):
        tmp_table_name_validator("123starts_with_digit")
    with pytest.raises(ValidationError):
        tmp_table_name_validator("has spaces")
    with pytest.raises(ValidationError):
        tmp_table_name_validator("has-dashes")
    with pytest.raises(ValidationError):
        tmp_table_name_validator("has.dots")
