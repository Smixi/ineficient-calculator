import requests
import ast
from ast import BinOp, Constant, Add, Mult, Sub, Div
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from os import environ
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


JAEGER_PORT = int(environ.get('TRACER_PORT', 6831))
JAEGER_HOST = environ.get('TRACER_HOST', 'localhost')
trace.set_tracer_provider(
TracerProvider(
        resource=Resource.create({SERVICE_NAME: "parse-ms"})
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


MS_EVAL = environ.get('MS_EVAL')
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()



operator_map = {Add: 'add', Sub: 'sub', Mult: 'mult', Div: 'div'}

def parse_node(node):
    if isinstance(node, BinOp):
        operator_type = operator_map[node.op.__class__]
        return {'type': 'expression', 'value': {'operator': operator_type, 'leftOperand': parse_node(node.left), 'rightOperand': parse_node(node.right)}}
    if isinstance(node, Constant):
        return {'type': 'literal', 'value': node.value}
    raise ValueError(f"instance of type `{node}` is not handled")

def parse_expression(str_expression):
    parsed = ast.parse(str_expression, mode="eval")
    expression = parse_node(parsed.body)
    return expression


@app.route("/", methods=["POST"])
def parse():

    str_expression = request.json['expression']
    parsed_expression = parse_expression(str_expression)
    result = requests.post(MS_EVAL, json=parsed_expression).json()

    return result, 200

if __name__ == "__main__":
    app.run(port=3000)
