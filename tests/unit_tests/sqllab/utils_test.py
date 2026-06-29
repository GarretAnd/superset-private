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
import pyarrow as pa

from superset.common.db_query_status import QueryStatus
from superset.sqllab.utils import (
    apply_display_max_row_configuration_if_require,
    DATABASE_KEYS,
    write_ipc_buffer,
)


def test_apply_display_max_row_truncates_when_exceeds_limit() -> None:
    sql_results: dict[str, object] = {
        "status": QueryStatus.SUCCESS,
        "query": {"rows": 10},
        "data": list(range(10)),
    }
    result = apply_display_max_row_configuration_if_require(sql_results, 5)
    assert len(result["data"]) == 5
    assert result["displayLimitReached"] is True


def test_apply_display_max_row_no_truncation_when_within_limit() -> None:
    sql_results: dict[str, object] = {
        "status": QueryStatus.SUCCESS,
        "query": {"rows": 3},
        "data": list(range(3)),
    }
    result = apply_display_max_row_configuration_if_require(sql_results, 5)
    assert len(result["data"]) == 3
    assert "displayLimitReached" not in result


def test_apply_display_max_row_no_truncation_when_equal_limit() -> None:
    sql_results: dict[str, object] = {
        "status": QueryStatus.SUCCESS,
        "query": {"rows": 5},
        "data": list(range(5)),
    }
    result = apply_display_max_row_configuration_if_require(sql_results, 5)
    assert len(result["data"]) == 5
    assert "displayLimitReached" not in result


def test_apply_display_max_row_no_truncation_on_failed_status() -> None:
    sql_results: dict[str, object] = {
        "status": QueryStatus.FAILED,
        "query": {"rows": 10},
        "data": list(range(10)),
    }
    result = apply_display_max_row_configuration_if_require(sql_results, 5)
    assert len(result["data"]) == 10
    assert "displayLimitReached" not in result


def test_write_ipc_buffer_produces_valid_buffer() -> None:
    table = pa.table({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    buf = write_ipc_buffer(table)
    assert isinstance(buf, pa.Buffer)
    assert len(buf) > 0


def test_write_ipc_buffer_roundtrip() -> None:
    original = pa.table({"x": [10, 20], "y": [1.5, 2.5]})
    buf = write_ipc_buffer(original)
    reader = pa.ipc.open_stream(buf)
    restored = reader.read_all()
    assert restored.equals(original)


def test_database_keys_contains_expected_keys() -> None:
    assert "id" in DATABASE_KEYS
    assert "database_name" in DATABASE_KEYS
    assert "backend" in DATABASE_KEYS
    assert "allow_ctas" in DATABASE_KEYS
    assert "expose_in_sqllab" in DATABASE_KEYS
