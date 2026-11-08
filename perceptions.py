# ============================================================
# UTILIDADES
# ============================================================

def distance(x1, y1, x2, y2):
    return max(
        abs(x2 - x1),
        abs(y2 - y1)
    )


def direction(value):
    if value > 0:
        return 1

    if value < 0:
        return -1

    return 0

# ============================================================
# PERCEPCIONES
# ============================================================

class PerceptionManager:

    def update(self, creature, world):
        perceptions = (creature.interpreter.context.perceptions)

        self.update_self(creature, world, perceptions)

        self.update_world(creature, world, perceptions)

        self.update_nearby(creature, world, perceptions)

    def update_world(self, creature, world, perceptions):
        perceptions["width"] = world.width
        perceptions["height"] = world.height
        perceptions["tick"] = world.tick_number

        total_creatures = 0
        total_allies = 0
        total_enemies = 0

        for other in world.creatures:

            if other is creature:
                continue

            if not other.alive:
                continue

            total_creatures += 1

            if other.faction == creature.faction:
                total_allies += 1
            else:
                total_enemies += 1

        perceptions["total_creatures"] = total_creatures
        perceptions["total_allies"] = total_allies
        perceptions["total_enemies"] = total_enemies

    def update_nearby(self, creature, world, perceptions):
        allies = self.get_visible_allies(creature, world)

        enemies = self.get_visible_enemies(creature, world)

        objects = self.get_visible_objects(creature, world)

        perceptions["allies_near"] = len(allies)
        perceptions["enemies_near"] = len(enemies)
        perceptions["objects_near"] = len(objects)

        self.set_nearest(creature, allies, perceptions, "ally")

        self.set_nearest(creature, enemies, perceptions, "enemy")

        self.set_nearest(creature, objects, perceptions, "object")

    def get_visible_allies(self, creature, world):
        allies = []

        for other in world.creatures:

            if other is creature:
                continue

            if not other.alive:
                continue

            if other.faction != creature.faction:
                continue

            dist = distance(creature.x, creature.y, other.x, other.y)

            if dist > creature.vision:
                continue

            allies.append((dist, other.x, other.y, other))
        return allies

    def get_visible_enemies(self, creature, world):
        enemies = []

        for other in world.creatures:

            if other is creature:
                continue

            if not other.alive:
                continue

            if other.faction == creature.faction:
                continue

            dist = distance(creature.x, creature.y, other.x, other.y)

            if dist > creature.vision:
                continue

            enemies.append(
                (
                    dist,
                    other.x,
                    other.y,
                    other
                )
            )

        return enemies

    def set_nearest(self, creature, candidates, perceptions, prefix):
        if not candidates:
            perceptions[f"{prefix}_dist"] = -1
            perceptions[f"{prefix}_dx"] = 0
            perceptions[f"{prefix}_dy"] = 0
            return

        candidates.sort(key=lambda item: item[0])

        dist, x, y, _ = candidates[0]

        perceptions[f"{prefix}_dist"] = dist

        perceptions[f"{prefix}_dx"] = direction(x - creature.x)

        perceptions[f"{prefix}_dy"] = direction(y - creature.y)

    def update_self(self, creature, world, perceptions):
        cell = world.get_cell(
            creature.x,
            creature.y
        )

        perceptions["health"] = creature.health
        perceptions["age"] = creature.age
        perceptions["lifespan"] = creature.lifespan
        perceptions["vision"] = creature.vision

        perceptions["species"] = creature.species  
        perceptions["faction"] = creature.faction

        perceptions["x"] = creature.x
        perceptions["y"] = creature.y

        perceptions["terrain_here"] = cell.terrain.name
        perceptions["reserve_here"] = cell.terrain.reserve

    def get_visible_objects(self, creature, world):
        objects = []

        for y in range(world.height):
            for x in range(world.width):
                cell = world.get_cell(x, y)

                if cell.object is None:
                    continue

                dist = distance(creature.x, creature.y, x, y)

                if dist > creature.vision:
                    continue

                objects.append((dist, x, y, cell.object))

        return objects  