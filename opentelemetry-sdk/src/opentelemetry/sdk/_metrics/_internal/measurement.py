# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from opentelemetry.util.types import Attributes

if TYPE_CHECKING:
    from opentelemetry.sdk._metrics._internal.instrument import _Instrument


@dataclass(frozen=True)
class Measurement:
    """
    Represents a data point reported via the metrics API to the SDK.
    """

    value: Union[int, float]
    instrument: "_Instrument"
    attributes: Attributes = None
