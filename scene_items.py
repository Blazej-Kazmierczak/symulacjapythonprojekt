# ui/scene_items.py
import math
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath, QFont, QPainter
from PyQt5.QtWidgets import (
    QGraphicsItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsTextItem
)

# Definicje kolorów systemowych
WATER_COLOR = QColor(0, 140, 255, 200)
PIPE_COLOR = QColor(130, 130, 130, 200)
TREND_COLOR = QColor(0, 255, 0) # Zielony dla wykresów

# ui/scene_items.py
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath, QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem

class TankItem(QGraphicsItem):
    def __init__(self, w, h, title):
        super().__init__()
        self.w, self.h = float(w), float(h)
        self.title = title
        self.fluid = QGraphicsRectItem(4, self.h-4, self.w-8, 0, self)
        self.fluid.setBrush(QBrush(QColor(0, 140, 255)))
        self.fluid.setPen(QPen(Qt.NoPen))
        
        self.lbl = QGraphicsTextItem(title, self)
        self.lbl.setDefaultTextColor(Qt.white)
        self.lbl.setFont(QFont("Consolas", 12, QFont.Bold))
        self.lbl.setPos(0, -35)

        self.data_lbl = QGraphicsTextItem("", self)
        self.data_lbl.setDefaultTextColor(QColor(0, 255, 255))
        self.data_lbl.setFont(QFont("Consolas", 11, QFont.Bold))
        self.data_lbl.setPos(0, self.h + 10)

    def set_info(self, lvl, q_h):
        self.data_lbl.setPlainText(f"L: {lvl:.2f} m\nQ: {q_h:.1f} m3/h")
        lvl_norm = max(0, min(lvl, 5.0)) / 5.0
        h_fill = (self.h - 8) * lvl_norm
        self.fluid.setRect(4, self.h - 4 - h_fill, self.w - 8, h_fill)

    def boundingRect(self): return QRectF(0, -40, self.w, self.h + 80)
    def paint(self, p, opt, w):
        p.setPen(QPen(Qt.white, 3))
        p.drawRect(0, 0, int(self.w), int(self.h))
class PumpOnPipe(QGraphicsItem):
    """Ikona pompy umieszczana bezpośrednio na rurze."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_on = False
        self.is_failed = False

    def paint(self, p, opt, w):
        color = Qt.red if self.is_failed else (Qt.green if self.is_on else Qt.gray)
        p.setBrush(QBrush(color))
        p.setPen(QPen(Qt.white, 2))
        p.drawEllipse(-12, -12, 24, 24)
        if self.is_failed:
            p.setPen(QPen(Qt.white, 2))
            p.drawLine(-7, -7, 7, 7)
            p.drawLine(-7, 7, 7, -7)

    def boundingRect(self):
        return QRectF(-15, -15, 30, 30)

class ValveItem(QGraphicsItem):
    def __init__(self, name="Z"):
        super().__init__()
        self.name = name
        self.closed = False
        self.txt = QGraphicsTextItem(self.name, self)
        self.txt.setDefaultTextColor(Qt.white)
        self.txt.setPos(-10, 15)

    def set_closed(self, closed):
        self.closed = closed
        self.update()

    def boundingRect(self):
        return QRectF(-20, -20, 40, 40)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.red if self.closed else Qt.green, 3))
        # Symbol zasuwy
        painter.drawRect(-15, -15, 30, 30)
        if self.closed:
            painter.drawLine(-15, -15, 15, 15)
            painter.drawLine(-15, 15, 15, -15)

class PipeItem(QGraphicsPathItem):
    def __init__(self, points, label=""):
        self.pts_data = points
        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.lineTo(x, y)
        super().__init__(path)
        self.setPen(QPen(PIPE_COLOR, 12, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(1)
        
        if label:
            self.lbl = QGraphicsTextItem(label, self)
            self.lbl.setDefaultTextColor(QColor(200, 200, 200))
            self.lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            self.lbl.setPos(points[0][0] + 10, points[0][1] - 35)

    def attach_to_scene(self, scene):
        scene.addItem(self)

    def set_flow(self, flow_val):
        # Opcjonalna zmiana koloru rury przy przepływie
        alpha = 150 + int(105 * min(1.0, flow_val))
        color = QColor(PIPE_COLOR.red(), PIPE_COLOR.green(), PIPE_COLOR.blue(), alpha)
        self.setPen(QPen(color, 12))

    def add_dots_to_scene(self, scene):
        pass # Miejsce na animację cząsteczek

    def step_anim(self, dt):
        pass

class FlowMeterItem(QGraphicsItem):
    def __init__(self, x, y, name="FM"):
        super().__init__()
        self.setPos(x, y)
        self.name = name
        self.v = 0.0

    def set_value(self, v):
        self.v = float(v)
        self.update()

    def boundingRect(self):
        return QRectF(0, 0, 130, 40)

    def paint(self, p, opt, w):
        p.setPen(Qt.white)
        p.setFont(QFont("Consolas", 10))
        p.drawText(0, 15, f"{self.name}:{self.v:.4f} m3/s")

class DryChamberItem(QGraphicsItem):
    """Panel statusowy pomp (diody) umieszczany pod rurą."""
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.states = [False, False, False, False] 

    def set_states(self, a_on, a_fail, b_on, b_fail):
        self.states = [a_on, a_fail, b_on, b_fail]
        self.update()

    def boundingRect(self):
        return QRectF(0, 0, 110, 70)

    def paint(self, p, opt, w):
        p.setPen(QPen(Qt.white, 1, Qt.DashLine))
        p.drawRect(0, 0, 110, 70)
        p.setFont(QFont("Consolas", 8))
        p.drawText(5, 15, self.title)
        
        # Diody statusowe
        for i in range(2):
            on = self.states[i*2]
            fail = self.states[i*2+1]
            color = Qt.red if fail else (Qt.green if on else Qt.gray)
            p.setBrush(QBrush(color))
            p.setPen(QPen(Qt.black, 1))
            p.drawEllipse(10, 25 + i*20, 12, 12)
            p.setPen(Qt.white)
            p.drawText(28, 35 + i*20, f"Pompa {chr(65+i)}")