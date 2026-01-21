# src/sewage_sim/inflow.py
import math
import random
from dataclasses import dataclass

@dataclass
class DiurnalRandomInflow:
    base_m3s: float
    peak_m3s: float
    peak_hours: list[int]
    noise_sigma: float
    rng: random.Random

    def flow(self, t: float) -> float:
        hour = int((t / 3600.0) % 24)
        target = self.peak_m3s if hour in self.peak_hours else self.base_m3s
        noise = self.rng.gauss(0.0, self.noise_sigma)
        factor = max(0.0, min(3.0, math.exp(noise)))
        return target * factor

@dataclass
class ConstantInflow:
    q_m3s: float

    def flow(self, t: float) -> float:
        return self.q_m3s
