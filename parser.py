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

        while not self.is_start_label():
            key = self.expect(TokenType.IDENTIFIER, "Se esperaba una clave")

            if key.value not in {
                "faction",
                "health",
                "vision",
                "lifespan"
            }:
                raise ParserError(
                    f"Clave desconocida '{key.value}'", key.line)

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

        start_token = self.expect(TokenType.IDENTIFIER, "Se esperaba 'start'")

        if start_token.value != "start":
            raise ParserError("Se esperaba 'start'", start_token.line)

        self.expect(TokenType.COLON, "Se esperaba ':' después de start")

        return CreatureHeader(
            creature=values["creature"],
            faction=values["faction"],
            health=values["health"],
            vision=values["vision"],
            lifespan=values["lifespan"],
        )