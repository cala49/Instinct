from ast_nodes import (
    Label,
    Goto,
    IfGoto,
    Assignment,
    ActionCall,
    FunctionCall,
    UnaryOperation,
    BinaryOperation,
)
from errors import SemanticError


# ============================================================
# LISTA DE ARGUMENTOS DE ACCIONES Y FUNCIONES
# ============================================================

ACTION_ARGUMENTS = {
    "wait": 1,
    "move": 3,
    "attack": 3,
    "consume": 4,
    "reproduce": 3,
    "roar": 1,
    "say": 1,
}


FUNCTION_ARGUMENTS = {
    "see": 2,
    "name": 2,
}

PERCEPTIONS = {
    "health",
    "age",
    "lifespan",
    "vision",
    "species",
    "faction",
    "x",
    "y",
    "terrain_here",
    "reserve_here",
    "width",
    "height",
    "tick",
    "total_creatures",
    "total_allies",
    "total_enemies",
    "random",
    "allies_near",
    "enemies_near",
    "objects_near",
    "enemy_dist",
    "enemy_dx",
    "enemy_dy",
    "ally_dist",
    "ally_dx",
    "ally_dy",
    "object_dist",
    "object_dx",
    "object_dy",
    "roars_near",
    "last_roar",
}


CONSTANTS = {
    "NONE",
    "GROUND",
    "OBJECT",
    "ALLY",
    "ENEMY",
}


# ============================================================
# ANALIZADOR SEMÁNTICO
# ============================================================

class SemanticAnalyzer:
    def __init__(self, program):
        self.program = program

    def validate(self):
        self.validate_header()
        self.validate_labels()
        self.validate_actions()
        self.validate_expressions()
        self.validate_assignments()

    # ========================================================
    # ETIQUETAS
    # ========================================================

    def validate_labels(self):
        labels = {}

        # Registrar todas las etiquetas
        for statement in self.program.statements:

            if isinstance(statement, Label):

                if statement.name in labels:
                    raise SemanticError(
                        f"Etiqueta duplicada '{statement.name}'",
                        statement.line
                    )

                labels[statement.name] = statement.line

        # Comprobar que exista la etiqueta obligatoria 'start'
        if "start" not in labels:
            raise SemanticError(
                "Falta la etiqueta obligatoria 'start:'"
            )

        # Comprobar destinos de goto e if ... goto
        for statement in self.program.statements:

            if isinstance(statement, Goto):

                if statement.label not in labels:
                    raise SemanticError(
                        f"La etiqueta '{statement.label}' no existe",
                        statement.line
                    )

            elif isinstance(statement, IfGoto):

                if statement.label not in labels:
                    raise SemanticError(
                        f"La etiqueta '{statement.label}' no existe",
                        statement.line
                    )


    # ========================================================
    # ACCIONES
    # ========================================================

    def validate_actions(self):
        for statement in self.program.statements:

            if not isinstance(statement, ActionCall):
                continue

            if statement.name not in ACTION_ARGUMENTS:
                raise SemanticError(
                    f"Acción desconocida '{statement.name}'",
                    statement.line
                )

            expected = ACTION_ARGUMENTS[statement.name]
            received = len(statement.arguments)

            if received != expected:
                raise SemanticError(
                    f"La acción '{statement.name}' espera "
                    f"{expected} argumento(s), pero recibió {received}",
                    statement.line
                )


    # ========================================================
    # EXPRESIONES Y FUNCIONES
    # ========================================================

    def validate_expressions(self):
        for statement in self.program.statements:

            if isinstance(statement, Assignment):
                self.validate_expression(
                    statement.expression
                )

            elif isinstance(statement, IfGoto):
                self.validate_expression(
                    statement.condition
                )

            elif isinstance(statement, ActionCall):
                for argument in statement.arguments:
                    self.validate_expression(argument)


    def validate_expression(self, expression):

        if isinstance(expression, FunctionCall):

            if expression.name not in FUNCTION_ARGUMENTS:
                raise SemanticError(
                    f"Función desconocida '{expression.name}'",
                    expression.line
                )

            expected = FUNCTION_ARGUMENTS[expression.name]
            received = len(expression.arguments)

            if received != expected:
                raise SemanticError(
                    f"La función '{expression.name}' espera "
                    f"{expected} argumento(s), pero recibió {received}",
                    expression.line
                )

            for argument in expression.arguments:
                self.validate_expression(argument)

        elif isinstance(expression, BinaryOperation):
            self.validate_expression(expression.left)
            self.validate_expression(expression.right)

        elif isinstance(expression, UnaryOperation):
            self.validate_expression(expression.operand)

    # ============================================================
    # ASIGNACIONES
    # ============================================================

    def validate_assignments(self):
        for statement in self.program.statements:

            if not isinstance(statement, Assignment):
                continue

            if statement.name in PERCEPTIONS:
                raise SemanticError(f"No se puede asignar a la percepción " 
                                    f"'{statement.name}'", statement.line)

            if statement.name in CONSTANTS:
                raise SemanticError(f"No se puede asignar a la constante "
                    f"'{statement.name}'", statement.line)

    # ============================================================
    # CLAVES
    # ============================================================

    def validate_header(self):
        header = self.program.header
    
        if header.health <= 0:
            raise SemanticError(
                "'health' debe ser mayor que 0"
            )

        if header.vision < 1:
            raise SemanticError(
                "'vision' debe ser mayor o igual que 1"
            )

        if header.lifespan <= 0:
            raise SemanticError(
                "'lifespan' debe ser mayor que 0"
            )