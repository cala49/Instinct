# ============================================================
# ENTIDAD CON RESERVA
# ============================================================

class ResourceEntity:
    def __init__(self, name: str, resource_max: int):
        self.name = name
        self.resource_max = resource_max
        self.reserve = resource_max

    def receive_damage(self, amount: int):
        self.reserve -= amount

# ============================================================
# TERRENO
# ============================================================

class Terrain(ResourceEntity):
    def __init__(
        self,
        name: str,
        char: str,
        resource_max: int,
        regen: int
    ):
        super().__init__(name, resource_max)

        self.char = char
        self.regen = regen

    def regenerate(self):
        self.reserve = min(
            self.resource_max,
            self.reserve + self.regen
        )

# ============================================================
# OBJETO
# ============================================================

class WorldObject(ResourceEntity):
    def __init__(
        self,
        name: str,
        char: str,
        resource_max: int
    ):
        super().__init__(name, resource_max)

        self.char = char

    @property
    def destroyed(self):
        return self.reserve <= 0