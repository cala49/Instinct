from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from __feature__ import snake_case, true_property

class MapView(QGraphicsView):

    def __init__(self):
        super().__init__()
    pass


class Ventana(QMainWindow):

    def __init__(self, simulador):
        super().__init__()
        
        self.simulador = simulador
        
        self.resize(900,650)

        self.timer = QTimer()
        self.timer.timeout.connect(self.excecute_tick)

        #Layout Principal

        self.main_layout = QVBoxLayout()

        #Layout superior

        self.top_layout = QHBoxLayout()

        #Panel izquierdo

        self.left_panel = QFrame()
        self.left_panel.style_sheet = "background: black; color: gold"
        self.left_panel.set_fixed_width(220)

        left_layout = QVBoxLayout()

        #Lista de Mapas

        left_layout.add_widget(QLabel("Mapas disponibles:"))
        self.list_maps = QListWidget()
        self.list_maps.add_items(["Isla de los Piratas","Marineford","East Blue"])

        left_layout.add_widget(self.list_maps)

        #Lista de especies
          
        left_layout.add_widget(QLabel("Lista de especies"))
        self.list_species = QListWidget()
        self.list_species.add_items(["Pirata","Marine","Espadachin"])

        left_layout.add_widget(self.list_species)
        
        self.left_panel.set_layout(left_layout)
        
        #Panel Central 

        self.center_panel = QFrame()
        self.center_panel.style_sheet = "background: blue; color: gold;"

        center_layout = QVBoxLayout()

        #Creamos la escena y la añadimos al mapa para mostrarla

        self.scene = QGraphicsScene()
        self.map_view = MapView()
        self.map_view.set_scene(self.scene)

        self.draw_grid()
        
        center_layout.add_widget(self.map_view)

        #Controles de Simulacion

        controls_layout = QHBoxLayout()

        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play_simulation)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_simulation)

        self.btn_step = QPushButton("Step")
        self.btn_step.clicked.connect(self.excecute_tick)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_simulation)

        #Selector de velocidad

        self.combo_speed = QComboBox()
        self.combo_speed.add_items(["x1","x2","x10"])
        self.combo_speed.currentIndexChanged.connect(self.change_speed)

        controls_layout.add_widget(self.btn_play)
        controls_layout.add_widget(self.btn_pause)
        controls_layout.add_widget(self.btn_step)
        controls_layout.add_widget(self.btn_reset)
        controls_layout.add_widget(QLabel("Velocidad"))
        controls_layout.add_widget(self.combo_speed)
        
        center_layout.add_layout(controls_layout)
        self.center_panel.set_layout(center_layout)

        #Agregamos al layout superior los paneles para organizar la parte de arriba de la ventana

        self.top_layout.add_widget(self.left_panel)
        self.top_layout.add_widget(self.center_panel)

        #Panel inferior

        self.bottom_panel = QFrame()
        self.bottom_panel.style_sheet = "background: lightblack; color: gold;"
        self.bottom_panel.set_fixed_height(150)

        bottom_layout = QVBoxLayout()

        self.label_logs = QLabel("Consola de logs: Esperando eventos")
        self.label_logs.style_sheet = "color: gold; font-family: monospace"
        self.label_logs.alignment = Qt.AlignCenter

        bottom_layout.add_widget(self.label_logs)
        
        self.bottom_panel.set_layout(bottom_layout)

        #Unimos todo en el layout principal

        self.main_layout.add_layout(self.top_layout)
        self.main_layout.add_widget(self.bottom_panel)

        #Ponemos todo en la ventana principal 
    
        self.widget = QWidget()
        self.widget.set_layout(self.main_layout)
        self.set_central_widget(self.widget)

    current_interval = 1000 

    #M'etodos

    def draw_grid(self):

        self.scene.clear()
        rows = 10
        cols = 10
        tile_size = 32

        bg_color = QBrush(QColor("#a0d8ef"))
        line_color = QPen(QColor("#555555"))

        for row in range(rows):
            for col in range(cols):

                x = col * tile_size
                y = row * tile_size

                rect = QRect(x, y, tile_size, tile_size)

                tile = self.scene.add_rect(rect, line_color, bg_color)

                tile.set_data(0, row)
                tile.set_data(1, col)

        self.scene.scene_rect = QRect(0, 0, float(cols * tile_size), float(rows * tile_size))          

    def excecute_tick(self):

        self.simulador.step()
        state = self.simulador.get_state()
        self.render(state)
        self.label_logs.text = f"Turno {state['tick']} ejecutado"

    def play_simulation(self):

        self.timer.start(self.current_interval)
        self.label_logs.text = "Simulación iniciada"

    def pause_simulation(self):

        self.timer.stop()
        self.label_logs.text = "Simulación pausada"

    def reset_simulation(self):

        self.timer.stop()
        self.simulador.reset()
        state = self.simulador.get_state()
        self.render(state)
        self.label_logs.text = "Simulación reiniciada"

    def change_speed(self,index):

        if index == 0:
            self.current_interval = 1000

        elif index == 1:
            self.current_interval = 500

        elif index == 2:
            self.current_interval = 100

        if self.timer.active:
            self.timer.stop()
            self.timer.start(self.current_interval)               

        self.label_logs.text = f"Velocidad cambiada a : {self.combo_speed.current_text}"

    def render(self,state):

        pass