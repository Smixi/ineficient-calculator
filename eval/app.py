import json
import requests
from flask import Flask, request
from os import environ
app = Flask(__name__)

MS_ADD = environ.get('MS_ADD')
MS_SUB = environ.get('MS_SUB')
MS_MULT = environ.get('MS_MULT')
MS_DIV = environ.get('MS_DIV')

service_mapping = {'add': MS_ADD,
                   'sub': MS_SUB,
                   'mult': MS_MULT,
                   'div': MS_DIV
                }

# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def eval():
    obj = request.json
    expression = obj['value']
    expression_type = obj['type']

    if expression_type == "expression":
        operator = expression['operator']
        response = requests.post(service_mapping[operator], json=expression)
        result = response.json()['value']
    else:
        result = expression
    
    return json.dumps({"value": result}), 200

if __name__ == "__main__":
    app.run(port=3010)
