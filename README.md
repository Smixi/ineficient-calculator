# ineficient-calculator

## What is this about ?

The purpose of this repository is for me to get hands on tools for Kubernetes: Istio, Knative Serving, Sidecards with Kiali, and OpenTelemetry. It will serve for a demo purpose, and require additionnals installation (which requirements may be later added) of Operators such as Knative Serving, Istio, Jaeger.

## The Ineficient Calculator

Of course, I wanted to have some nested spans and use multi services, so I choose to implement (a badly designed) microservices stack to compute simple equation. To do so, the **parse** microservice allow to be passed on the 'POST /' route a JSON of this structure: 
```json
{'expression': '1+2+3'}
```

This expression is parsed using the python AST and then converted as a JSONesque graph.

This is then evaluated using the **eval** microservice, which in turns knows how to evaluate each graph node, depending on the operator used.

For example, if **eval** receives
```json
{
    'type': 'expression', 
    'value': {
        'operator': 'add', 
        'leftOperand': {
            'type': 'expression', 
            'value': {
                'operator': 'add', 
                'leftOperand': {
                    'type': 'literal', 
                    'value': 1
                }, 
                'rightOperand': {
                    'type': 'literal', 
                    'value': 1
                }
            }
        }
        'rightOperand': {
            'type': 'literal', 
            'value': 1
        }
    }
}
```
Then it will sends one request to the **add** microservice, which in turns will see the two operand. The right operand is a literal, so it doesn't needs know its value, but the left one is an expression, which needs to be evaluated ... by the "eval" microservice. This make those service recursevily calls each others in some sort of the "Interpreter Pattern". Of course, those evaluation here are blocking, which means the left and right evaluation are executed in a sequence, and each microservices wait for the nested evaluation to be finished.

Using Kiali, we can see how everything is connected, which in case is a star-like graph centered on **eval** (which is obvious):

![kiali view](/doc/img/kiali.png "Mesh graph using kiali and istio")

Using Jaeger, we can see some spans and how everything is nested, for instance using a more complex query:
![jaeger view](/doc/img/spans-example.jpg "Span visualisation using Jaeger")