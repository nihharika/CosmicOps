"""
Metrics module for CosmicOps.
Defines OpenTelemetry counters.
"""

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader


# Setup Meter Provider

exporter = ConsoleMetricExporter()
reader = PeriodicExportingMetricReader(exporter)

provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("cosmicops")


# Metrics

images_processed = meter.create_counter(
    name="images_processed",
    description="Number of images processed",
)

anomalies_detected = meter.create_counter(
    name="anomalies_detected",
    description="Number of anomalies detected",
)