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
"""Verify that command run() methods raise ValueError instead of AssertionError
when the model/models attribute is not populated after validate().

These tests cover the B101 remediation: bare ``assert`` statements used for
runtime validation in the API command layer have been replaced with explicit
``if not ...: raise ValueError(...)`` guards.
"""

import pytest


def test_delete_chart_command_raises_value_error(mocker):
    """DeleteChartCommand.run() raises ValueError when _models is not set."""
    from superset.commands.chart.delete import DeleteChartCommand

    cmd = DeleteChartCommand([1])
    mocker.patch.object(cmd, "validate")  # no-op validate
    # _models remains None after validate
    with pytest.raises(ValueError, match="Charts not found"):
        cmd.run()


def test_update_chart_command_raises_value_error(mocker):
    """UpdateChartCommand.run() raises ValueError when _model is not set."""
    from superset.commands.chart.update import UpdateChartCommand

    cmd = UpdateChartCommand(1, {})
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Chart not found"):
        cmd.run()


def test_delete_dashboard_command_raises_value_error(mocker):
    """DeleteDashboardCommand.run() raises ValueError when _models is not set."""
    from superset.commands.dashboard.delete import DeleteDashboardCommand

    cmd = DeleteDashboardCommand([1])
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Dashboards not found"):
        cmd.run()


def test_update_dashboard_command_raises_value_error(mocker):
    """UpdateDashboardCommand.run() raises ValueError when _model is not set."""
    from superset.commands.dashboard.update import UpdateDashboardCommand

    cmd = UpdateDashboardCommand(1, {})
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Dashboard not found"):
        cmd.run()


def test_delete_dataset_command_raises_value_error(mocker):
    """DeleteDatasetCommand.run() raises ValueError when _models is not set."""
    from superset.commands.dataset.delete import DeleteDatasetCommand

    cmd = DeleteDatasetCommand([1])
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Datasets not found"):
        cmd.run()


def test_update_dataset_command_raises_value_error(mocker):
    """UpdateDatasetCommand.run() raises ValueError when _model is not set.

    The @transaction decorator's on_error handler catches ValueError and
    re-raises as DatasetUpdateFailedError, so we verify the wrapper exception.
    """
    from superset.commands.dataset.exceptions import DatasetUpdateFailedError
    from superset.commands.dataset.update import UpdateDatasetCommand

    cmd = UpdateDatasetCommand(1, {})
    mocker.patch.object(cmd, "validate")
    with pytest.raises(DatasetUpdateFailedError):
        cmd.run()


def test_delete_database_command_raises_value_error(mocker):
    """DeleteDatabaseCommand.run() raises ValueError when _model is not set."""
    from superset.commands.database.delete import DeleteDatabaseCommand

    cmd = DeleteDatabaseCommand(1)
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Database not found"):
        cmd.run()


def test_delete_report_schedule_command_raises_value_error(mocker):
    """DeleteReportScheduleCommand.run() raises ValueError when _models is not set."""
    from superset.commands.report.delete import DeleteReportScheduleCommand

    cmd = DeleteReportScheduleCommand([1])
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Report schedules not found"):
        cmd.run()


def test_update_tag_command_raises_value_error(mocker):
    """UpdateTagCommand.run() raises ValueError when _model is not set."""
    from superset.commands.tag.update import UpdateTagCommand

    cmd = UpdateTagCommand(1, {"name": "test"})
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Tag not found"):
        cmd.run()


def test_delete_annotation_layer_command_raises_value_error(mocker):
    """DeleteAnnotationLayerCommand.run() raises ValueError when _models is not set."""
    from superset.commands.annotation_layer.delete import DeleteAnnotationLayerCommand

    cmd = DeleteAnnotationLayerCommand([1])
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Annotation layers not found"):
        cmd.run()


def test_update_annotation_layer_command_raises_value_error(mocker):
    """UpdateAnnotationLayerCommand.run() raises ValueError when _model is not set."""
    from superset.commands.annotation_layer.update import UpdateAnnotationLayerCommand

    cmd = UpdateAnnotationLayerCommand(1, {})
    mocker.patch.object(cmd, "validate")
    with pytest.raises(ValueError, match="Annotation layer not found"):
        cmd.run()


def test_streaming_sql_export_raises_value_error():
    """StreamingSqlResultExportCommand helpers raise ValueError when _query is None."""
    from superset.commands.sql_lab.streaming_export_command import (
        StreamingSqlResultExportCommand,
    )

    cmd = StreamingSqlResultExportCommand("client-id")
    # _query is None by default
    with pytest.raises(ValueError, match="Query not found"):
        cmd._get_sql_and_database()

    with pytest.raises(ValueError, match="Query not found"):
        cmd._get_row_limit()
