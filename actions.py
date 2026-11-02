from abc import ABC, abstractmethod
from errors import InstinctRuntimeError
from creature import Creature


# ============================================================
# ACCIÓN BASE
# ============================================================

class Action(ABC):

    @abstractmethod
    def execute(self, creature, world, arguments):
        pass

# ============================================================
# MOVE
# ============================================================

class MoveAction(Action):

    def execute(self, creature, world, arguments):
        dx, dy, speed = arguments

        self.validate_arguments(
            dx,
            dy,
            speed
        )

        for _ in range(speed):

            new_x = creature.x + dx
            new_y = creature.y + dy

            if not world.can_move_to(
                new_x,
                new_y
            ):
                break

            world.move_creature(
                creature,
                new_x,
                new_y
            )

    def validate_arguments(self, dx, dy, speed):

        if not all(
            isinstance(value, int)
            for value in (dx, dy, speed)
        ):
            raise InstinctRuntimeError(
                "'move' requiere argumentos numéricos"
            )

        if dx not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dx' debe ser -1, 0 o 1"
            )

        if dy not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dy' debe ser -1, 0 o 1"
            )

# ============================================================
# ATTACK
# ============================================================

class AttackAction(Action):

    def execute(self, creature, world, arguments):
        dx, dy, damage = arguments

        self.validate_arguments(
            dx,
            dy,
            damage
        )

        target_x = creature.x + dx
        target_y = creature.y + dy

        if not world.is_inside(
            target_x,
            target_y
        ):
            return

        cell = world.get_cell(
            target_x,
            target_y
        )

        # Criatura
        if cell.creature is not None:
            target = cell.creature

            target.receive_damage(damage)

            if not target.alive:
                world.remove_creature(target)

            return

        # Objeto
        if cell.object is not None:
            cell.object.receive_damage(damage)

            if cell.object.destroyed:
                cell.object = None

            return

        # Terreno
        cell.terrain.receive_damage(damage)

    def execute(self, creature, world, arguments):
        dx, dy, damage = arguments

        self.validate_arguments(
            dx,
            dy,
            damage
        )

        target_x = creature.x + dx
        target_y = creature.y + dy

        if not world.is_inside(
            target_x,
            target_y
        ):
            return

        cell = world.get_cell(
            target_x,
            target_y
        )

        if cell.creature is not None:
            target = cell.creature

            target.receive_damage(damage)

            if not target.alive:
                world.remove_creature(target)


    def validate_arguments(self, dx, dy, damage):

        if not all(
            isinstance(value, int)
            for value in (dx, dy, damage)
        ):
            raise InstinctRuntimeError(
                "'attack' requiere argumentos numéricos"
            )

        if dx not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dx' debe ser -1, 0 o 1"
            )

        if dy not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dy' debe ser -1, 0 o 1"
            )

# ============================================================
# CONSUME
# ============================================================

class ConsumeAction(Action):

    def execute(self, creature, world, arguments):
        dx, dy, damage, heal = arguments

        self.validate_arguments(
            dx,
            dy,
            damage,
            heal
        )

        target_x = creature.x + dx
        target_y = creature.y + dy

        if not world.is_inside(
            target_x,
            target_y
        ):
            return

        cell = world.get_cell(
            target_x,
            target_y
        )

        # ----------------------------------------------------
        # CASO ESPECIAL: (0, 0)
        # ----------------------------------------------------
        # Consume el terreno debajo de la propia criatura.

        if dx == 0 and dy == 0:
            cell.terrain.receive_damage(damage)
            creature.heal(heal)
            return

        # ----------------------------------------------------
        # CRIATURA
        # ----------------------------------------------------

        if cell.creature is not None:
            target = cell.creature

            target.receive_damage(damage)

            creature.heal(heal)

            if not target.alive:
                world.remove_creature(target)

            return

        # ----------------------------------------------------
        # OBJETO
        # ----------------------------------------------------

        if cell.object is not None:
            cell.object.receive_damage(damage)

            creature.heal(heal)

            if cell.object.destroyed:
                cell.object = None

            return

        # ----------------------------------------------------
        # TERRENO
        # ----------------------------------------------------

        cell.terrain.receive_damage(damage)
        creature.heal(heal)


    def validate_arguments(
        self,
        dx,
        dy,
        damage,
        heal
    ):
        if not all(
            isinstance(value, int)
            for value in (
                dx,
                dy,
                damage,
                heal
            )
        ):
            raise InstinctRuntimeError(
                "'consume' requiere argumentos numéricos"
            )

        if dx not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dx' debe ser -1, 0 o 1"
            )

        if dy not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dy' debe ser -1, 0 o 1"
            )
        
