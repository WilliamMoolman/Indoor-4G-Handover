from .network_entities import MacroBS, SmallBS, UE
import numpy as np
import matplotlib.pyplot as plt

class Environment:
    def __init__(self, hm, ttt) -> None:
        # HEXAGON MATH
        r = 500 # radius of hexagon
        a = r * np.sqrt(3) / 2 # Apothem of hexagon
        # Get 6 offsets from hexagon centre 0.5 radius away
        hr = 500 / 2 # half radius
        hex_offsets = np.array([[hr, 0], [hr*np.cos(np.pi/3), hr*np.sin(np.pi/3)], [-hr*np.cos(np.pi/3), hr*np.sin(np.pi/3)], [-hr, 0], [-hr*np.cos(np.pi/3), -hr*np.sin(np.pi/3)], [hr*np.cos(np.pi/3), -hr*np.sin(np.pi/3)]])

        mBS_locations = np.array([[500, a], [1250, 2*a], [500, 3*a]])
        mBS_cells = [MacroBS(i, mBS_loc[0], mBS_loc[1]) for i, mBS_loc in enumerate(mBS_locations)]

        sBS_cells = []
        for i, mBS in enumerate(mBS_locations):
            for j, location in enumerate(mBS + hex_offsets[[1,3,5]]):
                # print(location)
                sBS_cells.append(SmallBS(i*3+j+3,location[0], location[1], mBS_cells[i]))

        self.mBS_cells = mBS_cells
        self.sBS_cells = sBS_cells
        self.cells = mBS_cells + sBS_cells

        np.random.seed(0)
        ue_points = []
        ue_bs = []
        while len(ue_points) < 1000:
            x, y = np.random.randint(0, 1750), np.random.randint(0, 1750)
            for i, mBS in enumerate(mBS_cells):
                if mBS.contains(x, y):
                    ue_bs.append(i)
                    ue_points.append([float(x), float(y)])
                    break

        M_PER_MS = 3600
        UEs = []
        for i in range(1000):
            if i < 400:
                UEs.append(UE(ue_points[i][0], ue_points[i][1], 0, self.cells))
            elif i < 600:
                UEs.append(UE(ue_points[i][0], ue_points[i][1], 5/M_PER_MS, self.cells))
            elif i < 800:
                UEs.append(UE(ue_points[i][0], ue_points[i][1], 25/M_PER_MS, self.cells))
            else:
                UEs.append(UE(ue_points[i][0], ue_points[i][1], 60/M_PER_MS, self.cells))
        
        
        self.ues = UEs
        self.hopps = 0
        self.hos = 0
        self.hm = hm
        self.ttt = ttt
    
    def plot_environment(self):
        bs_colours = {
            0: 'red',
            1: 'green',
            2: 'blue',
            3: 'orange',
            4: 'purple',
            5: 'yellow',
            6: 'pink',
            7: 'brown',
            8: 'grey',
            9: 'black',
            10: 'white',
            11: 'cyan'
        }
        plt.figure(figsize=(6, 6))

        ax = plt.gca()
        for cell in self.cells:
            cell.plot(ax)

        ue_array = np.array([[ue.x, ue.y] for ue in self.ues])
        colours = ([bs_colours[ue.bs] for ue in self.ues])
        # print(ue_array)
        plt.scatter(ue_array[:,0], ue_array[:,1], color=colours, s=10)

        plt.xlim(0, 1750)
        plt.ylim(0, 1750)
        plt.legend()
    
    def move_UEs(self, dt=1, debug=False):
        for i, ue in enumerate(self.ues):
            ue.move(dt)
            old_bs = ue.bs
            for bs in self.mBS_cells:
                if bs.contains(ue.x, ue.y):
                    break
            else:
                ue.move_back(dt)
            ok, hopp = ue.handover(self.cells, self.hm, self.ttt, dt)
            if ok:
                self.hos += 1
                if debug: print(f"HANDOVER: UE{i}: {old_bs}->{ue.bs}"+(" (PING PONG)" if hopp else ""))
            if hopp: self.hopps += 1