from loaders import ProjectLoader
from creature import Creature
from simulator import Simulator


loader = ProjectLoader(".")
loader.load_all()

print("CRIATURAS:", loader.creatures.keys())
print("LOGS DE CARGA:", loader.logs)

world = loader.maps["East Blue"]
program = loader.creatures["ErrorTest"]

creature = Creature(
    program=program,
    x=0,
    y=0
)

world.add_creature(creature)

simulator = Simulator(
    world,
    seed=42
)

print()
print("ANTES")
print("Alive:", creature.alive)

simulator.tick()

print()
print("DESPUÉS")
print("Alive:", creature.alive)
print(
    "Está en el mundo:",
    creature in world.creatures
)

print()
print("LOGS:")

for log in world.logs:
    print(log)