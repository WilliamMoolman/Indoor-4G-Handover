from matplotlib.patches import RegularPolygon
import numpy as np
import matplotlib.pyplot as plt

def PL_sBS(distance: float, Xa: float = 10):
    """
    Path loss for carrier frequency 2000MHz and height of 15m
    """
    return 128.1 + 37.6 * np.log10(distance) + Xa

def PL_mBS(distance: float, Xa: float = 10):
    """
    Path loss for carrier frequency 900MHz and height of 45m
    """
    return 95.5 + 34.01 * np.log10(distance) + Xa

def RSRP(bs_type: str, transit_power, antennae_gain, distance):
    if bs_type == "sBS":
        return transit_power + antennae_gain - PL_sBS(distance) 
    elif bs_type == "mBS":
        return transit_power + antennae_gain - PL_mBS(distance)
    else:
        raise ValueError("bs_type must be either sBS or mBS")
    
class BS:
    def __init__(self, id, x, y, freq, height, power, capacity, alpha, radius):
        self.id = id
        self.x = x
        self.y = y
        self.freq = freq
        self.height = height
        self.antenae_gain = 15
        self.power = power
        self.capacity = capacity
        self.alpha = alpha
        self.radius = radius

class MacroBS(BS):
    def __init__(self, id, x, y):
        super().__init__(id, x, y, 900, 45, 46, 200, 0.5, 500)
    
    def plot(self, ax):
        mBS_patch = RegularPolygon([self.x, self.y], numVertices=6, radius=500, orientation=np.pi/6, alpha=0.1, facecolor='blue', edgecolor='black')
        ax.add_patch(mBS_patch)
        ax.scatter(self.x, self.y, color='black', marker='s', s=100)

    def contains(self, x, y):
        x, y = map(abs, (x-self.x, y-self.y))
        return y < 3**0.5 * min(500 - x, 500 / 2)

POWER_BOOST = 45
class SmallBS(BS):
    def __init__(self, id, x, y, parent: MacroBS):
        super().__init__(id, x, y, 2000, 15, 30+POWER_BOOST, 50, 0.8, 200)
        self.parent = parent

    def plot(self, ax):
        sBS_patch = plt.Circle([self.x, self.y], radius=200, alpha=0.1, facecolor='red', edgecolor='black')
        ax.scatter(self.x, self.y, color='black', marker='^', s=100)
        ax.add_patch(sBS_patch)
        

class UE:
    def __init__(self, x, y, speed, cells):
        self.x = x
        self.y = y
        self.previous_bs = None
        self.bs = self.measurement_report(cells)[0][0]
        self.speed = speed
        self.angle = np.random.uniform(0, 2*np.pi)
        self.ttt = 0
        self.hopp_timer = 0
    
    def handover(self, cells, hm, ttt, dt):
        # Check for ping pong
        old_bs = self.bs
        if self._handover(cells, hm, ttt, dt):
            self.hopp_timer += dt
            if self.previous_bs == self.bs and self.hopp_timer < 1000: # Ping pong
                self.previous_bs = old_bs
                self.hopp_timer = 0
                return True, True # OK, ping pong
            else:
                self.previous_bs = old_bs
                self.hopp_timer = 0
                return True, False
        else:
            return False, False

    def _handover(self, cells, hm, ttt, dt):
        mr = self.measurement_report(cells)
        if self.bs is None:
            self.bs = mr[0][0]
            self.ttt = 0
            return True
        if self.bs == mr[0][0]:
            self.ttt = 0
            return False
        bs_strength = None
        for bs in mr:
            if bs[0] == self.bs:
                bs_strength = bs[1]
                break
        if bs_strength + hm < mr[0][1]:
            self.ttt += dt
            if self.ttt >= ttt:
                self.bs = mr[0][0]
                self.ttt = 0
                return True
            else:
                return False
        else:
            self.ttt = 0
            return False

    def move(self, dt):
        M_PER_MS = 3600
        # Change angle slightly
        self.x += self.speed/M_PER_MS * np.cos(self.angle) * dt
        self.y += self.speed/M_PER_MS * np.sin(self.angle) * dt
        self.angle += np.random.uniform(-np.pi/4, np.pi/4)

    def move_back(self, dt):
        self.x -= self.speed * np.cos(self.angle) * dt
        self.y -= self.speed * np.sin(self.angle) * dt
        self.angle -= np.pi/2
    
    def measurement_report(self, cells: list):
        report = []
        for cell in cells:
            cell_dist = np.sqrt((self.x - cell.x)**2 + (self.y - cell.y)**2)
            is_mbs = isinstance(cell, MacroBS)
            power = RSRP('mBS' if is_mbs else 'sBS', cell.power, cell.antenae_gain, cell_dist)
            report.append([cell.id, power])
        return sorted(report, key=lambda x: x[1], reverse=True)