from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random
import time

BOMB = QImage("bomb1.png")

COLORS = {1: QColor('violet'),2: QColor('blue'),3: QColor('gray'),4: QColor('green'),5: QColor('yellow'),6: QColor('red'),7: QColor('orange'),8: QColor('pink')}
LEVEL=[(20, 50)]
READY=0
IGRA=1
FAIL=2
SUCCESS=3
class Pos(QWidget):
    expandable = pyqtSignal(int, int)
    clicked = pyqtSignal()
    ohno = pyqtSignal()
    def __init__(self, x, y, *args, **kwargs):
        super(Pos, self).__init__(*args, **kwargs)
        self.setFixedSize(QSize(20, 20))
        self.x = x
        self.y = y
    def reset(self):
        self.is_start = False
        self.is_mine = False
        self.adjacent_n = 0
        self.is_revealed = False
        self.is_flagged = False
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = event.rect()
        if self.is_revealed:
            color = self.palette().color(QPalette.Background)
            outer, inner = color, color
        else:
            outer, inner = Qt.gray, Qt.lightGray
        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)
        if self.is_revealed:
            if self.is_mine:
                p.drawPixmap(r, QPixmap(BOMB))
            elif self.adjacent_n > 0:
                pen = QPen(COLORS[self.adjacent_n])
                p.setPen(pen)
                f = p.font()
                f.setBold(True)
                p.setFont(f)
                p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter, str(self.adjacent_n))
    def flag(self):
        self.is_flagged = True
        self.update()
        self.clicked.emit()
    def reveal(self):
        self.is_revealed = True
        self.update()
    def click(self):
        if not self.is_revealed:
            self.reveal()
            if self.adjacent_n == 0:
                self.expandable.emit(self.x, self.y)
        self.clicked.emit()
    def mouseReleaseEvent(self, e):
        if (e.button() == Qt.RightButton and not self.is_revealed):
            self.flag()
        elif (e.button() == Qt.LeftButton):
            self.click()
            if self.is_mine:
                self.ohno.emit()
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.b_size, self.n_mines = LEVEL[0]
        w=QWidget()
        hb=QHBoxLayout()
        self.mines=QLabel()
        self.mines.setAlignment
        self.clock=QLabel()
        self.clock.setAlignment
        f = self.mines.font()
        f.setPointSize(24)
        f.setWeight(75)
        self.mines.setFont(f)
        self.clock.setFont(f)
        self.mines.setText("%03d" % self.n_mines)
        self.button = QPushButton()
        self.button.setFixedSize(QSize(100, 100))
        self.button.setIconSize(QSize(100, 100))
        self.button.setFlat(True)
        l = QLabel()
        l.setPixmap(QPixmap.fromImage(BOMB))
        l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hb.addWidget(l)
        hb.addWidget(self.mines)
        l = QLabel()
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        vb = QVBoxLayout()
        vb.addLayout(hb)
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)
        self.init_map()
        self.update_status(READY)
        self.reset_map()
        self.update_status(READY)
        self.show()
    def init_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = Pos(x, y)
                self.grid.addWidget(w, y, x)
                w.clicked.connect(self.trigger_start)
                w.expandable.connect(self.expand_reveal)
                w.ohno.connect(self.game_over)
    def reset_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reset()
        positions = []
        while len(positions) < self.n_mines:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_mine = True
                positions.append((x, y))
        def get_adjacency_n(x, y):
            positions = self.get_surrounding(x, y)
            n_mines = sum(1 if w.is_mine else 0 for w in positions)
            return n_mines
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.adjacent_n = get_adjacency_n(x, y)
        while True:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            w = self.grid.itemAtPosition(y, x).widget()
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_start = True
                for w in self.get_surrounding(x, y):
                    if not w.is_mine:
                        w.click()
                break
    def get_surrounding(self, x, y):
        positions=[]
        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                positions.append(self.grid.itemAtPosition(yi, xi).widget())
        return positions
    def reveal_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reveal()
    def expand_reveal(self, x, y):
        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                w = self.grid.itemAtPosition(yi, xi).widget()
                if not w.is_mine:
                    w.click()
    def trigger_start(self, *args):
        if self.status!=IGRA:
            self.update_status(IGRA)
            self._timer_start_nsecs = int(time.time())
    def update_status(self, status):
        self.status=status
    def update_timer(self):
        if self.status==IGRA:
            n_secs = int(time.time()) - self._timer_start_nsecs
            self.clock.setText("%03d" % n_secs)
    def game_over(self):
        self.reveal_map()
        self.update_status(FAIL)
        
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()