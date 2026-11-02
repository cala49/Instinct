from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from creature import Creature
from world import World
from actions import (
    execute_action,
    execute_free_actions,
)
from errors import InstinctError


source = """
creature Pirate
faction StrawHats
health 100
vision 5
lifespan 500

start:
say("VOY A SER EL REY DE LOS PIRATAS")
roar("SANJI TENGO HAMBRE")
goto start
"""


def compile_program(source):
    tokens = Lexer(source).tokenize()

    program = Parser(tokens).parse()

    SemanticAnalyzer(program).validate()

    return program


try:
    program = compile_program(source)

    world = World(
        width=5,
        height=5
    )

    pirate = Creature(
        program=program,
        x=2,
        y=2
    )

    world.add_creature(pirate)

    action_request, free_actions = pirate.take_turn()

    # Ejecutar SAY
    execute_free_actions(
        free_actions,
        pirate,
        world
    )

    # Ejecutar ROAR
    if action_request is not None:
        execute_action(
            action_request,
            pirate,
            world
        )

    print("Logs:")
    for log in world.logs:
        print(log)

    print()

    print("Rugidos:")
    for roar in world.roars:
        print(roar["message"])


except InstinctError as error:
    print(f"Error: {error}")