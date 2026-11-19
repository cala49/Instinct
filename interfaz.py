from PySide6.QtWidgets import *
from PySide6.QtCore import *
from __feature__ import snake_case, true_property


class Ventana(QMainWindow):

    def __init__(self, simulador):
        super().__init__()
        
        self.simulador = simulador
        
        self.resize(800,600)

        #Layout Principal

        self.main_layout = QVBoxLayout()

        #Layout superior

        self.top_layout = QHBoxLayout()

        #Panel izquierdo

        self.left_panel = QFrame()
        self.left_panel.style_sheet = "background: black; color: gold"
        self.left_panel.set_fixed_width(200)

        left_layout = QVBoxLayout()

        self.label_species = QLabel("Lista de especies")
        self.label_species.style_sheet = "color: gold"
        self.label_species.alignment = Qt.AlignCenter

        left_layout.add_widget(self.label_species)

        self.button = QPushButton("Step")
        self.button.style_sheet = ("background: gray; color: gold;")
        self.button.set_fixed_size(80,30)

        self.button.clicked.connect(self.excecute_tick)
        
        left_layout.add_widget(self.button, alignment = Qt.AlignBottom) #coloca el bottom abajo
        
        self.left_panel.set_layout(left_layout)
        
        #Panel Central 

        self.center_panel = QFrame()
        self.center_panel.style_sheet = "background: blue; color: gold;"

        center_layout = QVBoxLayout()

        self.label_state = QLabel("Esperando inicio...")
        self.label_state.alignment = Qt.AlignCenter
        self.label_state.style_sheet = "font-size: 20px; color: gold"

        center_layout.add_widget(self.label_state)

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

    def excecute_tick(self):

        self.simulador.step()
        state = self.simulador.get_state()
        self.render(state)

    def render(self,state):

        self.label_state.text = f"Tick actual: {state['tick']}"
