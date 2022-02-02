import ast
import json
import redis
import requests
from flask import Flask, request
from os import environ
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

JAEGER_PORT = int(environ.get('TRACER_PORT', 6831))
JAEGER_HOST = environ.get('TRACER_HOST', 'localhost')

REDIS_HOST = environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = environ.get('REDIS_PORT', 6379)
REDIS_PASSWORD = environ.get('REDIS_PASSWORD', 'password')

trace.set_tracer_provider(
TracerProvider(
        resource=Resource.create({SERVICE_NAME: "eval-ms"})
    )
)
tracer = trace.get_tracer(__name__)

# create a JaegerExporter
jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name=JAEGER_HOST,
    agent_port=JAEGER_PORT
)

# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)
# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)

app = Flask(__name__)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
RedisInstrumentor().instrument()

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

MS_ADD = environ.get('MS_ADD')
MS_SUB = environ.get('MS_SUB')
MS_MULT = environ.get('MS_MULT')
MS_DIV = environ.get('MS_DIV')

service_mapping = {'add': MS_ADD,
                   'sub': MS_SUB,
                   'mult': MS_MULT,
                   'div': MS_DIV
                }

def try_eval_number(val):
  """Convert string to correct type"""
  try:
    val = ast.literal_eval(val)
  except ValueError:
    pass
  return val

@app.route("/", methods=["POST"])
def eval():
    obj = request.json
    expression = obj['value']
    expression_type = obj['type']

    exp_as_key = json.dumps(expression)
    if expression_type == "expression":
        # Full retarded caching here :).
        cached = redis_client.get(exp_as_key)
        if cached is not None:
            result = try_eval_number(cached.decode('utf8'))
        else: 
            operator = expression['operator']
            response = requests.post(service_mapping[operator], json=expression)
            result = response.json()['value']
            redis_client.set(exp_as_key, result)
    else:
        result = expression
    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3010)
