# ui/scada_app.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, 
                             QLabel, QSlider, QGraphicsView, QGraphicsScene, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from ui.scene_items import TankItem, PipeItem, ValveItem, DryChamberItem, FlowMeterItem, PumpOnPipe
from src.sewage_sim.sim import SewageSimulation
import datetime

class SCADAWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCADA Professional ULTRA - Final v5")
        self.resize(1550, 950)
        self.sim = SewageSimulation("config/default.yaml")
        
        # Inicjalizacja wydajności pomp
        for st in [self.sim.P1, self.sim.P2]:
            for p in st.pumps: p.q_nom_m3s = 0.0125

        main_layout = QVBoxLayout(self)
        top_row = QHBoxLayout()
        panel = QFrame(); panel.setFixedWidth(320)
        panel.setStyleSheet("background:#1a1a1a; color: white;")
        pv = QVBoxLayout(panel)
        
        pv.addWidget(QLabel("DOPŁYW 1 [%] (0-1000)"))
        self.s_in1 = self.create_slider(0, 1000, 100, pv)
        pv.addWidget(QLabel("DOPŁYW 2 [%] (0-1000)"))
        self.s_in2 = self.create_slider(0, 1000, 100, pv)
        pv.addSpacing(20)

        pv.addWidget(QLabel("WYDAJNOŚĆ POMP [%] (0-100)"))
        self.s_pump_speed = self.create_slider(0, 100, 100, pv)
        pv.addSpacing(20)

        pv.addWidget(QLabel("CZAS ROTACJI POMP [s]"))
        self.s_rot = self.create_slider(5, 600, 30, pv)
        pv.addSpacing(20)

        pv.addWidget(QLabel("RĘCZNE ZASUWY:"))
        h_v = QHBoxLayout()
        self.btn_z1 = QPushButton("Z1 OTW/ZAM"); self.btn_z1.clicked.connect(lambda: self.toggle_v("P1"))
        self.btn_z2 = QPushButton("Z2 OTW/ZAM"); self.btn_z2.clicked.connect(lambda: self.toggle_v("P2"))
        h_v.addWidget(self.btn_z1); h_v.addWidget(self.btn_z2); pv.addLayout(h_v)
        pv.addSpacing(20)

        pv.addWidget(QLabel("SYMULACJA AWARII:"))
        for s_n in ["P1", "P2"]:
            btns = QHBoxLayout()
            for i in range(2):
                btn = QPushButton(f"FAIL {s_n}{chr(65+i)}")
                btn.clicked.connect(lambda _, s=s_n, idx=i: self.trigger_fail(s, idx))
                btns.addWidget(btn)
            pv.addLayout(btns)
        
        btn_res = QPushButton("NAPRAW WSZYSTKO"); btn_res.clicked.connect(self.reset_all)
        btn_res.setStyleSheet("background: darkgreen; font-weight: bold; height: 50px;")
        pv.addWidget(btn_res); pv.addStretch(1)

        self.scene = QGraphicsScene(0, 0, 1600, 700)
        self.view = QGraphicsView(self.scene); self.view.setBackgroundBrush(QColor(15, 15, 15))
        top_row.addWidget(panel); top_row.addWidget(self.view); main_layout.addLayout(top_row, 3)
        
        self.console = QTextEdit(); self.console.setReadOnly(True)
        self.console.setStyleSheet("background: black; color: #00FF00; font-family: 'Consolas'; font-size: 22px;")
        self.console.setMaximumHeight(200); main_layout.addWidget(self.console)
        
        self._build_overview()
        self._last_alarms = set()
        self.timer = QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(50)

    def create_slider(self, mi, ma, v, layout):
        s = QSlider(Qt.Horizontal); s.setRange(mi, ma); s.setValue(v); layout.addWidget(s)
        return s

    def toggle_v(self, s):
        st = self.sim.P1 if s == "P1" else self.sim.P2
        st.manual_valve_closed = not getattr(st, 'manual_valve_closed', False)
        self.log(f"ZASUWA {s}: Zmiana manualna.")

    def trigger_fail(self, s, i):
        st = self.sim.P1 if s == "P1" else self.sim.P2
        st.pumps[i].state.failed = True
        self.log(f"AWARIA: {s}_{chr(65+i)}!")

    def reset_all(self):
        for st in [self.sim.P1, self.sim.P2]:
            for p in st.pumps: p.state.failed = False
            st.manual_valve_closed = False
        self.log("SYSTEM: Reset zakończony.")

    def log(self, msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{t}] {msg}")

    def _build_overview(self):
        self.t_houses1 = TankItem(100, 120, "Domy 1"); self.t_houses1.setPos(50, 300)
        self.t_p1 = TankItem(140, 180, "P1 Komora"); self.t_p1.setPos(300, 300)
        self.t_high = TankItem(100, 120, "Studnia"); self.t_high.setPos(650, 50)
        self.t_p2 = TankItem(140, 180, "P2 Zbiorczy"); self.t_p2.setPos(1100, 300)
        for t in [self.t_houses1, self.t_p1, self.t_high, self.t_p2]: self.scene.addItem(t)
        
        self.p1_st = DryChamberItem("Status P1"); self.p1_st.setPos(430, 550)
        self.p2_st = DryChamberItem("Status P2"); self.p2_st.setPos(1230, 550)
        self.scene.addItem(self.p1_st); self.scene.addItem(self.p2_st)
        
        self.z1 = ValveItem("Z1"); self.z1.setPos(220, 400); self.z2 = ValveItem("Z2"); self.z2.setPos(1000, 400)
        self.fm1 = FlowMeterItem(520, 330, "FM1"); self.fm2 = FlowMeterItem(1380, 330, "FM2")
        self.scene.addItem(self.z1); self.scene.addItem(self.z2); self.scene.addItem(self.fm1); self.scene.addItem(self.fm2)

        PipeItem([(150, 400), (300, 400)], "LINIA 1").attach_to_scene(self.scene)
        PipeItem([(440, 400), (600, 400), (600, 100), (650, 100)]).attach_to_scene(self.scene)
        PipeItem([(750, 100), (900, 100), (900, 400), (1100, 400)]).attach_to_scene(self.scene)
        PipeItem([(900, 10), (900, 100)], "DOMY 2").attach_to_scene(self.scene)
        PipeItem([(1240, 400), (1500, 400)]).attach_to_scene(self.scene)

        self.p1a_i = PumpOnPipe(); self.p1a_i.setPos(420, 400); self.scene.addItem(self.p1a_i)
        self.p1b_i = PumpOnPipe(); self.p1b_i.setPos(465, 400); self.scene.addItem(self.p1b_i)
        self.p2a_i = PumpOnPipe(); self.p2a_i.setPos(1215, 400); self.scene.addItem(self.p2a_i)
        self.p2b_i = PumpOnPipe(); self.p2b_i.setPos(1265, 400); self.scene.addItem(self.p2b_i)

    def tick(self):
        self.sim.inflow_mult_O1 = self.s_in1.value() / 100.0
        self.sim.inflow_mult_O2 = self.s_in2.value() / 100.0
        self.sim.P1.swap_limit = self.s_rot.value()
        self.sim.P2.swap_limit = self.s_rot.value()
        
        # Ustawienie prędkości pomp (0-100%)
        ps = self.s_pump_speed.value() / 100.0
        for st in [self.sim.P1, self.sim.P2]:
            for p in st.pumps: p.state.speed = ps

        self.sim.step()
        
        # Wyświetlanie w m3/h
        self.t_houses1.set_info(self.sim.sig.level_T1, self.sim.sig.q_in_O1 * 3600.0)
        self.t_p1.set_info(self.sim.P1.wet_well.level_m, self.sim.sig.q_p1_meas * 3600.0)
        self.t_high.set_info(self.sim.sig.level_T2, self.sim.sig.q_p1_meas * 3600.0)
        self.t_p2.set_info(self.sim.P2.wet_well.level_m, self.sim.sig.q_p2_meas * 3600.0)
        
        for s, n, ia, ib in [("P1", self.p1_st, self.p1a_i, self.p1b_i), ("P2", self.p2_st, self.p2a_i, self.p2b_i)]:
            st = self.sim.P1 if s == "P1" else self.sim.P2
            n.set_states(st.pumps[0].state.enabled, st.pumps[0].state.failed, st.pumps[1].state.enabled, st.pumps[1].state.failed)
            ia.is_on, ia.is_failed = st.pumps[0].state.enabled, st.pumps[0].state.failed
            ib.is_on, ib.is_failed = st.pumps[1].state.enabled, st.pumps[1].state.failed
            ia.update(); ib.update()

        self.z1.set_closed(self.sim.P1.inlet_valve_closed)
        self.z2.set_closed(self.sim.P2.inlet_valve_closed)
        self.fm1.set_value(self.sim.sig.q_p1_meas); self.fm2.set_value(self.sim.sig.q_p2_meas)
        
        cur_a = {a.code for a in self.sim.alarms.active_list()}
        for a in (cur_a - self._last_alarms): self.log(f"ALARM: {a}")
        self._last_alarms = cur_a