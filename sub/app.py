import json
import requests
from flask import Flask, request
from os import environ
app = Flask(__name__)

MS_EVAL = environ.get('MS_EVAL')

# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def sub():
    expression_to_sub = request.json
    left_operand = expression_to_sub['leftOperand']
    right_operand = expression_to_sub['rightOperand']

    if left_operand['type'] == 'expression':
        response = requests.post(MS_EVAL, json=left_operand['value'])
        l_value = response.json()['value']
    else:
        l_value = left_operand['value']

    if right_operand['type'] == 'expression':
        response = requests.post(MS_EVAL, json=right_operand['value'])
        r_value = response.json()['value']
    else:
        r_value = right_operand['value']

    result = l_value - r_value

    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3001)
