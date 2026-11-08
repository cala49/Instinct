import random
from actions import (execute_action, execute_free_actions,)
from errors import InstinctRuntimeError


# ============================================================
# SIMULADOR
# ============================================================

class Simulator:

    def __init__(self, world, seed=None):
        self.world = world
        # Generador aleatorio propio del simulador.
        self.random = random.Random(seed)
        self.world.rng = self.random
        self.running = False

    # ========================================================
    # TICK
    # ========================================================

    def tick(self):

        # Avanza el contador global del mundo.
        self.world.tick_number += 1

        creatures = list(self.world.creatures)

        # El orden de los turnos cambia
        self.random.shuffle(creatures)

        # ----------------------------------------------------
        # TURNOS DE LAS CRIATURAS
        # ----------------------------------------------------

        for creature in creatures:

            if not creature.alive:
                continue

        try:
            action_request, free_actions = (creature.take_turn(self.world))

            execute_free_actions(free_actions, creature, self.world)

            if action_request is not None:
                execute_action(
                    action_request,
                    creature,
                    self.world
                )

        except InstinctRuntimeError as error:

            self.world.logs.append(
                f"{creature.species}: {error}"
            )

            creature.die()

            self.world.remove_creature(
                creature
            )
        self.end_tick()
           
    # ========================================================
    # FIN DEL TICK
    # ========================================================

    def end_tick(self):

        # ----------------------------------------------------
        # VIDA Y EDAD
        # ----------------------------------------------------

        for creature in list(self.world.creatures):

            creature.end_tick()

            if not creature.alive: 
                self.world.remove_creature(creature)

        # ----------------------------------------------------
        # REGENERACIÓN DE TERRENO
        # ----------------------------------------------------

        self.regenerate_terrain()

        # ----------------------------------------------------
        # LIMPIEZA DE OBJETOS DESTRUIDOS
        # ----------------------------------------------------

        self.remove_destroyed_objects()

    # ========================================================
    # TERRENOS
    # ========================================================

    def regenerate_terrain(self):
        for y in range(self.world.height):
            for x in range(self.world.width):

                cell = self.world.get_cell(x, y)
                cell.terrain.regenerate()

    # ========================================================
    # OBJETOS
    # ========================================================

    def remove_destroyed_objects(self):
        for y in range(self.world.height):
            for x in range(self.world.width):
                cell = self.world.get_cell(x, y)

                if cell.object is None:
                    continue

                if cell.object.destroyed:
                    cell.object = None

    # ========================================================
    # CONTROL DE SIMULACIÓN
    # ========================================================

    def run(self, ticks: int):
        for _ in range(ticks):
            self.tick()

    def play(self):
        self.running = True

    def pause(self):
        self.running = False

    # ========================================================
    # UTILIDADES
    # ========================================================

    @property
    def tick_number(self):
        return self.world.tick_number

    @property
    def creatures(self):
        return self.world.creatures

    @property
    def logs(self):
        return self.world.logs