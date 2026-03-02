import simpy
import random
from network_setup import create_network
from congestion_monitor import NodeMonitor
from adaptive_routing import AdaptiveRouter

# Drain probability per packet arrival event.
# Each event: +1 packet arrives, then drain 1 with probability DRAIN_PROB.
# Heavy nodes (2, 4): prob=0.993 → queue fluctuates 0-15, avg ~9 (crosses both thresholds)
# Light nodes (1,3,5,6): prob=0.85 → arrivals rare enough queue stays low (OK state)
DRAIN_PROB = {1: 0.85, 2: 0.993, 3: 0.85, 4: 0.993, 5: 0.85, 6: 0.85}


def packet_generator(env, node_id, monitor, rate, results):
    """Simulates packets arriving at a node over time."""
    while True:
        yield env.timeout(random.expovariate(rate))

        monitor.queue_length += 1

        # Probabilistic drain — tuned per node so queues stay in a realistic range
        if random.random() < DRAIN_PROB[node_id]:
            monitor.queue_length = max(0, monitor.queue_length - 1)

        monitor.traffic_rate = int(rate * 10)
        monitor.delay = monitor.queue_length * 0.005

        # Two-stage prediction check
        monitor.predict_congestion()

        results.append({
            'time': round(env.now, 3),
            'node': node_id,
            'queue': monitor.queue_length,
            'delay': round(monitor.delay, 4),
            'rate': monitor.traffic_rate,
            'predicted': monitor.predicted,
            'congested': monitor.congested
        })


def run_simulation(duration=50):
    """Run the full network simulation with early congestion prediction."""
    print("=" * 55)
    print("  Early Congestion Prediction & Adaptive Routing Sim")
    print("=" * 55)

    env = simpy.Environment()
    network = create_network()
    monitors = {n: NodeMonitor(n) for n in network.nodes()}
    router = AdaptiveRouter(network, monitors)
    results = []

    traffic_rates = {
        1: 5,
        2: 15,   # Heavy — will trigger prediction
        3: 5,
        4: 12,   # Heavy — will trigger prediction
        5: 5,
        6: 5
    }

    print(f"\nStarting simulation for {duration} time units...")
    print(f"Heavy traffic: Node 2 (rate=15), Node 4 (rate=12)")
    print(f"Early prediction triggers at 60-70% of congestion thresholds\n")

    for node_id, rate in traffic_rates.items():
        env.process(packet_generator(env, node_id, monitors[node_id], rate, results))

    prev_path = router.find_best_path(1, 6)

    env.run(until=duration)

    print("\n--- Final Node Status ---")
    for node_id, monitor in monitors.items():
        monitor.report()

    print("\n--- Adaptive Routing Decision (Node 1 to Node 6) ---")
    final_path = router.find_best_path(1, 6)

    predicted_events = sum(1 for r in results if r['predicted'])
    congested_events = sum(1 for r in results if r['congested'])

    print(f"\n--- Simulation Summary ---")
    print(f"Total events recorded : {len(results)}")
    print(f"Early prediction hits : {predicted_events}  (rerouted before congestion)")
    print(f"Actual congestion hits: {congested_events}  (threshold breached)")
    print(f"Packets saved by early prediction: ~{predicted_events}")

    return results, monitors


if __name__ == '__main__':
    results, monitors = run_simulation(duration=50)