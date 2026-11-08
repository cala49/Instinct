from ast_nodes import (
    Label,
    Goto,
    IfGoto,
    Assignment,
    ActionCall,
)
from errors import InstinctRuntimeError
from dataclasses import dataclass
import random

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
        self.creature = None
        self.world = None
        
        self.constants = {
            "NONE": -1,
            "GROUND": 0,
            "OBJECT": 1,
            "ALLY": 2,
            "ENEMY": 3,
        }

    def bind_world(self, creature, world):
        self.creature = creature
        self.world = world

    def resolve(self, name, line=None):
        if name in self.variables:
            return self.variables[name]

        if name == "random":
            if self.world is None:
                raise InstinctRuntimeError("'random' necesita estar conectado al mundo")
            return self.world.rng.randint(0, 99)

        if name in self.perceptions:
            return self.perceptions[name]

        if name in self.constants:
            return self.constants[name]

        raise InstinctRuntimeError(
            f"Variable '{name}' usada antes de ser asignada", line
        )

    def assign(self, name, value):
        self.variables[name] = value

    def call_function(self, name, arguments):
        if name == "see":
            return self.see(arguments[0], arguments[1])

        if name == "name":
            return self.get_name(arguments[0], arguments[1])

        raise InstinctRuntimeError(f"Función desconocida '{name}'")

    def see(self, x, y):
        if not isinstance(x, int) or not isinstance(y, int):
            raise InstinctRuntimeError("Las coordenadas deben ser números")

        creature = self.creature
        world = self.world

        dist = max(abs(x - creature.x), abs(y - creature.y))

        if dist > creature.vision:
            return self.constants["NONE"]

        if not world.is_inside(x, y):
            return self.constants["OBJECT"]

        cell = world.get_cell(x, y)

        if cell.creature is not None:

            if cell.creature.faction == creature.faction:
                return self.constants["ALLY"]

            return self.constants["ENEMY"]

        if cell.object is not None:
            return self.constants["OBJECT"]

        return self.constants["GROUND"]

    def get_name(self, x, y):

        if not isinstance(x, int) or not isinstance(y, int):
            raise InstinctRuntimeError("Las coordenadas deben ser números")

        creature = self.creature
        world = self.world

        dist = max(abs(x - creature.x), abs(y - creature.y))

        if dist > creature.vision:
            return ""

        if not world.is_inside(x, y):
            return ""

        cell = world.get_cell(x, y)

        if cell.creature is not None:
            return cell.creature.species

        if cell.object is not None:
            return cell.object.name

        return cell.terrain.name

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
    