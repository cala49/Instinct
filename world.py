# ============================================================
# CASILLA
# ============================================================

from entities import Terrain


class Cell:
    def __init__(self, terrain):
        self.terrain = terrain
        self.object = None
        self.creature = None

    @property
    def is_occupied(self):
        return (
            self.object is not None
            or self.creature is not None
        )
        
# ============================================================
# MUNDO
# ============================================================

class World:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.logs = []
        self.roars = []
        self.creatures = []

        self.grid = [
            [Cell(Terrain("default", ".", 100, 10)) for _ in range(width)]
            for _ in range(height)
        ]

        self.tick_number = 0

    # ========================================================
    # COORDENADAS
    # ========================================================

    def is_inside(self, x: int, y: int):
        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def get_cell(self, x: int, y: int):
        if not self.is_inside(x, y):
            return None

        return self.grid[y][x]

    # ========================================================
    # CRIATURAS
    # ========================================================

    def add_creature(self, creature):
        if not self.is_inside(creature.x, creature.y):
            return False

        cell = self.get_cell(
            creature.x,
            creature.y
        )

        if cell.is_occupied:
            return False

        cell.creature = creature
        self.creatures.append(creature)

        return True

    def remove_creature(self, creature):
        if self.is_inside(creature.x, creature.y):
            cell = self.get_cell(
                creature.x,
                creature.y
            )

            if cell.creature is creature:
                cell.creature = None

        if creature in self.creatures:
            self.creatures.remove(creature)

    # ========================================================
    # MOVIMIENTO
    # ========================================================

    def can_move_to(self, x: int, y: int):
        if not self.is_inside(x, y):
            return False

        cell = self.get_cell(x, y)

        return not cell.is_occupied

    def move_creature(self, creature, new_x: int, new_y: int):
        if not self.can_move_to(new_x, new_y):
            return False

        old_cell = self.get_cell(
            creature.x,
            creature.y
        )

        new_cell = self.get_cell(
            new_x,
            new_y
        )

        old_cell.creature = None

        new_cell.creature = creature

        creature.x = new_x
        creature.y = new_y

        return True

def add_object(self, obj, x: int, y: int):
    if not self.is_inside(x, y):
        return False

    cell = self.get_cell(x, y)

    if cell.is_occupied:
        return False

    cell.object = obj

    return True