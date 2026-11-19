from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class MapView(QGraphicsView):

    def __init__(self, parent_ventana):
        super().__init__()
        self.ventana = parent_ventana

    def clear_creatures(self):

        for item in self.scene().items():

            if isinstance(item, QGraphicsTextItem):
                self.scene().removeItem(item)    
    
    def mousePressEvent(self,event):

        pos_pixel = event.position().toPoint()

        item = self.itemAt(pos_pixel)

        if item and isinstance(item, QGraphicsRectItem):
            row = item.data(0)
            col = item.data(1)

            if event.button() == Qt.LeftButton:
                selected_items = self.ventana.list_species.selectedItems()

                if selected_items:

                    species_name = selected_items[0].text()

                    self.ventana.simulador.place_creature(row, col, species_name)

                    state = self.ventana.simulador.get_state()
                    self.ventana.render(state)

                    self.ventana.log_message(f"Colocaste un {species_name} ! Fila: {row} Columna: {col}")

            elif event.button == Qt.RightButton:

                state = self.ventana.silulador.get_state()

                if (row,col) in state["creatures"]:

                    self.ventana.simulador.remove_creature(row,col)
                    self.ventana.render(state)
                    self.ventana.log_message(f"Criatura eliminanda en Fila: {row} Columna: {col}")
                else:
                    self.ventana.log_message("No hay ninguna criatura en esa casilla")    

        super().mousePressEvent(event)


class Ventana(QMainWindow):

    def __init__(self, simulador):
        super().__init__()
        
        self.simulador = simulador
        
        self.resize(900,650)

        self.timer = QTimer()
        self.timer.timeout.connect(self.execute_tick)

        # Layout Principal

        self.main_layout = QVBoxLayout()

        # Layout superior

        self.top_layout = QHBoxLayout()

        # Panel izquierdo

        self.left_panel = QFrame()
        self.left_panel.setStyleSheet("background: black; color: gold")
        self.left_panel.setFixedWidth(220)

        left_layout = QVBoxLayout()

        # Lista de Mapas

        left_layout.addWidget(QLabel("Mapas disponibles:"))
        self.list_maps = QListWidget()
        self.list_maps.addItems(["Isla de los Piratas","Marineford","East Blue"])

        left_layout.addWidget(self.list_maps)

        # Lista de especies
          
        left_layout.addWidget(QLabel("Lista de especies"))
        self.list_species = QListWidget()
        self.list_species.addItems(["Pirata","Marine","Espadachin"])

        left_layout.addWidget(self.list_species)
        
        self.left_panel.setLayout(left_layout)
        
        # Panel Central 

        self.center_panel = QFrame()
        self.center_panel.setStyleSheet("background: blue; color: gold;")

        center_layout = QVBoxLayout()

        # Creamos la escena y la añadimos al mapa para mostrarla

        self.scene = QGraphicsScene()
        self.map_view = MapView(self)
        self.map_view.setScene(self.scene)

        self.draw_grid()
        
        center_layout.addWidget(self.map_view)

        # Controles de Simulación

        controls_layout = QHBoxLayout()

        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play_simulation)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_simulation)

        self.btn_step = QPushButton("Step")
        self.btn_step.clicked.connect(self.execute_tick)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_simulation)

        # Selector de velocidad

        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["x1","x2","x10"])
        self.combo_speed.currentIndexChanged.connect(self.change_speed)

        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_step)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(QLabel("Velocidad"))
        controls_layout.addWidget(self.combo_speed)
        
        center_layout.addLayout(controls_layout)
        self.center_panel.setLayout(center_layout)

        # Agregamos al layout superior los paneles para organizar la parte de arriba de la ventana

        self.top_layout.addWidget(self.left_panel)
        self.top_layout.addWidget(self.center_panel)

        # Panel inferior

        self.bottom_panel = QFrame()
        self.bottom_panel.setStyleSheet("background: black; color: gold; font: 14px;")
        self.bottom_panel.setFixedHeight(150)

        bottom_layout = QVBoxLayout()

        self.label_logs = QPlainTextEdit()
        self.label_logs.setReadOnly(True)
        self.label_logs.setStyleSheet("color: gold; font-family: monospace")

        self.label_logs.setPlainText("Esperando eventos...")

        bottom_layout.addWidget(self.label_logs)
        
        self.bottom_panel.setLayout(bottom_layout)

        # Unimos todo en el layout principal

        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.bottom_panel)

        # Ponemos todo en la ventana principal 
    
        self.widget = QWidget()
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

    current_interval = 1000 

    # Métodos

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

                tile = self.scene.addRect(rect, line_color, bg_color)

                tile.setData(0, row)
                tile.setData(1, col)

        self.scene.sceneRect = QRect(0, 0, float(cols * tile_size), float(rows * tile_size))          

    def execute_tick(self):

        self.simulador.step()
        state = self.simulador.get_state()
        self.render(state)
        self.log_message(f"Turno {state['tick']} ejecutado")

    def play_simulation(self):

        self.timer.start(self.current_interval)
        self.log_message("Simulación iniciada")

    def pause_simulation(self):

        self.timer.stop()
        self.log_message("Simulación pausada")

    def reset_simulation(self):

        self.timer.stop()
        self.simulador.reset()

        self.map_view.clear_creatures()
        self.label_logs.clear()

        state = self.simulador.get_state()
        self.render(state)
        self.log_message("Simulación reiniciada")

    def change_speed(self,index):

        if index == 0:
            self.current_interval = 1000

        elif index == 1:
            self.current_interval = 500

        elif index == 2:
            self.current_interval = 100

        if self.timer.isActive:
            self.timer.stop()
            self.timer.start(self.current_interval)               

        self.log_message(f"Velocidad cambiada a : {self.combo_speed.currentText()}")

    def render(self,state):

        self.map_view.clear_creatures()

        creatures = state.get("creatures", {})

        for (row, col), species_name in creatures.items():
            self.draw_creature(row, col, species_name)

    def draw_creature(self, row, col, species_name):
        
        letter = species_name[0].upper()

        tile_size = 32
        x = col * tile_size
        y = row * tile_size

        text_item = self.scene.addText(letter)

        text_bounds = text_item.boundingRect()

        text_item.setPos(
            x + (tile_size/2) - (text_bounds.width()/2),
            y + (tile_size/2) - (text_bounds.height()/2)
        )       

    def log_message(self, message):

        self.label_logs.appendPlainText(f"> {message}")