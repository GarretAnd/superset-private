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
"""Base classes for favorite/unfavorite commands.

Provides ``BaseAddFavoriteCommand`` and ``BaseDelFavoriteCommand`` which
encapsulate the repeated pattern of:
  1. Look up a model by ID (via a DAO)
  2. Validate access
  3. Add or remove the model from the user's favorites

Subclasses only need to specify:
  - ``dao``: the DAO class (must implement ``find_by_id``, ``add_favorite``,
    and ``remove_favorite``)
  - ``not_found_error``: exception to raise when the model isn't found
  - ``access_error``: exception to raise on access denial
  - ``fave_error`` / ``unfave_error``: transaction-error exceptions
  - ``validate_access(model)``: hook for custom security checks
"""

import logging
from typing import Any, ClassVar

from superset.commands.base import BaseCommand

logger = logging.getLogger(__name__)


class BaseAddFavoriteCommand(BaseCommand):
    """Base command for adding a model to the user's favorites."""

    dao: ClassVar[Any]
    not_found_error: ClassVar[type[Exception] | None]
    fave_error: ClassVar[type[Exception]]

    def __init__(self, model_id: int) -> None:
        self._model_id = model_id
        self._model: Any | None = None

    def run(self) -> None:
        self.validate()
        if self._model:
            return self.dao.add_favorite(self._model)

    def validate(self) -> None:
        model = self.dao.find_by_id(self._model_id)
        if not model:
            if self.not_found_error:
                raise self.not_found_error()
            return
        self.validate_access(model)
        self._model = model

    def validate_access(self, model: Any) -> None:
        """Override to add custom access checks (e.g., security_manager)."""


class BaseDelFavoriteCommand(BaseCommand):
    """Base command for removing a model from the user's favorites."""

    dao: ClassVar[Any]
    not_found_error: ClassVar[type[Exception] | None]
    unfave_error: ClassVar[type[Exception]]

    def __init__(self, model_id: int) -> None:
        self._model_id = model_id
        self._model: Any | None = None

    def run(self) -> None:
        self.validate()
        if self._model:
            return self.dao.remove_favorite(self._model)

    def validate(self) -> None:
        model = self.dao.find_by_id(self._model_id)
        if not model:
            if self.not_found_error:
                raise self.not_found_error()
            return
        self.validate_access(model)
        self._model = model

    def validate_access(self, model: Any) -> None:
        """Override to add custom access checks (e.g., security_manager)."""
