from lexer import Lexer
from parser import Parser
from errors import InstinctError


source = """
creature Pirate
faction StrawHats
health 100
vision 5
lifespan 500

start:
"""


try:
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    program = parser.parse()

    print("claves cargadas correctamente:")
    print(program.header)

except InstinctError as error:
    print(f"Error: {error}")