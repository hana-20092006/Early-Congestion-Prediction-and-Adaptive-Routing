# ── Hard thresholds (actual congestion) ──────────────────────
QUEUE_THRESHOLD = 10    # More than 10 packets waiting = congested
DELAY_THRESHOLD = 0.05  # More than 50ms delay = congested
RATE_THRESHOLD = 80     # More than 80 packets/sec = congested

# ── Soft thresholds (early prediction) ───────────────────────
# Set at ~60-70% of hard thresholds so we predict BEFORE it happens
PREDICT_QUEUE = 6       # 60% of QUEUE_THRESHOLD
PREDICT_DELAY = 0.03    # 60% of DELAY_THRESHOLD
PREDICT_RATE  = 55      # 70% of RATE_THRESHOLD


class NodeMonitor:
    def __init__(self, node_id):
        self.node_id = node_id
        self.queue_length = 0
        self.delay = 0.0
        self.traffic_rate = 0
        self.congestion_score = 0
        self.predicted = False   # True = heading toward congestion (early warning)
        self.congested = False   # True = actually congested (hard threshold breached)

    def update(self, queue_length=None, delay=None, traffic_rate=None):
        """Update monitor with new values"""
        if queue_length is not None:
            self.queue_length = queue_length
        if delay is not None:
            self.delay = delay
        if traffic_rate is not None:
            self.traffic_rate = traffic_rate
        # Auto-predict after update
        self.predict_congestion()

    def predict_congestion(self):
        """
        Two-stage detection:
        Stage 1 - EARLY PREDICTION: soft thresholds (acts before congestion hits)
        Stage 2 - ACTUAL CONGESTION: hard thresholds (congestion already happening)
        Rerouting is triggered at Stage 1, so packets are moved BEFORE Stage 2.
        """
        # Stage 2: Hard thresholds — actual congestion
        hard_score = 0
        if self.queue_length > QUEUE_THRESHOLD:
            hard_score += 1
        if self.delay > DELAY_THRESHOLD:
            hard_score += 1
        if self.traffic_rate > RATE_THRESHOLD:
            hard_score += 1
        self.congestion_score = hard_score
        self.congested = hard_score >= 2

        # Stage 1: Soft thresholds — early prediction
        soft_score = 0
        if self.queue_length > PREDICT_QUEUE:
            soft_score += 1
        if self.delay > PREDICT_DELAY:
            soft_score += 1
        if self.traffic_rate > PREDICT_RATE:
            soft_score += 1
        # Predicted = soft thresholds triggered but hard not yet (still time to reroute)
        self.predicted = (soft_score >= 2) and not self.congested

        # Return True if ANY warning (predicted OR congested) — triggers rerouting
        return self.predicted or self.congested

    def get_routing_score(self):
        """
        Score used by the router to pick the best path.
        Predicted nodes cost 1 (avoid if possible).
        Congested nodes cost 3 (strongly avoid).
        This ensures rerouting happens at prediction stage.
        """
        if self.congested:
            return 3
        if self.predicted:
            return 1
        return 0

    def report(self):
        if self.congested:
            status = 'CONGESTED'
        elif self.predicted:
            status = 'PREDICTED (early warning — rerouting triggered)'
        else:
            status = 'OK'
        print(f'Node {self.node_id}: Queue={self.queue_length}, '
              f'Delay={self.delay:.3f}s, Rate={self.traffic_rate} pkt/s, Status={status}')


if __name__ == '__main__':
    print("--- Testing Congestion Monitor ---\n")

    # Normal node
    m1 = NodeMonitor(1)
    m1.update(queue_length=3, delay=0.01, traffic_rate=20)
    m1.report()

    # Node in EARLY PREDICTION stage (soft thresholds hit, hard not yet)
    m2 = NodeMonitor(2)
    m2.update(queue_length=7, delay=0.035, traffic_rate=60)
    m2.report()

    # Fully congested node (hard thresholds hit)
    m3 = NodeMonitor(3)
    m3.update(queue_length=12, delay=0.06, traffic_rate=85)
    m3.report()

    print("\nRouting scores (used to pick best path):")
    for m in [m1, m2, m3]:
        print(f'  Node {m.node_id}: routing_score = {m.get_routing_score()}')