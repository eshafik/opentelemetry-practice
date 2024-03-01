from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import requests
import _requests

from opentelemetry import trace, baggage, metrics
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.mysqlclient import MySQLClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


# # Configure Jaeger exporter (replace with your endpoint)
# jaeger_exporter = JaegerExporter(
#    agent_host_name="localhost",
#    agent_port=6831,
# )


resource = Resource(
    attributes={
        SERVICE_NAME: 'project_1',
        SERVICE_NAMESPACE: "Project_1",
    }
)
# trace.set_tracer_provider(
#     TracerProvider(resource=resource)
# )
# trace.get_tracer_provider().add_span_processor(
#     BatchSpanProcessor(jaeger_exporter)
# )

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider)

# reader = PeriodicExportingMetricReader(
#     OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics"),
#     export_interval_millis=1000, export_timeout_millis=60000
# )
# meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
# # metrics.set_meter_provider(meterProvider)
#
# print("hello... world....asdf")
# meter = metrics.get_meter('project_1')
# print("meter", meter)
#
# counter = meter.create_counter(
#     name="api_request_count",
#     description="Counts the number of API requests",
#     unit="1",
# )

middleware = [
    Middleware(CORSMiddleware,
               allow_origins=["*"],
               allow_credentials=True,
               allow_methods=["*"],
               allow_headers=["*"])
]

tracer = trace.get_tracer(__name__)


app = FastAPI(middleware=middleware)

FastAPIInstrumentor.instrument_app(app)


@app.on_event("startup")
async def startup_event():
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    MySQLClientInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()


@app.get("/api1")
async def api_one():
    # with trace.get_tracer('special').start_as_current_span('api1'):
    #     resp = requests.get('http://localhost:8002/pro1')
    #     print("response", resp.json())
    #     return {"message": "Hello World from api_one"}
    print("here...")
    return {"message": "Hello World from api_one"}


@app.get("/api2")
async def api_two():
    with trace.get_tracer('special').start_as_current_span("api2_span") as span:
        ctx = baggage.set_baggage(name='project_1', value='project_1')

        headers = {}
        W3CBaggagePropagator().inject(headers, ctx)
        TraceContextTextMapPropagator().inject(headers, ctx)
        print(headers)
        resp = await _requests.get("http://localhost:8002/pro2", headers=headers)
        print("response", resp.json())
        return {"message": "Hello World from api_one"}