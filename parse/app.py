from inspect import isclass
import json
import requests
import ast
from ast import BinOp, Constant, Add, Mult, Sub, Div
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from os import environ

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

MS_EVAL = environ.get('MS_EVAL')

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
