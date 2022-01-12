import json
import requests
from flask import Flask, request
from os import environ
app = Flask(__name__)

MS_EVAL = environ.get('MS_EVAL')

# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def div():
    expression_to_add = request.json
    left_operand = expression_to_add['leftOperand']
    right_operand = expression_to_add['rightOperand']

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

    result = l_value / r_value

    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3004)
