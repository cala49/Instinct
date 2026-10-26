from ast import expr
from cProfile import label
import token

from lexer import TokenType
from ast_nodes import (
    Program,
    CreatureHeader,
    Label,
    Goto,
    IfGoto,
    Assignment,
    ActionCall,
    Literal,
    Variable,
    UnaryOperation,
    BinaryOperation,
    FunctionCall,
)
from errors import ParserError

class Parser:
# ==================================================================================
# UTILIDADES
# ==================================================================================
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()
        if self.position < len(self.tokens) - 1:
            self.position += 1        
        return token

    def check(self, token_type):
        return self.current().type == token_type

    def match(self, *types):
        if self.current().type in types:
            return self.advance()
        return None

    def expect(self, token_type, message):
        if not self.check(token_type):
            raise ParserError(message, self.current().line)
        return self.advance()

    def skip_newlines(self):
        while self.check(TokenType.NEWLINE):
            self.advance()

# ==================================================================================
# PARSEO
# ==================================================================================

    def parse(self):
        self.skip_newlines()
        header = self.parse_header()
        statements = []
        self.skip_newlines()

        while not self.check(TokenType.EOF):
            statement = self.parse_statement()
            statements.append(statement)
            self.skip_newlines()
        return Program(header = header, statements = statements)

# ================================================================================
# CABECERA
# ================================================================================
    @property
    def is_start_label(self):
        return (
            self.check(TokenType.IDENTIFIER)
            and self.current().value == "start"
        )
    
    def parse_header(self):
        creature_token = self.expect(TokenType.IDENTIFIER, "Se esperaba 'creature'")
        if creature_token.value != "creature":
            raise ParserError("La primera linea debe comenzar con 'creature'", creature_token.line)

        name = self.expect(TokenType.IDENTIFIER, "Se esperaba el nombre").value
        self.expect(TokenType.NEWLINE, "Se esperaba un salto de línea después del nombre")
        values =  {"creature": name}

        while not self.is_start_label:
            key = self.expect(TokenType.IDENTIFIER, "Se esperaba una clave")

            if key.value not in {
                "faction",
                "health",
                "vision",
                "lifespan"
            }:
                raise ParserError(
                    f"Clave desconocida '{key.value}'", key.line)

            if key.value in values:
                raise ParserError(f"Clave duplicada '{key.value}'", key.line)
            
            if key.value == "faction":
                value = self.expect(TokenType.IDENTIFIER, "Se esperaba el nombre de la facción").value
            else:
                value = self.expect(TokenType.INTEGER, f"Se esperaba un número para '{key.value}'").value

            values[key.value] = value

            self.expect(TokenType.NEWLINE, "Se esperaba un salto de línea")

            self.skip_newlines()

        required = {
            "faction",
            "health",
            "vision",
            "lifespan"
        }

        missing = required - values.keys()

        if missing:
            raise ParserError(f"Faltan campos: {', '.join(missing)}", self.current().line)

        return CreatureHeader(
            creature=values["creature"],
            faction=values["faction"],
            health=values["health"],
            vision=values["vision"],
            lifespan=values["lifespan"],
        )

