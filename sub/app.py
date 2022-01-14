import json
import requests
from flask import Flask, request
from os import environ
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

JAEGER_PORT = int(environ.get('TRACER_PORT', 6831))
JAEGER_HOST = environ.get('TRACER_HOST', 'localhost')
trace.set_tracer_provider(
TracerProvider(
        resource=Resource.create({SERVICE_NAME: "sub-ms"})
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

MS_EVAL = environ.get('MS_EVAL')

# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def sub():
    expression_to_sub = request.json
    left_operand = expression_to_sub['leftOperand']
    right_operand = expression_to_sub['rightOperand']

    if left_operand['type'] == 'expression':
        response = requests.post(MS_EVAL, json=left_operand)
        l_value = response.json()['value']
    else:
        l_value = left_operand['value']

    if right_operand['type'] == 'expression':
        response = requests.post(MS_EVAL, json=right_operand)
        r_value = response.json()['value']
    else:
        r_value = right_operand['value']

    result = l_value - r_value

    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3001)
