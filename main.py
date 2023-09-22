from __future__ import annotations

#import ipaddress
import json
import logging
#import struct
import sys
import time
import tkinter
#import zlib
from dataclasses import astuple
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional, Tuple

#import dns
# dns.resolver
from idlelib.tooltip import Hovertip
from twisted.internet import reactor, task, tksupport
from modules.ACCTrainer import (FuelMonitor, accSharedMemory, log_telemetry_data, ACC_map)
#from modules.Client import ClientInstance
from modules.Common import (CarInfo, NetData,
                            NetworkQueue)
from modules.DriverInputs import DriverInputs
#from modules.Server import ServerInstance
#from modules.Strategy import StrategyUI
from modules.Telemetry import Telemetry, TelemetryRT, TelemetryUI
from modules.TyreGraph import PrevLapsGraph, TyreGraph
from modules.TyreSets import TyreSets, TyresSetData
from modules.Users import UserUI

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s.%(msecs)03d | %(name)s | %(message)s",
                    datefmt="%H:%M:%S")


_VERSION_ = "0.0.1"


class App(tkinter.Tk):

    def __init__(self) -> None:

        tkinter.Tk.__init__(self)

        tksupport.install(self)

        self.geometry("830x580+0+0")

        try:
            with open("./Config/gui.json", "r") as fp:

                self.gui_config = json.load(fp)

        except FileNotFoundError:
            print("APP: './Config/gui.json' not found.")
            sys.exit(1)

        self.font = (self.gui_config["font"], self.gui_config["font_size"])

        app_style = ttk.Style(self)
        app_style.configure('.',
                            font=self.font,
                            background=self.gui_config["background_colour"],
                            foreground=self.gui_config["foreground_colour"])

        app_style.configure('TNotebook.Tab', foreground="#000000")
        app_style.configure('TButton', foreground="#000000")
        app_style.configure('TCombobox', foreground="#000000")

        app_style.configure("ActiveDriver.TLabel",
                            background=self.gui_config["active_driver_colour"])

        app_style.configure("Fuel.TFrame", background="#000000")
        app_style.configure("TelemetryGrid.TFrame", background="#000000")
        app_style.configure("PressureInfo.TFrame", background="#000000")
        app_style.configure("TEntry", foreground="#000000")

        self.title(f"ACCTrainer {_VERSION_}")
        self.config(bg="Grey")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.menu_bar = tkinter.Menu(self)
        self.menu_bar.add_command(label="Log",
                                  command=log_telemetry_data,
                                  font=self.font)

        self.config(menu=self.menu_bar)

        self.main_canvas = tkinter.Canvas(self)
        self.main_frame = ttk.Frame(self)

        self.hsb = ttk.Scrollbar(self)
        self.vsb = ttk.Scrollbar(self)

        self.main_canvas.config(xscrollcommand=self.hsb.set,
                                yscrollcommand=self.vsb.set,
                                highlightthickness=0)

        self.hsb.config(orient=tkinter.HORIZONTAL,
                        command=self.main_canvas.xview)
        self.vsb.config(orient=tkinter.VERTICAL,
                        command=self.main_canvas.yview)

        self.hsb.pack(fill=tkinter.X, side=tkinter.BOTTOM,
                      expand=tkinter.FALSE)
        self.vsb.pack(fill=tkinter.Y, side=tkinter.RIGHT,
                      expand=tkinter.FALSE)

        self.main_canvas.pack(fill=tkinter.BOTH, side=tkinter.LEFT,
                              expand=tkinter.TRUE)

        self.main_canvas.create_window(0, 0, window=self.main_frame,
                                       anchor=tkinter.NW)

        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.grid(row=0, column=0, pady=3)

        self.trainer_ui = accSharedMemory(self.tab_control)
        self.trainer_ui.pack(fill=tkinter.BOTH, side=tkinter.LEFT,
                               expand=tkinter.TRUE)

        self.telemetry_ui = TelemetryUI(self.tab_control)
        self.telemetry_ui.pack(fill=tkinter.BOTH, side=tkinter.LEFT,
                               expand=tkinter.TRUE)

        self.driver_inputs = DriverInputs(self.tab_control)
        self.driver_inputs.pack(fill=tkinter.BOTH, side=tkinter.LEFT,
                                expand=tkinter.TRUE)

        self.tyre_graph = TyreGraph(self.tab_control, self.gui_config)
        self.tyre_graph.pack(fill=tkinter.BOTH, expand=1)

        self.prev_lap_graph = PrevLapsGraph(self.tab_control, self.gui_config)
        self.prev_lap_graph.pack(fill=tkinter.BOTH, expand=1)

        self.tyre_sets = TyreSets(self.tab_control, self.gui_config)
        self.tyre_sets.pack(fill=tkinter.BOTH, expand=1)

        self.tab_control.add(self.trainer_ui, text="Trainer")
        self.tab_control.add(self.telemetry_ui, text="Telemetry")
        self.tab_control.add(self.driver_inputs, text="Driver Inputs")
        self.tab_control.add(self.tyre_graph, text="Pressures")
        self.tab_control.add(self.prev_lap_graph, text="Previous Laps")
        self.tab_control.add(self.tyre_sets, text="Tyre Sets")

        self.tab_control.hide(0)

        self.last_time = time.time()
        self.rt_last_time = time.time()
        self.rt_min_delta = self.gui_config["driver_input_speed"]
        self.min_delta = 0.5
        self.last_telemetry = time.time()
        self.telemetry_timeout = 2

        logging.info("Main UI created.")

        self.client_loopCall = task.LoopingCall(self.client_loop)
        self.client_loopCall.start(0.01)

        self.eval('tk::PlaceWindow . center')
        self.updateScrollRegion()

    def updateScrollRegion(self):

        self.main_canvas.update_idletasks()
        self.main_canvas.config(scrollregion=self.main_frame.bbox())

    def client_loop(self) -> None:

        selected_tab_name = self.tab_control.tab(self.tab_control.select(),
                                                 "text")
        if selected_tab_name == "Driver Inputs":
            if not self.driver_inputs.is_animating:
                self.driver_inputs.start_animation()

        else:
            if self.driver_inputs.is_animating:
                self.driver_inputs.stop_animation()

        if selected_tab_name == "Pressures":
            if not self.tyre_graph.is_animating:
                self.tyre_graph.start_animation()

        else:
            if self.tyre_graph.is_animating:
                self.tyre_graph.stop_animation()
                
        if self.telemetry_ui.driver_swap or self.user_ui.active_user is None:
            if self.telemetry_ui.current_driver is not None:
                self.user_ui.set_active(self.telemetry_ui.current_driver)
                self.telemetry_ui.driver_swap = False
                self.trainer_ui.read_shared_memory_with_retry(self.trainer_ui.get_shared_memory_data)

        rt_delta_time = time.time() - self.rt_last_time
        delta_time = time.time() - self.last_time

        asm_data = self.trainer_ui()
        if asm_data is not None:

            if self.rt_min_delta < rt_delta_time:

                self.rt_last_time = time.time()

                telemetry_rt = TelemetryRT(
                    asm_data.Physics.gas,
                    asm_data.Physics.brake,
                    asm_data.Physics.steer_angle,
                    asm_data.Physics.gear,
                    asm_data.Physics.speed_kmh
                )

                
            if self.min_delta < delta_time:

                self.last_time = time.time()

                infos = CarInfo(
                    *astuple(asm_data.Graphics.mfd_tyre_pressure),
                    asm_data.Graphics.mfd_fuel_to_add,
                    asm_data.Static.max_fuel,
                    asm_data.Graphics.mfd_tyre_set)

                # Telemetry
                name = asm_data.Static.player_name.split("\x00")[0]
                surname = asm_data.Static.player_surname.split("\x00")[0]
                driver = f"{name} {surname}"

                telemetry_data = Telemetry(
                    driver,
                    asm_data.Graphics.completed_lap,
                    asm_data.Physics.fuel,
                    asm_data.
                    asm_data.Graphics.fuel_per_lap,
                    asm_data.Graphics.fuel_estimated_laps,
                    asm_data.Physics.pad_life,
                    asm_data.Physics.disc_life,
                    asm_data.Graphics.current_time,
                    asm_data.Graphics.best_time,
                    asm_data.Graphics.last_time,
                    asm_data.Graphics.is_in_pit,
                    asm_data.Graphics.is_in_pit_lane,
                    asm_data.Graphics.session_type,
                    asm_data.Graphics.driver_stint_time_left,
                    asm_data.Physics.wheel_pressure,
                    asm_data.Physics.tyre_core_temp,
                    asm_data.Physics.brake_temp,
                    asm_data.Graphics.rain_tyres,
                    asm_data.Graphics.session_time_left,
                    asm_data.Graphics.track_grip_status,
                    asm_data.Physics.front_brake_compound,
                    asm_data.Physics.rear_brake_compound,
                    asm_data.Physics.car_damage,
                    asm_data.Graphics.rain_intensity,
                    asm_data.Physics.suspension_damage,
                    asm_data.Graphics.current_sector_index,
                    asm_data.Graphics.last_sector_time,
                    asm_data.Graphics.is_valid_lap,
                    asm_data.Physics.air_temp,
                    asm_data.Physics.road_temp,
                    asm_data.Graphics.wind_speed,
                    asm_data.Graphics.driver_stint_total_time_left,
                    asm_data.Graphics.current_tyre_set,
                )

                self.net_queue.q_in.append(NetData(NetworkQueue.Telemetry,
                                           telemetry_data.to_bytes()))

    def on_close(self) -> None:

        logging.info("Closing the app")

        self.strategy_ui.close()
        self.tyre_graph.close()
        self.prev_lap_graph.close()
        self.tyre_sets.close()

        self.client_loopCall.stop()

        tksupport.uninstall()

        reactor.stop()

        self.destroy()
        logging.info("App closed")


def create_gui() -> None:
    App()


def main():

    reactor.callLater(0, create_gui)
    reactor.run()


if __name__ == "__main__":

    main()