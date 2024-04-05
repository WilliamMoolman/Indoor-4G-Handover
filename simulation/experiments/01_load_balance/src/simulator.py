from .environment import Environment
# from tqdm import tqdm


class Simulator:
    def __init__(self, homs: list = [], ttts: list = []) -> None:
        self.homs = homs
        self.ttts = ttts

    def run_single(self, hm, ttt, max_time):
        env = Environment(hm, ttt)
        timestep = 16  # ms
        for _ in range(int(max_time / timestep)):
            env.move_UEs(timestep)
        return env.hm, env.ttt

    def run(self):
        results = {}
        for hom in self.homs:
            for ttt in self.ttts:
                print(f"===== Running with hm={hom} and ttt={ttt} =====")
                hopps, hos = self.run_single(hom, ttt, 600000)
                results[(hom, ttt)] = (hopps, hos)
        return results
