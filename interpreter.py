from ast_nodes import (
    Label,
    Goto,
    IfGoto,
    Assignment,
    ActionCall,
)
from errors import InstinctRuntimeError
from dataclasses import dataclass

@dataclass
class ActionRequest:
    name: str
    arguments: list
    line: int

# ============================================================
# EJECUCIÓN
# ============================================================

class ExecutionContext:
    def __init__(self):
        self.variables = {}
        self.perceptions = {}
        self.constants = {
            "NONE": -1,
            "GROUND": 0,
            "OBJECT": 1,
            "ALLY": 2,
            "ENEMY": 3,
        }

    def resolve(self, name):
        if name in self.variables:
            return self.variables[name]

        if name in self.perceptions:
            return self.perceptions[name]

        if name in self.constants:
            return self.constants[name]

        raise InstinctRuntimeError(
            f"Variable '{name}' usada antes de ser asignada"
        )

    def assign(self, name, value):
        self.variables[name] = value

    def call_function(self, name, arguments):
        raise InstinctRuntimeError(
            f"La función '{name}' todavía no está conectada al mundo"
        )

# ============================================================
# INTÉRPRETE
# ============================================================

class Interpreter:
    def __init__(self, program):
        self.program = program
        self.statements = program.statements

        self.context = ExecutionContext()

        self.instruction_pointer = 0

        self.labels = self.build_label_table()

    def build_label_table(self):
        labels = {}

        for index, statement in enumerate(self.statements):
            if isinstance(statement, Label):
                labels[statement.name] = index

        return labels

    def start(self):
        self.instruction_pointer = self.labels["start"]

    def execute_turn(self):
        lines_executed = 0

        while lines_executed < 100:
            if self.instruction_pointer >= len(self.statements):
                self.instruction_pointer = self.labels["start"]
                return None

            statement = self.statements[self.instruction_pointer]

            lines_executed += 1

            action = self.execute_statement(statement)

            if action is not None:
                return action

        return None

    def execute_statement(self, statement):

        # ----------------------------------------------------
        # Etiqueta
        # ----------------------------------------------------

        if isinstance(statement, Label):
            self.instruction_pointer += 1
            return None

        # ----------------------------------------------------
        # Asignación
        # ----------------------------------------------------

        if isinstance(statement, Assignment):
            value = statement.expression.evaluate(self.context)

            self.context.assign(
                statement.name,
                value
            )

            self.instruction_pointer += 1
            return None

        # ----------------------------------------------------
        # GOTO
        # ----------------------------------------------------

        if isinstance(statement, Goto):
            self.instruction_pointer = self.labels[statement.label] +1
            return None

        # ----------------------------------------------------
        # IF ... GOTO
        # ----------------------------------------------------

        if isinstance(statement, IfGoto):
            condition = statement.condition.evaluate(self.context)

            if condition:
                self.instruction_pointer = self.labels[statement.label] + 1
            else:
                self.instruction_pointer += 1

            return None

        # ----------------------------------------------------
        # ACCIÓN
        # ----------------------------------------------------

        if isinstance(statement, ActionCall):
            arguments = []

            for expression in statement.arguments:
                value = expression.evaluate(self.context)
                arguments.append(value)

            self.instruction_pointer += 1

            return ActionRequest(
            name=statement.name,
            arguments=arguments,
            line=statement.line
        )

        raise InstinctRuntimeError(
        "Instrucción desconocida",
        statement.line
    )

    def execute_turn(self):
        lines_executed = 0
        free_actions = []

        while lines_executed < 100:

            if self.instruction_pointer >= len(self.statements):
                self.instruction_pointer = self.labels["start"]
                return None, free_actions

            statement = self.statements[self.instruction_pointer]

            lines_executed += 1

            action = self.execute_statement(statement)

            if action is None:
                continue

            if action.name == "say":
                free_actions.append(action)
                continue

            return action, free_actions

        return None, free_actions        
    