# src/sewage_sim/alarms.py
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Alarm:
    code: str
    active: bool = False
    message: str = ""

@dataclass
class AlarmBook:
    alarms: Dict[str, Alarm] = field(default_factory=dict)

    def set(self, code: str, message: str):
        a = self.alarms.get(code) or Alarm(code=code)
        a.active = True
        a.message = message
        self.alarms[code] = a

    def clear(self, code: str):
        if code in self.alarms:
            self.alarms[code].active = False

    def active_list(self):
        return [a for a in self.alarms.values() if a.active]
