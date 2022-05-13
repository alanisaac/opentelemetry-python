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

from atexit import register, unregister
from logging import getLogger
from threading import Lock
from typing import Optional, Sequence

# This kind of import is needed to avoid Sphinx errors.
import opentelemetry.sdk._metrics
from opentelemetry._metrics import Counter as APICounter
from opentelemetry._metrics import Histogram as APIHistogram
from opentelemetry._metrics import Meter as APIMeter
from opentelemetry._metrics import MeterProvider as APIMeterProvider
from opentelemetry._metrics import NoOpMeter
from opentelemetry._metrics import ObservableCounter as APIObservableCounter
from opentelemetry._metrics import ObservableGauge as APIObservableGauge
from opentelemetry._metrics import (
    ObservableUpDownCounter as APIObservableUpDownCounter,
)
from opentelemetry._metrics import UpDownCounter as APIUpDownCounter
from opentelemetry.sdk._metrics._internal.instrument import (
    Counter,
    Histogram,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk._metrics._internal.measurement_consumer import (
    MeasurementConsumer,
    SynchronousMeasurementConsumer,
)
from opentelemetry.sdk._metrics._internal.sdk_configuration import (
    SdkConfiguration,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.util._once import Once
from opentelemetry.util._time import _time_ns

_logger = getLogger(__name__)


class Meter(APIMeter):
    """See `opentelemetry._metrics.Meter`."""

    def __init__(
        self,
        instrumentation_scope: InstrumentationScope,
        measurement_consumer: MeasurementConsumer,
    ):
        super().__init__(instrumentation_scope)
        self._instrumentation_scope = instrumentation_scope
        self._measurement_consumer = measurement_consumer
        self._instrument_id_instrument = {}
        self._instrument_id_instrument_lock = Lock()

    def create_counter(self, name, unit="", description="") -> APICounter:

        (
            is_instrument_registered,
            instrument_id,
        ) = self._is_instrument_registered(name, Counter, unit, description)

        if is_instrument_registered:
            # FIXME #2558 go through all views here and check if this
            # instrument registration conflict can be fixed. If it can be, do
            # not log the following warning.
            _logger.warning(
                "An instrument with name %s, type %s, unit %s and "
                "description %s has been created already.",
                name,
                APICounter.__name__,
                unit,
                description,
            )
            with self._instrument_id_instrument_lock:
                return self._instrument_id_instrument[instrument_id]

        instrument = Counter(
            name,
            self._instrumentation_scope,
            self._measurement_consumer,
            unit,
            description,
        )

        with self._instrument_id_instrument_lock:
            self._instrument_id_instrument[instrument_id] = instrument
            return instrument

    def create_up_down_counter(
        self, name, unit="", description=""
    ) -> APIUpDownCounter:

        (
            is_instrument_registered,
            instrument_id,
        ) = self._is_instrument_registered(
            name, UpDownCounter, unit, description
        )

        if is_instrument_registered:
            # FIXME #2558 go through all views here and check if this
            # instrument registration conflict can be fixed. If it can be, do
            # not log the following warning.
            _logger.warning(
                "An instrument with name %s, type %s, unit %s and "
                "description %s has been created already.",
                name,
                APIUpDownCounter.__name__,
                unit,
                description,
            )
            with self._instrument_id_instrument_lock:
                return self._instrument_id_instrument[instrument_id]

        instrument = UpDownCounter(
            name,
            self._instrumentation_scope,
            self._measurement_consumer,
            unit,
            description,
        )

        with self._instrument_id_instrument_lock:
            self._instrument_id_instrument[instrument_id] = instrument
            return instrument

    def create_observable_counter(
        self, name, callbacks=None, unit="", description=""
    ) -> APIObservableCounter:

        (
            is_instrument_registered,
            instrument_id,
        ) = self._is_instrument_registered(
            name, ObservableCounter, unit, description
        )

        if is_instrument_registered:
            # FIXME #2558 go through all views here and check if this
            # instrument registration conflict can be fixed. If it can be, do
            # not log the following warning.
            _logger.warning(
                "An instrument with name %s, type %s, unit %s and "
                "description %s has been created already.",
                name,
                APIObservableCounter.__name__,
                unit,
                description,
            )
            with self._instrument_id_instrument_lock:
                return self._instrument_id_instrument[instrument_id]

        instrument = ObservableCounter(
            name,
            self._instrumentation_scope,
            self._measurement_consumer,
            callbacks,
            unit,
            description,
        )

        self._measurement_consumer.register_asynchronous_instrument(instrument)

        with self._instrument_id_instrument_lock:
            self._instrument_id_instrument[instrument_id] = instrument
            return instrument

    def create_histogram(self, name, unit="", description="") -> APIHistogram:

        (
            is_instrument_registered,
            instrument_id,
        ) = self._is_instrument_registered(name, Histogram, unit, description)

        if is_instrument_registered:
            # FIXME #2558 go through all views here and check if this
            # instrument registration conflict can be fixed. If it can be, do
            # not log the following warning.
            _logger.warning(
                "An instrument with name %s, type %s, unit %s and "
                "description %s has been created already.",
                name,
                APIHistogram.__name__,
                unit,
                description,
            )
            with self._instrument_id_instrument_lock:
                return self._instrument_id_instrument[instrument_id]

        instrument = Histogram(
            name,
            self._instrumentation_scope,
            self._measurement_consumer,
            unit,
            description,
        )
        with self._instrument_id_instrument_lock:
            self._instrument_id_instrument[instrument_id] = instrument
            return instrument

    def create_observable_gauge(
        self, name, callbacks=None, unit="", description=""
    ) -> APIObservableGauge:

        (
            is_instrument_registered,
            instrument_id,
        ) = self._is_instrument_registered(
            name, ObservableGauge, unit, description
        )

        if is_instrument_registered:
            # FIXME #2558 go through all views here and check if this
            # instrument registration conflict can be fixed. If it can be, do
            # not log the following warning.
            _logger.warning(
                "An instrument with name %s, type %s, unit %s and "
                "description %s has been created already.",
                name,
                APIObservableGauge.__name__,
                unit,
                description,
            )
            with self._instrument_id_instrument_lock:
                return self._instrument_id_instrument[instrument_id]

        instrument = ObservableGauge(
            name,
            self._instrumentation_scope,
            self._measurement_consumer,
            callbacks,
            unit,
            description,
        )

        self._measurement_consumer.register_asynchronous_instrument(instrument)

        with self._instrument_id_instrument_lock:
            self._instrument_id_instrument[instrument_id] = instrument
            return instrument

    def create_observable_up_down_counter(
        self, name, callbacks=None, unit="", description=""
    ) -> APIObservableUpDownCounter:

        (
            is_instrument_registered,
            instrument_id,
        ) = self._is_instrument_registered(name, Counter, unit, description)

        if is_instrument_registered:
            # FIXME #2558 go through all views here and check if this
            # instrument registration conflict can be fixed. If it can be, do
            # not log the following warning.
            _logger.warning(
                "An instrument with name %s, type %s, unit %s and "
                "description %s has been created already.",
                name,
                APIObservableUpDownCounter.__name__,
                unit,
                description,
            )
            with self._instrument_id_instrument_lock:
                return self._instrument_id_instrument[instrument_id]

        instrument = ObservableUpDownCounter(
            name,
            self._instrumentation_scope,
            self._measurement_consumer,
            callbacks,
            unit,
            description,
        )

        self._measurement_consumer.register_asynchronous_instrument(instrument)

        with self._instrument_id_instrument_lock:
            self._instrument_id_instrument[instrument_id] = instrument
            return instrument


class MeterProvider(APIMeterProvider):
    r"""See `opentelemetry._metrics.MeterProvider`.

    Args:
        metric_readers: Register metric readers to collect metrics from the SDK
            on demand. Each :class:`opentelemetry.sdk._metrics.export.MetricReader` is
            completely independent and will collect separate streams of
            metrics. TODO: reference ``PeriodicExportingMetricReader`` usage with push
            exporters here.
        resource: The resource representing what the metrics emitted from the SDK pertain to.
        shutdown_on_exit: If true, registers an `atexit` handler to call
            `MeterProvider.shutdown`
        views: The views to configure the metric output the SDK

    By default, instruments which do not match any :class:`opentelemetry.sdk._metrics.view.View` (or if no :class:`opentelemetry.sdk._metrics.view.View`\ s
    are provided) will report metrics with the default aggregation for the
    instrument's kind. To disable instruments by default, configure a match-all
    :class:`opentelemetry.sdk._metrics.view.View` with `DropAggregation` and then create :class:`opentelemetry.sdk._metrics.view.View`\ s to re-enable
    individual instruments:

    .. code-block:: python
        :caption: Disable default views

        MeterProvider(
            views=[
                View(instrument_name="*", aggregation=DropAggregation()),
                View(instrument_name="mycounter"),
            ],
            # ...
        )
    """

    _all_metric_readers_lock = Lock()
    _all_metric_readers = set()

    def __init__(
        self,
        metric_readers: Sequence[
            "opentelemetry.sdk._metrics.export.MetricReader"
        ] = (),
        resource: Resource = Resource.create({}),
        shutdown_on_exit: bool = True,
        views: Sequence["opentelemetry.sdk._metrics.view.View"] = (),
    ):
        self._lock = Lock()
        self._meter_lock = Lock()
        self._atexit_handler = None
        self._sdk_config = SdkConfiguration(
            resource=resource,
            metric_readers=metric_readers,
            views=views,
        )
        self._measurement_consumer = SynchronousMeasurementConsumer(
            sdk_config=self._sdk_config
        )

        if shutdown_on_exit:
            self._atexit_handler = register(self.shutdown)

        self._meters = {}

        for metric_reader in self._sdk_config.metric_readers:

            with self._all_metric_readers_lock:
                if metric_reader in self._all_metric_readers:
                    raise Exception(
                        f"MetricReader {metric_reader} has been registered "
                        "already in other MeterProvider instance"
                    )

                self._all_metric_readers.add(metric_reader)

            metric_reader._set_collect_callback(
                self._measurement_consumer.collect
            )

        self._shutdown_once = Once()
        self._shutdown = False

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        deadline_ns = _time_ns() + timeout_millis * 10**6

        metric_reader_error = {}

        for metric_reader in self._sdk_config.metric_readers:
            current_ts = _time_ns()
            try:
                if current_ts >= deadline_ns:
                    raise Exception("Timed out while flushing metric readers")
                metric_reader.collect(
                    timeout_millis=(deadline_ns - current_ts) / 10**6
                )

            # pylint: disable=broad-except
            except Exception as error:

                metric_reader_error[metric_reader] = error

        if metric_reader_error:

            metric_reader_error_string = "\n".join(
                [
                    f"{metric_reader.__class__.__name__}: {repr(error)}"
                    for metric_reader, error in metric_reader_error.items()
                ]
            )

            raise Exception(
                "MeterProvider.force_flush failed because the following "
                "metric readers failed during collect:\n"
                f"{metric_reader_error_string}"
            )
        return True

    def shutdown(self, timeout_millis: float = 30_000):
        deadline_ns = _time_ns() + timeout_millis * 10**6

        def _shutdown():
            self._shutdown = True

        did_shutdown = self._shutdown_once.do_once(_shutdown)

        if not did_shutdown:
            _logger.warning("shutdown can only be called once")
            return

        metric_reader_error = {}

        for metric_reader in self._sdk_config.metric_readers:
            current_ts = _time_ns()
            try:
                if current_ts >= deadline_ns:
                    raise Exception(
                        "Didn't get to execute, deadline already exceeded"
                    )
                metric_reader.shutdown(
                    timeout_millis=(deadline_ns - current_ts) / 10**6
                )

            # pylint: disable=broad-except
            except Exception as error:

                metric_reader_error[metric_reader] = error

        if self._atexit_handler is not None:
            unregister(self._atexit_handler)
            self._atexit_handler = None

        if metric_reader_error:

            metric_reader_error_string = "\n".join(
                [
                    f"{metric_reader.__class__.__name__}: {repr(error)}"
                    for metric_reader, error in metric_reader_error.items()
                ]
            )

            raise Exception(
                (
                    "MeterProvider.shutdown failed because the following "
                    "metric readers failed during shutdown:\n"
                    f"{metric_reader_error_string}"
                )
            )

    def get_meter(
        self,
        name: str,
        version: Optional[str] = None,
        schema_url: Optional[str] = None,
    ) -> Meter:

        if self._shutdown:
            _logger.warning(
                "A shutdown `MeterProvider` can not provide a `Meter`"
            )
            return NoOpMeter(name, version=version, schema_url=schema_url)

        if not name:
            _logger.warning("Meter name cannot be None or empty.")
            return NoOpMeter(name, version=version, schema_url=schema_url)

        info = InstrumentationScope(name, version, schema_url)
        with self._meter_lock:
            if not self._meters.get(info):
                # FIXME #2558 pass SDKConfig object to meter so that the meter
                # has access to views.
                self._meters[info] = Meter(
                    info,
                    self._measurement_consumer,
                )
            return self._meters[info]
