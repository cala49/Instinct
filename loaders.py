from pathlib import Path

from entities import Terrain, WorldObject
from world import World

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


# ============================================================
# UTILIDADES
# ============================================================

def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.readlines()

def clean_lines(path):
    result = []

    for number, raw_line in enumerate(
        read_lines(path),
        start=1
        ):
        
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        result.append((number, line))

    return result


def split_key_value(line, line_number):
    parts = line.split(maxsplit=1)

    if len(parts) != 2:
        raise ValueError(f"Línea {line_number}: se esperaba una clave y un valor")

    return parts[0], parts[1]


# ============================================================
# TERRENOS
# ============================================================

def load_terrain(path):
    lines = clean_lines(path)

    if not lines:
        raise ValueError("El archivo está vacío")

    first_line_number, first_line = lines[0]

    key, name = split_key_value(first_line, first_line_number)

    if key != "terrain":
        raise ValueError(
            f"Línea {first_line_number}: se esperaba 'terrain'")

    values = {}

    for line_number, line in lines[1:]:
        key, value = split_key_value(line, line_number)

        if key in values:
            raise ValueError(
                f"Línea {line_number}: clave duplicada '{key}'")

        values[key] = value

    required = {"char", "resource_max", "regen",}

    missing = required - values.keys()

    if missing:
        raise ValueError("Faltan claves: " + ", ".join(missing))

    char = values["char"]

    if len(char) != 1:
        raise ValueError("'char' debe ser un solo carácter")

    try:
        resource_max = int(values["resource_max"])

        regen = int(values["regen"])

    except ValueError:
        raise ValueError("'resource_max' y 'regen' deben ser enteros")

    return Terrain(name=name, char=char, resource_max=resource_max, regen=regen)


# ============================================================
# OBJETOS
# ============================================================

def load_object(path):
    lines = clean_lines(path)

    if not lines:
        raise ValueError("El archivo está vacío")

    first_line_number, first_line = lines[0]

    key, name = split_key_value(first_line, first_line_number)

    if key != "object":
        raise ValueError(
            f"Línea {first_line_number}: se esperaba 'object'")

    values = {}

    for line_number, line in lines[1:]:
        key, value = split_key_value(line, line_number)

        if key in values:
            raise ValueError(
                f"Línea {line_number}: clave duplicada '{key}'")

        values[key] = value

    required = {"char", "resource_max",}

    missing = required - values.keys()

    if missing:
        raise ValueError(
            "Faltan claves: " + ", ".join(missing))

    char = values["char"]

    if len(char) != 1:
        raise ValueError("'char' debe ser un solo carácter")

    try:
        resource_max = int(values["resource_max"])

    except ValueError:
        raise ValueError(
            "'resource_max' debe ser entero"
        )

    return WorldObject(
        name=name,
        char=char,
        resource_max=resource_max
    )


# ============================================================
# CRIATURAS .INS
# ============================================================

