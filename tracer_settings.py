from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure Jaeger exporter (replace with your endpoint)
jaeger_exporter = JaegerExporter(
   agent_host_name="localhost",
   agent_port=6831,
)


def get_trace(service_name):
    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            SERVICE_NAMESPACE: "Project_1",
        }
    )
    trace.set_tracer_provider(
        TracerProvider(resource=resource)
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    return trace