# ================================================================================
# INSTRUCCIONES
# ================================================================================

    def parse_statement(self):
        token = self.current()

        if token.type == TokenType.GOTO:
            return self.parse_goto()

        if token.type == TokenType.IF:
            return self.parse_if_goto()

        if token.type == TokenType.IDENTIFIER:
            return self.parse_identifier_statement()

        raise ParserError(
            f"Instrucción no válida: '{token.value}'",
            token.line
        )

    def parse_identifier_statement(self):
        identifier = self.advance()

        if identifier.value == "start" and not self.check(TokenType.COLON):
            raise ParserError(
                "Se esperaba ':' después de 'start'",
                identifier.line
            )
        
        if self.check(TokenType.COLON):
            self.advance()

            return Label(
                name=identifier.value,
                line=identifier.line
            )

        if self.check(TokenType.EQUAL):
            self.advance()

            expression = self.parse_expression()

            return Assignment(
                name=identifier.value,
                expression=expression,
                line=identifier.line
            )

        if self.check(TokenType.LEFT_PAREN):
            return self.parse_action_call(identifier)

        raise ParserError(
            f"No se reconoce la instrucción que comienza con '{identifier.value}'",
            identifier.line
        )

    def parse_goto(self):
        goto_token = self.expect(
            TokenType.GOTO,
            "Se esperaba 'goto'"
        )

        label = self.expect(
            TokenType.IDENTIFIER,
            "Se esperaba el nombre de una etiqueta"
        )

        return Goto(
            label=label.value,
            line=goto_token.line
        )
    def parse_if_goto(self):
        if_token = self.expect(
            TokenType.IF,
            "Se esperaba 'if'"
        )

        condition = self.parse_expression()

        self.expect(
            TokenType.GOTO,
            "Se esperaba 'goto' después de la condición"
        )

        label = self.expect(
            TokenType.IDENTIFIER,
            "Se esperaba el nombre de una etiqueta"
        )

        return IfGoto(
            condition=condition,
            label=label.value,
            line=if_token.line
        )

    def parse_action_call(self, identifier):
        self.expect(
            TokenType.LEFT_PAREN,
            "Se esperaba '(' después del nombre de la acción"
        )

        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.parse_expression())

            while self.check(TokenType.COMMA):
                self.advance()
                arguments.append(self.parse_expression())

        self.expect(
            TokenType.RIGHT_PAREN,
            "Se esperaba ')' al final"
        )

        return ActionCall(
            name=identifier.value,
            arguments=arguments,
            line=identifier.line
        )

# ================================================================================
# EXPRESIONES
# ================================================================================

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expression = self.parse_and()

        while self.check(TokenType.OR):
            operator = self.advance()
            
            right = self.parse_and()
            
            expression = BinaryOperation(
                left=expression,
                operator=operator.value,
                right=right,
                line=operator.line
            )
        return expression

    def parse_and(self):
        expression = self.parse_comparison()

        while self.check(TokenType.AND):
            operator = self.advance()
            
            right = self.parse_comparison()
            
            expression = BinaryOperation(
                left=expression,
                operator=operator.value,
                right=right,
                line=operator.line
            )
        return expression

    def parse_comparison(self):
        expression = self.parse_addition()

        comparison_types = {
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.NOT_EQUAL,
        } 

        while self.current().type in comparison_types:
            operator = self.advance()
            
            right = self.parse_addition()
            
            expression = BinaryOperation(
                left=expression,
                operator=operator.value,
                right=right,
                line=operator.line
            )
        return expression

    def parse_addition(self):
        expression = self.parse_multiplication()

        while self.current().type in {
            TokenType.PLUS,
            TokenType.MINUS
        }:
            operator = self.advance()
            
            right = self.parse_multiplication()
            
            expression = BinaryOperation(
                left=expression,
                operator=operator.value,
                right=right,
                line=operator.line
            )
        return expression

    def parse_multiplication(self):
        expression = self.parse_unary()

        while self.current().type in {
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT
        }:
            operator = self.advance()
            right = self.parse_unary()

            expression = BinaryOperation(
                left=expression,
                operator=operator.value,
                right=right,
                line=operator.line
            )

        return expression

    def parse_unary(self):
        if self.current().type in {
            TokenType.MINUS,
            TokenType.NOT
        }:
            operator = self.advance()
            
            operand = self.parse_unary()
            
            return UnaryOperation(
                operator=operator.value,
                operand=operand,
                line=operator.line
            )
        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        if self.check(TokenType.INTEGER):
            self.advance()

            return Literal(
                value=token.value,
                line=token.line
            )

        if self.check(TokenType.STRING):
            self.advance()

            return Literal(
                value=token.value,
                line=token.line
            )

        if self.check(TokenType.IDENTIFIER):
            identifier = self.advance()

            if self.check(TokenType.LEFT_PAREN):
                return self.parse_function_call(identifier)

            return Variable(
                name=identifier.value,
                line=identifier.line
            )

        if self.check(TokenType.LEFT_PAREN):
            self.advance()

            expression = self.parse_expression()

            self.expect(
                TokenType.RIGHT_PAREN,
                "Se esperaba ')'"
            )

            return expression

        raise ParserError(
            f"Expresión no válida cerca de '{token.value}'",
            token.line
        )