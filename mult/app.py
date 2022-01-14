import json
import requests
from flask import Flask, request
from os import environ
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

MS_EVAL = environ.get('MS_EVAL')


@app.route("/", methods=["POST"])
def mult():
    expression_to_mult = request.json
    left_operand = expression_to_mult['leftOperand']
    right_operand = expression_to_mult['rightOperand']

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

    result = l_value * r_value

    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3003)
