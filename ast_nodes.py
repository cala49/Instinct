from abc import ABC, abstractmethod
from dataclasses import dataclass
from errors import InstinctRuntimeError

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
        return context.resolve(self.name, self.line)

@dataclass
class UnaryOperation(Expression):
    operator: str
    operand: Expression
    line: int

    def evaluate(self, context):
        value = self.operand.evaluate(context)

        if self.operator == "not":
            return 0 if value else 1

        if self.operator == "-":
            if not isinstance(value, int):
                raise InstinctRuntimeError(
                    "El operador '-' requiere un número",
                    self.line
                )

            return -value

        raise InstinctRuntimeError(f"Operador unario desconocido '{self.operator}'", self.line)

@dataclass
class BinaryOperation(Expression):
    operator: str
    left: Expression
    right: Expression
    line: int

    def evaluate(self, context):
        left_value = self.left.evaluate(context)
        right_value = self.right.evaluate(context)

        if self.operator in {"and", "or"}:
            match self.operator:
                case "and":
                    return int(bool(left_value) and bool(right_value))

                case "or":
                    return int(bool(left_value) or bool(right_value))

    
        if type(left_value) is not type(right_value):
            raise InstinctRuntimeError("No se puede mezclar número y texto en el mismo operador", self.line)


        if isinstance(left_value, str):

            match self.operator:
                case "==":
                    return int(left_value == right_value)

                case "!=":
                    return int(left_value != right_value)

                case _:
                    raise InstinctRuntimeError(f"El operador '{self.operator}' no se puede aplicar a texto", self.line)

    
        match self.operator:

            case "+":
                return left_value + right_value

            case "-":
                return left_value - right_value

            case "*":
                return left_value * right_value

            case "/":
                if right_value == 0:
                    raise InstinctRuntimeError("División por cero", self.line)

                return left_value // right_value

            case "%":
                if right_value == 0:
                    raise InstinctRuntimeError("Módulo por cero", self.line)

                return left_value % right_value

            case "<":
                return int(left_value < right_value)

            case "<=":
                return int(left_value <= right_value)

            case ">":
                return int(left_value > right_value)

            case ">=":
                return int(left_value >= right_value)

            case "==":
                return int(left_value == right_value)

            case "!=":
                return int(left_value != right_value)

            case _:
                raise InstinctRuntimeError(f"Operador desconocido '{self.operator}'", self.line)
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
    lifespan: int

@dataclass 
class Program:
    header: CreatureHeader
    statements: list[Statement]