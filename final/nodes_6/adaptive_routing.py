import networkx as nx
from network_setup import create_network
from congestion_monitor import NodeMonitor


class AdaptiveRouter:
    def __init__(self, network, monitors):
        self.network = network
        self.monitors = monitors  # dict: {node_id: NodeMonitor}

    def path_cost(self, path):
        """
        Calculate routing cost along a path using prediction-aware scores.
        Predicted nodes cost 1 — rerouting happens here (EARLY, before congestion).
        Congested nodes cost 3 — strongly avoided.
        Normal nodes cost 0.
        This is what makes routing adaptive AND predictive.
        """
        total = 0
        for node in path:
            if node in self.monitors:
                total += self.monitors[node].get_routing_score()
        return total

    def find_best_path(self, source, destination):
        """Find the least congested path, rerouting at prediction stage."""
        try:
            all_paths = list(nx.all_simple_paths(self.network, source, destination))
        except nx.NetworkXNoPath:
            print(f'No path found between {source} and {destination}!')
            return None

        if not all_paths:
            print(f'No path found between {source} and {destination}!')
            return None

        best_path = min(all_paths, key=self.path_cost)
        best_cost = self.path_cost(best_path)

        print(f'\nAll paths from Node {source} to Node {destination}:')
        for path in all_paths:
            cost = self.path_cost(path)
            # Show why each path was scored the way it was
            node_states = []
            for n in path:
                if n in self.monitors:
                    m = self.monitors[n]
                    if m.congested:
                        node_states.append(f'N{n}[CONG]')
                    elif m.predicted:
                        node_states.append(f'N{n}[PRED]')
                    else:
                        node_states.append(f'N{n}[OK]')
            marker = ' <-- BEST PATH' if path == best_path else ''
            print(f'  {" -> ".join(node_states)}  |  Cost={cost}{marker}')

        return best_path


if __name__ == '__main__':
    print("--- Testing Adaptive Routing with Early Prediction ---\n")

    network = create_network()
    monitors = {n: NodeMonitor(n) for n in network.nodes()}

    # Node 2: in EARLY PREDICTION stage (not yet congested but trending there)
    monitors[2].update(queue_length=7, delay=0.035, traffic_rate=60)

    # Node 4: fully congested
    monitors[4].update(queue_length=15, delay=0.09, traffic_rate=95)

    print("Node states before routing:")
    for n, m in monitors.items():
        m.report()

    router = AdaptiveRouter(network, monitors)
    best = router.find_best_path(1, 6)
    print(f'\nChosen path: {best}')
    print('\nNote: Rerouting triggered by PREDICTION on Node 2,')
    print('before it ever became fully congested.')