def load_creature(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        source = file.read()

    tokens = Lexer(
        source
    ).tokenize()

    program = Parser(
        tokens
    ).parse()

    SemanticAnalyzer(
        program
    ).validate()

    return program


# ============================================================
# MAPAS
# ============================================================

def load_map(
    path,
    terrains,
    objects
):
    lines = read_lines(path)

    if not lines:
        raise ValueError(
            "El mapa está vacío"
        )

    map_name = lines[0].strip()

    if not map_name:
        raise ValueError(
            "La primera línea debe contener "
            "el nombre del mapa"
        )

    rows = [
        line.rstrip("\n\r")
        for line in lines[1:]
    ]

    # Quitamos solo líneas vacías del final.
    while rows and rows[-1] == "":
        rows.pop()

    if not rows:
        raise ValueError(
            "El mapa no contiene casillas"
        )

    width = len(rows[0])

    if width == 0:
        raise ValueError(
            "Las filas del mapa no pueden estar vacías"
        )

    for index, row in enumerate(
        rows,
        start=2
    ):
        if len(row) != width:
            raise ValueError(
                f"Línea {index}: "
                "todas las filas deben tener "
                "el mismo largo"
            )

    if not terrains:
        raise ValueError(
            "No hay terrenos cargados"
        )

    # --------------------------------------------------------
    # CHAR -> DEFINICIÓN
    # --------------------------------------------------------

    terrain_by_char = {
        terrain.char: terrain
        for terrain in terrains.values()
    }

    object_by_char = {
        obj.char: obj
        for obj in objects.values()
    }

    # El primer terreno cargado es el terreno base
    # debajo de los objetos.
    base_terrain = next(
        iter(terrains.values())
    )

    # --------------------------------------------------------
    # VALIDAR CARACTERES
    # --------------------------------------------------------

    for y, row in enumerate(rows):

        for x, char in enumerate(row):

            if (
                char not in terrain_by_char
                and char not in object_by_char
            ):
                raise ValueError(
                    f"Línea {y + 2}: "
                    f"carácter desconocido '{char}'"
                )

    # --------------------------------------------------------
    # CREAR MUNDO
    # --------------------------------------------------------

    world = World(
        width=width,
        height=len(rows)
    )

    for y, row in enumerate(rows):

        for x, char in enumerate(row):

            cell = world.get_cell(
                x,
                y
            )

            # -----------------------------------------------
            # TERRENO
            # -----------------------------------------------

            if char in terrain_by_char:

                template = terrain_by_char[char]

                cell.terrain = Terrain(
                    name=template.name,
                    char=template.char,
                    resource_max=template.resource_max,
                    regen=template.regen
                )

                continue

            # -----------------------------------------------
            # OBJETO
            # -----------------------------------------------

            object_template = object_by_char[
                char
            ]

            # Debajo del objeto va el primer terreno
            # declarado/cargado.
            cell.terrain = Terrain(
                name=base_terrain.name,
                char=base_terrain.char,
                resource_max=base_terrain.resource_max,
                regen=base_terrain.regen
            )

            cell.object = WorldObject(
                name=object_template.name,
                char=object_template.char,
                resource_max=object_template.resource_max
            )

    return map_name, world


# ============================================================
# CARGADOR GENERAL
# ============================================================

class ProjectLoader:

    def __init__(self, base_directory="."):
        self.base_directory = Path(
            base_directory
        )

        self.terrains = {}
        self.objects = {}
        self.maps = {}
        self.creatures = {}

        self.logs = []

        self.used_chars = {}


    # ========================================================
    # CARGAR TODO
    # ========================================================

    def load_all(self):
        self.load_terrains()
        self.load_objects()
        self.load_maps()
        self.load_creatures()

        return self


    # ========================================================
    # TERRENOS
    # ========================================================

    def load_terrains(self):
        directory = (
            self.base_directory
            / "terrains"
        )

        if not directory.exists():
            self.logs.append(
                "No existe la carpeta terrains/"
            )
            return

        for path in sorted(
            directory.glob("*.te")
        ):

            try:
                terrain = load_terrain(
                    path
                )

                self.validate_char(
                    terrain.char,
                    path
                )

                self.terrains[
                    terrain.name
                ] = terrain

            except Exception as error:
                self.logs.append(
                    f"{path.name}: {error}"
                )


    # ========================================================
    # OBJETOS
    # ========================================================

    def load_objects(self):
        directory = (
            self.base_directory
            / "objects"
        )

        if not directory.exists():
            self.logs.append(
                "No existe la carpeta objects/"
            )
            return

        for path in sorted(
            directory.glob("*.ob")
        ):

            try:
                obj = load_object(
                    path
                )

                self.validate_char(
                    obj.char,
                    path
                )

                self.objects[
                    obj.name
                ] = obj

            except Exception as error:
                self.logs.append(
                    f"{path.name}: {error}"
                )


    # ========================================================
    # MAPAS
    # ========================================================

    def load_maps(self):
        directory = (
            self.base_directory
            / "maps"
        )

        if not directory.exists():
            self.logs.append(
                "No existe la carpeta maps/"
            )
            return

        for path in sorted(
            directory.glob("*.map")
        ):

            try:
                name, world = load_map(
                    path,
                    self.terrains,
                    self.objects
                )

                self.maps[
                    name
                ] = world

            except Exception as error:
                self.logs.append(
                    f"{path.name}: {error}"
                )


    # ========================================================
    # CRIATURAS
    # ========================================================

    def load_creatures(self):
        directory = (
            self.base_directory
            / "creatures"
        )

        if not directory.exists():
            self.logs.append(
                "No existe la carpeta creatures/"
            )
            return

        for path in sorted(
            directory.glob("*.ins")
        ):

            try:
                program = load_creature(
                    path
                )

                self.creatures[
                    program.header.creature
                ] = program

            except Exception as error:
                self.logs.append(
                    f"{path.name}: {error}"
                )


    # ========================================================
    # CHAR ÚNICO
    # ========================================================

    def validate_char(
        self,
        char,
        path
    ):
        if char in self.used_chars:

            previous = self.used_chars[
                char
            ]

            raise ValueError(
                f"el char '{char}' ya fue usado "
                f"por {previous}"
            )

        self.used_chars[
            char
        ] = path.name