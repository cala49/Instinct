from interpreter import Interpreter
from perceptions import PerceptionManager


# ============================================================
# CRIATURA
# ============================================================

class Creature:
    def __init__(self, program, x: int, y: int):

        # ----------------------------------------------------
        # PROGRAMA / INTÉRPRETE
        # ----------------------------------------------------

        self.program = program
        self.interpreter = Interpreter(program)

        self.interpreter.start()

        # ----------------------------------------------------
        # DATOS DE LA ESPECIE
        # ----------------------------------------------------

        header = program.header

        self.species = header.creature
        self.faction = header.faction

        self.health = header.health
        self.vision = header.vision
        self.lifespan = header.lifespan

        # ----------------------------------------------------
        # ESTADO INDIVIDUAL
        # ----------------------------------------------------

        self.age = 0

        self.x = x
        self.y = y

        self.alive = True

        # turnos restantes de espera por wait(n)
        self.wait_remaining = 0

    # ========================================================
    # PERCEPCIONES
    # ========================================================

    def update_basic_perceptions(self):
        perceptions = self.interpreter.context.perceptions

        perceptions["health"] = self.health
        perceptions["age"] = self.age
        perceptions["lifespan"] = self.lifespan
        perceptions["vision"] = self.vision

        perceptions["species"] = self.species
        perceptions["faction"] = self.faction

        perceptions["x"] = self.x
        perceptions["y"] = self.y

    # ========================================================
    # TURNO
    # ========================================================

    def take_turn(self, world):
        if not self.alive:
            return None, []

        self.interpreter.context.bind_world(self, world)

        PerceptionManager().update(self, world)

        if self.wait_remaining > 0:
            self.wait_remaining -= 1
            return None, []

        return self.interpreter.execute_turn()

    # ========================================================
    # VIDA
    # ========================================================

    def receive_damage(self, amount: int):
        self.health -= amount

        if self.health <= 0:
            self.die()


    def heal(self, amount: int):
        self.health += amount


    def die(self):
        self.alive = False

    # ========================================================
    # ENVEJECIIMIENTO
    # ========================================================

    def end_tick(self):
        if not self.alive:
            return

        self.health -= 1
        self.age += 1

        if self.health <= 0:
            self.die()

        elif self.age >= self.lifespan:
            self.die()