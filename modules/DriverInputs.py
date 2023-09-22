from __future__ import annotations

import logging
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QSlider, QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFontDatabase
from ..modules.Telemetry import TelemetryRT
import sys
import matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

#style.use("dark_background")

log = logging.getLogger(__name__)


class DriverInputs(QWidget):
    def __init__(self):
        super(DriverInputs, self).__init__()

        self.time_axis = []
        self.gas_data = []
        self.brake_data = []

        self.gas_20s = []
        self.brake_20s = []
        self.time_20s = []
        self.layout = QVBoxLayout()

        self.figure = Figure()
        self.figure.get_figure = Figure(figsize=(6.5, 4.5), dpi=100)
        self.figure.subplots_adjust(left=0.125,
                                    bottom=0.1,
                                    right=0.9,
                                    top=0.9,
                                    wspace=0.2,
                                    hspace=0.7)
        
        self.gas_graph = self.figure.add_subplot(2, 1, 1)
        self.brake_graph = self.figure.add_subplot(2, 1, 2)

        self.start_lap_time = 0

        self.gas_line,  = self.gas_graph.plot(
            self.time_20s, self.gas_20s,
            "#00FF00",
            label="Gas")

        self.brake_line,  = self.brake_graph.plot(
            self.time_20s, self.brake_20s,
            "#FF0000",
            label="Brake")

        self.gas_graph.set_title("Throttle input over time")
        self.gas_graph.set_xlabel("Time (Seconds)")
        self.gas_graph.set_ylabel("Throttle (%)")
        self.gas_graph.set_xlim(0, 1)
        self.gas_graph.set_ylim(-5, 105)

        self.brake_graph.set_title("Brake input over time")
        self.brake_graph.set_xlabel("Time (Seconds)")
        self.brake_graph.set_ylabel("Brake (%)")
        self.brake_graph.set_xlim(0, 1)
        self.brake_graph.set_ylim(-5, 105)

        self.gas_graph.set_xlim(10, 0)
        self.brake_graph.set_xlim(10, 0)

        self.canvas = FigureCanvas(self.figure, self)
        self.ani = animation.FuncAnimation(self.figure, self._animate,
                                           interval=100, blit=False)
        self.ani.event_source.stop()
        self.layout.addWidget(self.ani)

        # Styling
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(0, 255, 0))


        # Gas and Brake Progress Bars
        self.gas_label = QLabel("Gas:")
        self.gas_progress = QProgressBar()
        # Basic Blue with Rounded Corners:
        # self.gas_progress.setStyleSheet("""
        #     QProgressBar {border: 2px solid grey; border-radius: 8px; text-align: center;}
        #     QProgressBar::chunk {background-color: #05B8CC; width: 10px; margin: 0.5px;}
        # """)
        # Modern Gray with Stripes:
        # self.gas_progress.setStyleSheet("""
        #     QProgressBar {border: 2px solid grey; border-radius: 4px; background-color: #D8D8D8; text-align: center;}
        #     QProgressBar::chunk {background-color: #B4B4B4; background-image: url(stripe.png); background-position: 0px 0px;}
        # """)
        # Green Gradient Fill:
        # self.gas_progress.setStyleSheet("""
        #     QProgressBar {border: 2px solid grey; border-radius: 4px; text-align: center;}
        #     QProgressBar::chunk {background-color: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #00FF00, stop: 1 #008800); }
        # """)
        #Red with Outer Glow:
        # self.gas_progress.setStyleSheet("""
        #     QProgressBar {border: 0px solid grey; border-radius: 4px; text-align: center; background: transparent;}
        #     QProgressBar::chunk {background-color: #FF0000; border-radius: 4px; border: 1px solid #900000;}
        # """)
        # Yellow with Transparent Background:
        self.gas_progress.setStyleSheet("""
        QProgressBar {border: 2px solid transparent; border-radius: 4px; background: transparent; text-align: center;  background-color: #333333;}
        QProgressBar::chunk {background-color: #05B8CC; width: 10px; margin: 0.5px;}
        """)

        self.gas_progress.setPalette(palette)
        self.layout.addWidget(self.gas_label)
        self.layout.addWidget(self.gas_progress)

        self.brake_label = QLabel("Brake:")
        self.brake_progress = QProgressBar()
        self.brake_progress.setStyleSheet("""
        QProgressBar {border: 2px solid transparent; border-radius: 4px; background: transparent; text-align: center;  background-color: #333333;}
        QProgressBar::chunk {background-color: #05B8CC; width: 10px; margin: 0.5px;}
        """)
        self.brake_progress.setPalette(palette)
        self.layout.addWidget(self.brake_label)
        self.layout.addWidget(self.brake_progress)

        # Steering Slider
        self.steering_label = QLabel("Steering:")
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #333333;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #05B8CC;
                border: 1px solid #05B8CC;
                width: 18px;
                margin: -2px 0;
                border-radius: 4px;
            }
        """)
        self.steering_slider.setMinimum(-100)
        self.steering_slider.setMaximum(100)
        self.steering_slider.setPalette(palette)
        self.layout.addWidget(self.steering_label)
        self.layout.addWidget(self.steering_slider)

        # Gear and Speed Labels
        self.gear_label = QLabel("1", self)
        self.gear_label.setStyleSheet(f"""
            QLabel {{
                font: bold 24px;
                color: #05B8CC;
                background-color: #333333;
                border: 2px solid #999999;
                border-radius: 8px;
                padding: 4px;
                text-align: center;
            }}
        """)
        self.speed_label = QLabel("0", self)
        self.speed_label.setStyleSheet(f"""
            QLabel {{
                font: bold 24px;
                color: #05B8CC;
                background-color: #333333;
                border: 2px solid #999999;
                border-radius: 8px;
                padding: 4px;
                text-align: center;
            }}
        """)
        self.layout.addWidget(self.gear_label)
        self.layout.addWidget(self.speed_label)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(100)  # Update every 100ms

    def _animate(self, i) -> None:

        if len(self.time_axis) == 0:
            return

        self.gas_line.set_data(self.time_20s, self.gas_20s)
        self.brake_line.set_data(self.time_20s, self.brake_20s)

    def reset(self) -> None:

        self.time_axis.clear()
        self.gas_data.clear()
        self.brake_data.clear()
        self.start_lap_time = 0

    def stop_animation(self) -> None:
        self.ani.event_source.stop()

    def start_animation(self) -> None:
        self.ani.event_source.start()

    def update_values(self):

        gas_value = TelemetryRT.gas.as_integer_ratio(0, 100)
        brake_value = TelemetryRT.brake.as_integer_ratio(0, 100)
        steering_value = TelemetryRT.streering_angle.as_integer_ratio(-100, 100)
        gear_value = TelemetryRT.gear.as_integer_ratio(1, 6)
        speed_value = TelemetryRT.speed.as_integer_ratio(0, 200)

        self.gas_progress.setValue(gas_value)
        self.brake_progress.setValue(brake_value)
        self.steering_slider.setValue(steering_value)
        self.gear_label.setText(f"Gear: {gear_value}")
        self.speed_label.setText(f"Speed: {speed_value} KPH")
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

    window = DriverInputs()
    window.show()
    sys.exit(app.exec_())
