from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from errors import InstinctError


source = """
creature Pirate
faction StrawHats
health 100
vision 5
lifespan 500

start:
steps = 0

walk:
if health < 20 goto flee
move(1, 0, 2)
steps = steps + 1
goto start

flee:
say("Run!")
wait(1)
goto start
"""


try:
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    program = parser.parse()

    semantic = SemanticAnalyzer(program)
    semantic.validate()

    print("Programa válido")

except InstinctError as error:
    print(f"Error: {error}")