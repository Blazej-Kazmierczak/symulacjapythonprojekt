# src/sewage_sim/components.py
from dataclasses import dataclass, field
from .types import PumpState, ValveState

@dataclass
class WetWell:
    area_m2: float
    level_min_m: float
    level_start_m: float
    level_max_m: float
    level_m: float

    def add_volume(self, dV_m3: float):
        self.level_m = max(0.0, self.level_m + dV_m3 / self.area_m2)

@dataclass
class Pump:
    name: str
    q_nom_m3s: float
    efficiency: float
    state: PumpState = field(default_factory=PumpState)

    def actual_flow(self) -> float:
        if not self.state.enabled or self.state.failed:
            return 0.0
        return max(0.0, self.q_nom_m3s * self.state.speed)

@dataclass
class FlowMeter:
    tolerance_rel: float
    fail_delay_s: float
    bad_time_s: float = 0.0

    def check(self, q_cmd: float, q_meas: float, dt: float) -> bool:
        if q_cmd <= 1e-9:
            self.bad_time_s = 0.0
            return True

        rel_err = abs(q_meas - q_cmd) / max(q_cmd, 1e-9)
        if rel_err > self.tolerance_rel:
            self.bad_time_s += dt
        else:
            self.bad_time_s = 0.0

        return self.bad_time_s < self.fail_delay_s

@dataclass
class PumpStation:
    name: str
    wet_well: WetWell
    pumps: list[Pump]
    flowmeter: FlowMeter
    discharge_valve: ValveState = field(default_factory=ValveState)
    last_single_idx: int = 0
