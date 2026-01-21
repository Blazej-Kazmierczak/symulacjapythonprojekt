# src/sewage_sim/sim.py
import yaml
import random
from dataclasses import dataclass
from .components import WetWell, Pump, FlowMeter, PumpStation
from .inflow import DiurnalRandomInflow, ConstantInflow
from .alarms import AlarmBook
from .control import control_station

@dataclass
class SimSignals:
    t: float = 0.0
    q_in_O1: float = 0.0      
    q_in_O2: float = 0.0      
    q_p1_meas: float = 0.0    
    q_p2_meas: float = 0.0    
    level_T1: float = 0.0     # Domy 1
    level_T2: float = 0.0     # Studnia
    level_T3: float = 0.0     # P2

class SewageSimulation:
    def __init__(self, cfg_path: str):
        with open(cfg_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

        self.dt = float(self.cfg["sim"]["dt_s"])
        self.rng = random.Random(int(self.cfg["sim"]["seed"]))
        self.alarms = AlarmBook()
        self.sig = SimSignals()

        self.P1 = self._build_station("P1", self.cfg["stations"]["P1"])
        self.P2 = self._build_station("P2", self.cfg["stations"]["P2"])

        self.inflow_O1 = DiurnalRandomInflow(0.005, 0.015, [7,8,19,20], 0.2, self.rng)
        self.inflow_O2 = ConstantInflow(q_m3s=0.008)

        self.inflow_mult_O1 = 1.0
        self.inflow_mult_O2 = 1.0

        # Zbiorniki pasywne
        self.T1_well = WetWell(area_m2=5.0, level_min_m=0, level_start_m=2, level_max_m=5, level_m=2.0)
        self.T2_well = WetWell(area_m2=4.0, level_min_m=0, level_start_m=1, level_max_m=5, level_m=1.0)

    def _build_station(self, name: str, cfg: dict) -> PumpStation:
        ww_cfg = cfg["wet_well"]
        ww = WetWell(float(ww_cfg["area_m2"]), 0.8, 2.0, 3.0, float(ww_cfg["initial_level_m"]))
        pumps = [Pump(p["name"], float(p["q_nom_m3s"]), float(p["efficiency"])) for p in cfg["pumps"]]
        flowm = FlowMeter(0.25, 10.0)
        st = PumpStation(name=name, wet_well=ww, pumps=pumps, flowmeter=flowm)
        st.inlet_valve_closed = False 
        st.manual_valve_closed = False
        st.swap_limit = 60.0
        return st

    def step(self):
        dt = self.dt
        s = self.sig

        #Generowanie dopływu
        s.q_in_O1 = self.inflow_mult_O1 * self.inflow_O1.flow(s.t)
        s.q_in_O2 = self.inflow_mult_O2 * self.inflow_O2.flow(s.t)

        #Logika Sterowania
        control_station(self.P1, self.alarms, dt)
        control_station(self.P2, self.alarms, dt)

        
        max_out_t1 = self.T1_well.level_m * 0.1 #Grawitacja
        q_out_t1 = 0.0 if self.P1.inlet_valve_closed else max_out_t1
       
        if self.T1_well.level_m <= 0: q_out_t1 = 0.0
        
        self.T1_well.add_volume((s.q_in_O1 - q_out_t1) * dt)
        s.level_T1 = self.T1_well.level_m

        #Bilans P1
        q_p1_expected = sum(p.actual_flow() for p in self.P1.pumps)
        s.q_p1_meas = q_p1_expected 
        if any(p.state.failed for p in self.P1.pumps if p.state.enabled): s.q_p1_meas = 0.0
        
        self.P1.wet_well.add_volume((q_out_t1 - s.q_p1_meas) * dt)

        #Bilans Studnia (T2)
        q_out_t2 = s.level_T2 * 0.05
        self.T2_well.add_volume((s.q_p1_meas - q_out_t2) * dt)
        s.level_T2 = self.T2_well.level_m

        #Bilans P2
        q_in_total_p2 = q_out_t2 + s.q_in_O2
        q_into_p2 = 0.0 if self.P2.inlet_valve_closed else q_in_total_p2
        
        q_p2_expected = sum(p.actual_flow() for p in self.P2.pumps)
        s.q_p2_meas = q_p2_expected
        if any(p.state.failed for p in self.P2.pumps if p.state.enabled): s.q_p2_meas = 0.0

        self.P2.wet_well.add_volume((q_into_p2 - s.q_p2_meas) * dt)
        s.level_T3 = self.P2.wet_well.level_m

        s.t += dt