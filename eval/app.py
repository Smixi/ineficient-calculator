import json
import requests
from flask import Flask, request
from os import environ
app = Flask(__name__)

MS_ADD = environ.get('MS_ADD')
MS_SUB = environ.get('MS_SUB')
MS_MULT = environ.get('MS_MULT')
MS_DIV = environ.get('MS_DIV')

# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def eval():
    obj = request.json
    expression = obj['value']
    expression_type = obj['type']

    if expression_type == "expression":
        operator = expression['operator']
        response = {'add': requests.post(MS_ADD, json=expression),
                    'sub': requests.post(MS_SUB, json=expression),
                    'mult': requests.post(MS_MULT, json=expression),
                    'div': requests.post(MS_DIV, json=expression)}[operator]
        result = response.json()['value']
    else:
        result = expression
    
    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3010)
