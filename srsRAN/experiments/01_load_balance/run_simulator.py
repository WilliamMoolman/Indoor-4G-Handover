from src.simulator import Simulator
import sys
import os

if __name__ == "__main__":
    sim = Simulator()
    hom, ttt = sys.argv[1], sys.argv[2]
    hopps, hos = sim.run_single(int(hom), int(ttt), 600000)
    os.system(f"echo {hom},{ttt},{hopps},{hos} >> results.csv")
