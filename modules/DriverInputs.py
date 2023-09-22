from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFontDatabase
import random
import sys

class DriverInputs(QWidget):
    def __init__(self):
        super(DriverInputs, self).__init__()

        self.layout = QVBoxLayout()

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

    def update_values(self):
        gas_value = random.randint(0, 100)
        brake_value = random.randint(0, 100)
        steering_value = random.randint(-100, 100)
        gear_value = random.randint(1, 6)
        speed_value = random.randint(0, 200)

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
