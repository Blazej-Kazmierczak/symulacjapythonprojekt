from dataclasses import dataclass

@dataclass
class PumpState:
    enabled: bool = False
    failed: bool = False
    speed: float = 1.0  # 0..1 typowo

@dataclass
class ValveState:
    closed: bool = False
