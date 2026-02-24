from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

resource = Resource(attributes={
    "service.name": "cosmicops"
})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer("cosmicops")