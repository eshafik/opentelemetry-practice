from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import requests
import _requests

from opentelemetry import trace, baggage, propagators
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

# Configure Jaeger exporter (replace with your endpoint)
jaeger_exporter = JaegerExporter(
   agent_host_name="localhost",
   agent_port=6831,
)


resource = Resource(
    attributes={
        SERVICE_NAME: 'project_2',
        SERVICE_NAMESPACE: "Project_2",
    }
)
trace.set_tracer_provider(
    TracerProvider(resource=resource)
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

middleware = [
    Middleware(CORSMiddleware,
               allow_origins=["*"],
               allow_credentials=True,
               allow_methods=["*"],
               allow_headers=["*"])
]

app = FastAPI(middleware=middleware)

FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)


@app.on_event("startup")
async def startup_event():
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    MySQLClientInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()


@app.get("/pro1")
async def api_one():
    return {"message": "Hello World from api_one"}


@app.get("/pro2")
async def api_two(request: Request):
    # Example: Log headers received in the request in API 2
    headers = dict(request.headers)
    ctx2 = None
    if headers.get('traceparent'):
        print(f"Received headers: {headers}")
        carrier = {'traceparent': headers['traceparent']}
        ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
        print(f"Received context: {ctx}")

        b2 = {'baggage': headers['baggage']}
        ctx2 = W3CBaggagePropagator().extract(b2, context=ctx)
        print(f"Received context2: {ctx2}")

    # Start a new span
    with tracer.start_span("api2_span", context=ctx2):
        # Use propagated context
        print(baggage.get_baggage('hello', ctx2))
        return {"message": "Hello World from api_one"}