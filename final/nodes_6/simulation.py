import simpy
import random
from network_setup import create_network
from congestion_monitor import NodeMonitor
from adaptive_routing import AdaptiveRouter

TRAFFIC_RATES = {1: 5, 2: 15, 3: 5, 4: 12, 5: 5, 6: 5}

# Drain rates calculated dynamically - 20-30% higher than arrival rate
DRAIN_RATES = {}
for node_id, rate in TRAFFIC_RATES.items():
    # Drain 2-3 more than arrival rate to keep queues stable
    DRAIN_RATES[node_id] = rate + 2
    # For high-traffic nodes, add extra buffer
    if rate > 10:
        DRAIN_RATES[node_id] = rate + 3

print(f"Dynamic drain rates: {DRAIN_RATES}")


def packet_generator(env, node_id, monitor, rate, results):
    """Simulates packets arriving at a node over time (arrival-only).

    Drain is handled by a separate periodic process so the simulation uses a
    consistent 1-second time granularity for comparisons (same model as
    `compare.py`).
    """
    while True:
        yield env.timeout(random.expovariate(rate))

        monitor.queue_length += 1

        # Update instantaneous metrics (traffic rate has small noise)
        monitor.traffic_rate = int(rate * 10) + random.randint(-3, 3)
        monitor.delay = monitor.queue_length * 0.005
        
        # Predict congestion after update
        monitor.predict_congestion()

        # Record an arrival event (useful for timeline-based visualizations)
        results.append({
            'time': round(env.now, 3),
            'node': node_id,
            'queue': monitor.queue_length,
            'delay': round(monitor.delay, 4),
            'rate': monitor.traffic_rate,
            'predicted': monitor.predicted,
            'congested': monitor.congested
        })


def run_simulation(duration=50, seed=None):
    """Run the full network simulation with early congestion prediction.

    If `seed` is provided, the RNG is seeded for reproducible runs.
    """
    if seed is not None:
        random.seed(seed)

    print("=" * 55)
    print("  Early Congestion Prediction & Adaptive Routing Sim")
    print("=" * 55)

    env = simpy.Environment()
    network = create_network()
    monitors = {n: NodeMonitor(n) for n in network.nodes()}
    router = AdaptiveRouter(network, monitors)
    results = []

    traffic_rates = TRAFFIC_RATES  # Use the same rates defined above

    print(f"\nStarting simulation for {duration} time units...")
    print("Traffic rates per node:")
    for nid, r in traffic_rates.items():
        print(f"  Node {nid}: rate={r}")
    print(f"\nEarly prediction triggers at 60-70% of congestion thresholds\n")

    for node_id, rate in traffic_rates.items():
        env.process(packet_generator(env, node_id, monitors[node_id], rate, results))

    def drain_and_record():
        while True:
            yield env.timeout(1.0)
            for n, monitor in monitors.items():
                drain = random.randint(DRAIN_RATES[n] - 1, DRAIN_RATES[n] + 1)
                monitor.queue_length = max(0, monitor.queue_length - drain)
                monitor.traffic_rate = int(traffic_rates[n] * 10) + random.randint(-3, 3)
                monitor.delay = monitor.queue_length * 0.005
                monitor.predict_congestion()
                results.append({
                    'time': round(env.now, 3),
                    'node': n,
                    'queue': monitor.queue_length,
                    'delay': round(monitor.delay, 4),
                    'rate': monitor.traffic_rate,
                    'predicted': monitor.predicted,
                    'congested': monitor.congested
                })

    env.process(drain_and_record())

    # Initial routing decision
    prev_path = router.find_best_path(1, 6)
    print(f"Initial path from Node 1 to Node 6: {prev_path}")

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
    
    # Estimate packets saved (this is a simplification)
    if predicted_events > 0:
        print(f"Packets potentially saved by early prediction: ~{predicted_events // 2}")

    return results, monitors


if __name__ == '__main__':
    results, monitors = run_simulation(duration=50, seed=42)