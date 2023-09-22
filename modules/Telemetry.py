from __future__ import annotations


import copy
import logging
import struct
from dataclasses import astuple, dataclass
from typing import ClassVar, List, Optional, Tuple
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QRectF
import sys

log = logging.getLogger(__name__)

@dataclass
class TelemetryRT:

    gas: float
    brake: float
    streering_angle: float
    gear: int
    speed: float

    byte_format: ClassVar[str] = "!3f i f"
    byte_size: ClassVar[int] = struct.calcsize(byte_format)

    def to_bytes(self) -> bytes:

        return struct.pack(self.byte_format, *astuple(self))

    @classmethod
    def from_bytes(cls, data: bytes) -> TelemetryRT:

        if len(data) > cls.byte_size:

            log.warning(f"Telemetry: Warning got packet of {len(data)} bytes")
            data = data[:cls.byte_size]

        unpacked_data = struct.unpack(cls.byte_format, data)

        return TelemetryRT(*unpacked_data)

class TyreInfo(QWidget):

    def __init__(self, parent=None, name: str = "", on_the_right: bool = True):
        super(TyreInfo, self).__init__(parent)

        # Initialization
        self.colours = [(32, 32, 255), (32, 255, 32), (255, 32, 32)]
        self.name = name
        self.on_the_right = on_the_right
        self.has_wet = False
        self.tyre_pressure = 0.0
        self.tyre_temp = 0.0
        self.brake_temp = 0.0
        self.pad_compound = 0
        self.pad_wear = 0.0
        self.disc_wear = 0.0
        self.tyre_canvas = QGraphicsView(self)
        self.tyre_scene = QGraphicsScene(self)
        self.tyre_canvas.setScene(self.tyre_scene)

        # Set size for the QGraphicsView
        self.tyre_canvas.setFixedSize(50, 100)
        row_count = 0
        # Create rectangles and add them to the scene
        self.tyre_rect = self.tyre_scene.addRect(QRectF(0, 0, 50, 100), Qt.NoPen, QColor("Grey"))
        self.brake_rect = self.tyre_scene.addRect(QRectF(0, 25, 15, 50), Qt.NoPen, QColor("Grey"))
        self.core_rect = self.tyre_scene.addRect(QRectF(15, 35, 35, 65), Qt.NoPen, QColor("Grey"))

        # Set QGraphicsView position on the parent QWidget (adjust these according to your layout)
        self.tyre_canvas.move(0, 0)

        # ... (rest of your initializations)
        self.tyre_range = {
            "dry": {
                "pressure": [26, 29],
                "temperature": [50, 120]
            },
            "wet": {
                "pressure": [28, 32],
                "temperature": [20, 70]
            },
            "gt4": {
                "pressure": [25, 28],
                "temperature": [40, 110]
            }
        }

        self.brake_range = {
            "front": [150, 850],
            "rear": [150, 750],
        }

        label_width = 16
        var_width = 5
        if on_the_right:
            label_column = 2
            var_column = 1
            tyre_column = 0
            #txt_anchor = 
            brake_x = 0
            core_x = 50

        else:
            label_column = 0
            var_column = 1
            tyre_column = 2
            #txt_anchor = tkinter.E
            brake_x = 35
            core_x = 35

        # Create and set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create labels
        self.l_tyre = QLabel(name)
        self.l_tyre_pressure = QLabel("Tyre pressure")
        self.l_tire_pressure_var = QLabel(self.l_tyre_pressure)

        # ... (rest of your labels)

        # Add labels to layout
        self.layout.addWidget(self.l_tyre, 0, 0)
        self.layout.addWidget(self.l_tyre_pressure, 1, 0)
        self.layout.addWidget(self.l_tire_pressure_var, 2, 0)

        # ... (rest of your layout placements)

        # Create custom drawing area (replacing canvas)
        self.drawing_area = QWidget()
        self.drawing_area.setMinimumSize(50, 100)
        self.layout.addWidget(self.drawing_area, 0, 1, 6, 1)

        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self.drawing_area)
        # ... (your custom drawing logic)

    def initUI(self):
        main_layout = QVBoxLayout()

        self.graphicsView = QGraphicsView()
        self.scene = QGraphicsScene()
        self.tyre_rect = self.scene.addRect(QRectF(0, 0, 50, 100), Qt.black, QColor("grey"))

        self.graphicsView.setScene(self.scene)
        main_layout.addWidget(self.graphicsView)

        # Tyre Pressure
        tyre_pressure_layout = QHBoxLayout()
        self.tyre_pressure_label = QLabel("Tyre Pressure (PSI):")
        self.tyre_pressure_value = QLabel("0")
        tyre_pressure_layout.addWidget(self.tyre_pressure_label)
        tyre_pressure_layout.addWidget(self.tyre_pressure_value)
        main_layout.addLayout(tyre_pressure_layout)

        # Other labels and value widgets can be added here in a similar fashion

        self.setLayout(main_layout)

    def update_values(self, pad_compound, pad_wear, disc_wear, has_wet, tyre_pressure, tyre_temp, brake_temp):
        # Update values
        self.tyre_pressure_value.setText(str(round(tyre_pressure, 1)) + " PSI")
        # Add other updates here

    def update_tyre_hud(self, pressure, temperature):
        # Your logic for updating colors
        color = QColor(*self.colours[0])  # Example color
        self.tyre_rect.setBrush(color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # font_database = QFontDatabase()
    # font_id = font_database.addApplicationFont("ACCTrainer/font/cs_regular.ttf")

    # # Check if the font is loaded correctly
    # if font_id == -1:
    #     print("Error loading font!")
    # else:
    #     font_families = QFontDatabase.applicationFontFamilies(font_id)
    #     if len(font_families) > 0:
    #         counter_strike_font_family = font_families[0]

    window = TyreInfo()
    window.show()
    sys.exit(app.exec_())