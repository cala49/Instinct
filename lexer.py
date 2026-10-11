from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    # Literales
    INTEGER = auto()
    STRING = auto()

    # Identificadores
    IDENTIFIER = auto()

    # Palabras reservadas
    IF = auto()
    GOTO = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Operadores
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    EQUAL = auto()
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()

    LESS = auto()
    LESS_EQUAL = auto()

    GREATER = auto()
    GREATER_EQUAL = auto()

    # Símbolos
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    COMMA = auto()
    COLON = auto()

    # Control
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: object
    line: int

KEYWORDS = {
    "if": TokenType.IF,
    "goto": TokenType.GOTO,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1

    def current_char(self):
        if self.position >= len(self.text):
            return None

        return self.text[self.position]

    def advance(self):
        self.position += 1

    def tokenize(self):
        tokens = []

        while self.current_char() is not None:
            char = self.current_char()

            # Espacios
            if char in " \t\r":
                self.advance()
                continue

            # Saltos de línea
            if char == "\n":
                tokens.append(
                    Token(TokenType.NEWLINE, "\n", self.line)
                )
                self.line += 1
                self.advance()
                continue

            # Comentarios
            if char == "#":
                self.skip_comment()
                continue

            # Números
            if char.isdigit():
                tokens.append(self.read_number())
                continue

            # Strings
            if char == '"':
                tokens.append(self.read_string())
                continue

            # Palabras reservadas
            if char.isalpha() or char == "_":
                tokens.append(self.read_identifier())
                continue

            # Símbolos y operadores
            token = self.read_symbol()

            if token is not None:
                tokens.append(token)
                continue

            raise Exception(
                f"Carácter desconocido '{char}' en línea {self.line}"
            )

        tokens.append(
            Token(TokenType.EOF, None, self.line)
        )

        return tokens

    def read_number(self):
        start = self.position

        while (
            self.current_char() is not None
            and self.current_char().isdigit()
        ):
            self.advance()

        value = self.text[start:self.position]

        return Token(
            TokenType.INTEGER,
            int(value),
            self.line
        )

    def read_identifier(self):
        start = self.position

        while (
            self.current_char() is not None
            and (
                self.current_char().isalnum()
                or self.current_char() == "_"
            )
        ):
            self.advance()

        value = self.text[start:self.position]

        token_type = KEYWORDS.get(
            value,
            TokenType.IDENTIFIER
        )

        return Token(
            token_type,
            value,
            self.line
        )

    def read_string(self):
        line = self.line

        self.advance() # comilla inicial

        start = self.position

        while (
            self.current_char() is not None
            and self.current_char() != '"'
        ):
            if self.current_char() == "\n":
                raise Exception(
                    f"String sin cerrar en línea {line}"
                )

            self.advance()

        if self.current_char() is None:
            raise Exception(
                f"String sin cerrar en línea {line}"
            )

        value = self.text[start:self.position]

        self.advance()  # comilla final

        return Token(
            TokenType.STRING,
            value,
            line
        )

    def skip_comment(self):
        while (
            self.current_char() is not None
            and self.current_char() != "\n"
        ):
            self.advance()

    def read_symbol(self):
        char = self.current_char()
        line = self.line

        # 2 CARACTERES
        next_char = None

        if self.position + 1 < len(self.text):
            next_char = self.text[self.position + 1]

        pair = char + (next_char or "")

        double_symbols = {
            "==": TokenType.EQUAL_EQUAL,
            "!=": TokenType.NOT_EQUAL,
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
        }

        if pair in double_symbols:
            self.advance()
            self.advance()

            return Token(
                double_symbols[pair],
                pair,
                line
            )

        # 1 CARACTER
        single_symbols = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "=": TokenType.EQUAL,
            "<": TokenType.LESS,
            ">": TokenType.GREATER,
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
        }

        if char in single_symbols:
            self.advance()

            return Token(
                single_symbols[char],
                char,
                line
            )

        return None