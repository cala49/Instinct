from abc import ABC, abstractmethod
from email import header 
from dataclasses import dataclass
from typing import Any

# ==================================================================================
# EXPRESIONES
# ==================================================================================

class Expression(ABC):
    @abstractmethod
    def evaluate(self,context):
        pass

@dataclass
class Literal(Expression):
    value: int|str
    line: int

    def evaluate(self, context):
        return self.value

@dataclass
class Variable(Expression):
    name: str
    line: int

    def evaluate(self, context):
        return context.resolve(self.name)

@dataclass
class UnaryOperation(Expression):
    operator: str
    operand: Expression
    line: int

    def evaluate(self, context):
        value = self.operand.evaluate(context)
        if self.operator == '-':
            return -value
        if self.operator == 'not':
            return 0 if value else 1
        raise RuntimeError(f"Operador Unario desconocido: {self.operator} en la línea {self.line}")

@dataclass
class BinaryOperation(Expression):
    operator: str
    left: Expression
    right: Expression
    line: int

    def evaluate(self, context):
        left_value = self.left.evaluate(context)
        right_value = self.right.evaluate(context)

        match self.operator:
            case '+':
                return left_value + right_value
            case '-':
                return left_value - right_value
            case '*':
                return left_value * right_value
            case '/':
                return left_value // right_value
            case '%':
                return left_value % right_value
            case '<':
                return int(left_value < right_value)
            case '<=':
                return int(left_value <= right_value)
            case '>':
                return int(left_value > right_value)
            case '>=':
                return int(left_value >= right_value)
            case '==':
                return int(left_value == right_value)
            case '!=':
                return int(left_value != right_value)
            case 'and':
                return 1 if left_value and right_value else 0
            case 'or':
                return 1 if left_value or right_value else 0
            case _:
                raise RuntimeError(f"Operador Binario desconocido: {self.operator} en la línea {self.line}")

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: list[Expression]
    line: int

    def evaluate(self, context):
        values = [argument.evaluate(context) for argument in self.arguments]
        return context.call_function(self.name, values)

# ==================================================================================
# INSTRUCCIONES
# ==================================================================================


class Statement(ABC):
    pass

@dataclass
class Label (Statement):
    name: str
    line: int

@dataclass 
class Goto(Statement):
    label: str
    line: int

@dataclass
class IfGoto(Statement):
    condition: Expression
    label: str
    line: int

@dataclass
class Assignment(Statement):
    name: str
    expression: Expression
    line: int

@dataclass
class ActionCall(Statement):
    name: str
    arguments: list[Expression]
    line: int

# ==================================================================================
# PROGRAMA
# ==================================================================================

@dataclass
class CreatureHeader:
    creature: str
    faction: str
    health: int
    vision: int
    livespan: int

@dataclass 
class Program:
    header: CreatureHeader
    Statements: list[Statement]