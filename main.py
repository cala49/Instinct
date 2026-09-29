from ast_nodes import (Literal, BinaryOperation)

expression = BinaryOperation(
    left=Literal(10, line=1),
    operator="+",
    right=Literal(3, line=1),
    line=1
)
result = expression.evaluate(None)
print(result)