# ============================================================
# WAIT
# ============================================================

class WaitAction(Action):

    def execute(self, creature, world, arguments):
        n = arguments[0]

        self.validate_arguments(n)

        turns = max(1, n)

        # El turno actual ya fue consumido por wait
        creature.wait_remaining = turns - 1


    def validate_arguments(self, n):
        if not isinstance(n, int):
            raise InstinctRuntimeError(
                "'wait' requiere un argumento numérico"
            )

# ============================================================
# SAY
# ============================================================

class SayAction(Action):

    def execute(self, creature, world, arguments):
        value = arguments[0]

        message = str(value)

        world.logs.append(
            f"{creature.species}: {message}"
        )

# ============================================================
# ROAR
# ============================================================

class RoarAction(Action):

    def execute(self, creature, world, arguments):
        value = arguments[0]

        message = str(value)

        roar = {
            "creature": creature,
            "x": creature.x,
            "y": creature.y,
            "message": message,
        }

        world.roars.append(roar)

        world.logs.append(
            f"{creature.species} roars: {message}"
        )

# ============================================================
# REPRODUCE
# ============================================================

class ReproduceAction(Action):

    def execute(self, creature, world, arguments):
        dx, dy, health = arguments

        self.validate_arguments(
            dx,
            dy,
            health
        )

        target_x = creature.x + dx
        target_y = creature.y + dy

        # La reproducción siempre es a una casilla adyacente.
        if dx == 0 and dy == 0:
            return

        if not world.is_inside(
            target_x,
            target_y
        ):
            return

        cell = world.get_cell(
            target_x,
            target_y
        )

        # La casilla debe tener únicamente terreno.
        if cell.is_occupied:
            return

        # La madre debe tener MÁS vida que la que entrega.
        if creature.health <= health:
            return

        child = Creature(
            program=creature.program,
            x=target_x,
            y=target_y
        )

        # La cría nace con la vida indicada en reproduce(),
        # no con la vida inicial de la cabecera.
        child.health = health

        # Edad inicial.
        child.age = 0

        # El constructor ya crea un Interpreter nuevo,
        # por lo que sus variables empiezan vacías.

        added = world.add_creature(child)

        if not added:
            return

        creature.health -= health


    def validate_arguments(
        self,
        dx,
        dy,
        health
    ):
        if not all(
            isinstance(value, int)
            for value in (
                dx,
                dy,
                health
            )
        ):
            raise InstinctRuntimeError(
                "'reproduce' requiere argumentos numéricos"
            )

        if dx not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dx' debe ser -1, 0 o 1"
            )

        if dy not in {-1, 0, 1}:
            raise InstinctRuntimeError(
                "'dy' debe ser -1, 0 o 1"
            )


# ============================================================
# CATÁLOGO
# ============================================================

ACTIONS = {
    "move": MoveAction(),
    "attack": AttackAction(),
    "consume": ConsumeAction(),
    "wait": WaitAction(),
    "say": SayAction(),
    "roar": RoarAction(),
    "reproduce": ReproduceAction(),
}

def execute_action(
    action_request,
    creature,
    world
):
    action = ACTIONS.get(
        action_request.name
    )

    if action is None:
        raise InstinctRuntimeError(
            f"Acción desconocida "
            f"'{action_request.name}'",
            action_request.line
        )

    action.execute(
        creature,
        world,
        action_request.arguments
    )

def execute_free_actions(
    free_actions,
    creature,
    world
):
    for action_request in free_actions:
        execute_action(
            action_request,
            creature,
            world
        )