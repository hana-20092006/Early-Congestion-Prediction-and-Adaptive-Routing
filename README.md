# Early Congestion Prediction & Adaptive Routing

> A Computer Networks simulation that **predicts congestion before it happens** and reroutes traffic proactively to prevent packet loss and delay.

Traditional congestion control reacts after packet loss. This system predicts congestion at 60–70% utilization and reroutes traffic before performance degrades.

[Live Demo](https://srijani-das07.github.io/Early-Congestion-Prediction-and-Adaptive-Routing/)

---

## Overview

In a computer network, data packets compete for limited bandwidth. When queues fill up, congestion occurs, leading to delay and packet drops.

This project implements:

- A **two-stage congestion detection model**
- A **cost-based adaptive routing algorithm**
- A **SimPy discrete-event network simulation**
- Visualization of congestion trends and routing behavior

The system reroutes traffic at the *prediction stage*, not the failure stage.

This repository contains **two working versions**:

| | `nodes_6/` | `nodes_100/` |
|---|---|---|
| **Nodes / Edges** | 6 nodes, 7 edges | 100 nodes, ~300+ edges |
| **Topology** | Hand-crafted fixed graph | Random geometric graph (ISP-like) |
| **Routing algorithm** | `all_simple_paths` (exhaustive) | Dijkstra (O(E log V)) |
| **Congested node cost** | 3 | ∞ (hard block) |
| **Hot nodes** | Node 2, Node 4 (fixed) | ~15 high-degree nodes (dynamic) |
| **Edge capacity** | Fixed values | Degree-scaled (40–150) |
| **Congestion thresholds** | Same | Same (identical, for comparability) |

---

## Problem Statement

Most congestion control mechanisms (e.g., TCP AIMD) use packet loss as the signal for congestion. This is reactive and the performance degradation has already occurred.

This project improves upon that by:

| Traditional Approach | This Project |
|----------------------|-------------|
| Detects after packet loss | Predicts before packet loss |
| Acts when queue is full | Acts at 60–70% capacity |
| Single detection threshold | Two-stage threshold system |
| Reroutes after degradation | Reroutes while performance is stable |

Core insight: **If congestion can be predicted, it can be avoided.**

---

## Architecture

### 1. Two-Stage Congestion Detection

Implemented in `congestion_monitor.py`. Thresholds are **identical in both versions** so results remain directly comparable.

#### Stage 1 — Early Prediction (Soft Thresholds)

A node is marked **PREDICTED** if any 2 of the following occur:

- Queue length > 6 packets
- Delay > 30 ms
- Traffic rate > 55 packets/sec

These represent ~60–70% of danger capacity.

#### Stage 2 — Hard Congestion (Hard Thresholds)

A node is marked **CONGESTED** if any 2 of the following occur:

- Queue length > 10 packets
- Delay > 50 ms
- Traffic rate > 80 packets/sec

This two-metric requirement prevents false positives from single metric spikes.

---

### 2. Adaptive Routing Logic

Implemented in `adaptive_routing.py`.

#### 6-Node Version

Each node contributes a flat cost to a path:

- OK → cost 0
- PREDICTED → cost 1
- CONGESTED → cost 3

All simple paths from source to destination are evaluated using `all_simple_paths`. The path with **minimum total cost** is selected. Rerouting is triggered at cost 1 (prediction stage), not cost 3 (congestion stage).

#### 100-Node Version

Upgraded to **Dijkstra's algorithm** (O(E log V)) for scalability. Congested nodes are **hard-blocked** (removed from the graph entirely before routing). Dynamic edge weights account for live queue load:

```
weight(u → v) = 1 + (20 if predicted) + (queue_length × 2)
```

| Status | 6-Node Cost | 100-Node Cost |
|--------|-------------|---------------|
| OK | 0 | 1 (base) |
| PREDICTED | 1 | +20 penalty |
| CONGESTED | 3 | ∞ (hard block) |

---

## Network Topology

### 6-Node Version
- **6 nodes** (routers), **7 bidirectional edges**
- Hand-crafted fixed topology
- Node 2 and Node 4 receive higher simulated traffic to demonstrate prediction and rerouting

### 100-Node Version
- **100 nodes** (routers), **~300+ bidirectional edges**
- **Random geometric graph** with radius 0.15 — nodes connect if within spatial proximity, mimicking real ISP mesh topology
- Full connectivity guaranteed — isolated components are bridged automatically
- **Variable edge capacities** (40–150): core nodes with higher degree receive higher capacity
- ~5–8 average degree per node
- **~15 "hot" nodes** (high-degree) receive elevated traffic during simulation

---

## Project Structure

```
root/
│
├── nodes_6/                   # Original 6-node version
│   ├── network_setup.py       # Fixed graph (6 nodes, 7 edges)
│   ├── congestion_monitor.py  # Two-stage prediction logic
│   ├── adaptive_routing.py    # all_simple_paths + cost 0/1/3 scoring
│   ├── simulation.py          # SimPy simulation (Node 2 & 4 as hot nodes)
│   ├── compare.py             # Baseline vs Early Prediction graphs
│   ├── visualize.py           # 4-panel matplotlib output chart
│   ├── run.py                 # Single command to run everything
│   ├── index.html             # Live interactive browser demo
│   ├── requirements.txt       # Python dependencies
│   └── README.md
│
├── nodes_100/                 # Scaled 100-node version
│   ├── network_setup.py       # Random geometric graph (100 nodes, degree-scaled capacity)
│   ├── congestion_monitor.py  # Same thresholds, ∞ cost for congested nodes
│   ├── adaptive_routing.py    # Dijkstra + hard block + dynamic queue cost
│   ├── simulation.py          # SimPy simulation (~15 hot nodes)
│   ├── compare.py             # Heatmap, CDF, timeline graphs
│   ├── visualize.py           # Per-node visualisation helpers
│   ├── run.py                 # Single command to run everything
│   ├── index.html             # Live interactive browser demo
│   ├── package-lock.json      # Frontend dependency lock file
│   ├── requirements.txt       # Python dependencies
│   └── README.md
│
└── README.md                  # This file
```

---

## How to Run

### Prerequisites

Make sure you have Python 3.8 or higher installed:

```bash
python --version
```

### Step 1 — Fork & Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/Early-Congestion-Prediction-and-Adaptive-Routing.git
cd Early-Congestion-Prediction-and-Adaptive-Routing
```

### Step 2 — Install Dependencies

```bash
# For the 6-node version
cd nodes_6
pip install -r requirements.txt

# For the 100-node version
cd nodes_100
pip install -r requirements.txt
```

This installs: `networkx`, `simpy`, `matplotlib` (+ `numpy` for 100-node version).

### Step 3 — Run Everything

```bash
# 6-node version
cd nodes_6
python run.py

# 100-node version
cd nodes_100
python run.py
```

### Running the Live Demo (Optional)

Open `index.html` (inside either `nodes_6/` or `nodes_100/`) in any browser. No installation required. Use the sliders to control traffic rates per node in real time and watch the routing adapt live.

---

## CN Concepts Used

| Concept | Where It's Applied |
|---|---|
| **Congestion Control** | Two-stage threshold system in `congestion_monitor.py` |
| **Routing Algorithms** | `all_simple_paths` (6-node) / Dijkstra (100-node) in `adaptive_routing.py` |
| **Quality of Service (QoS)** | Prioritising low-congestion paths to maintain throughput and reduce delay |
| **Network Monitoring** | Continuous per-node tracking of queue length, delay, and traffic rate |
| **Discrete Event Simulation** | SimPy environment simulating packet arrivals using exponential distribution |
| **Graph Theory** | NetworkX graph with weighted edges representing link capacity |

---

## Tools & Technologies

| Tool | Purpose |
|---|---|
| **Python 3.8+** | Core programming language |
| **NetworkX** | Network graph creation and path enumeration |
| **NumPy** | Random geometric graph generation and degree calculations *(100-node only)* |
| **SimPy** | Discrete-event simulation engine for modelling time and packet arrivals |
| **Matplotlib** | Chart generation and result visualisation |
| **HTML/CSS/JavaScript** | Live interactive browser demo (`index.html`) |
| **Chart.js** | Real-time charts inside the browser demo |

---

## Key Results

### 6-Node Version
- **Congestion events reduced by 50%**
- **Average queue length reduced by 6–28% on most nodes**
- **Node 2 (high traffic) showed 100% improvement** after early rerouting
- **First reroute triggered at t=1.0s** (before any congestion occurred)
- **Zero packet drops** in the prediction-enabled run

### 100-Node Version
- **~15 hot nodes** identified and monitored for early congestion buildup
- **Baseline**: hot nodes breach soft threshold then hard threshold — queues remain elevated
- **Early Prediction**: rerouting triggered as soon as soft threshold crossed — visible "catch and recover" pattern in queue timelines
- **CDF curve** for Early Prediction shifted clearly left of baseline
- **Heatmap**: "Baseline Congested" column dark for hot nodes; "Predicted Congested" near-zero

---

## Conclusion

Compared to no early prediction (both versions):

- Reduced packet loss (queues avoided before overflow)
- Lower end-to-end delay
- Improved throughput
- Better traffic distribution across nodes
- Fewer nodes reaching hard congestion state

---

## Advantages

- Predictive rather than reactive
- Lightweight (no ML, no DPI)
- Two-metric validation reduces false positives
- Path diversity awareness (longer clean path preferred over shorter congested one)
- Dijkstra in the 100-node version ensures scalability without sacrificing prediction accuracy

---

## Limitations

- Simulated environment (SimPy model)
- Static threshold values
- No feedback loop for rerouted traffic load
- Simplified queue drain model
- Assumes global state visibility (SDN-like control)
- No packet prioritization
- `all_simple_paths` (6-node) becomes slow beyond ~20 nodes — solved in the 100-node version with Dijkstra
- Random geometric graph (100-node) may produce varying topologies across different seeds

---

## Authors

- [Hana Maria Philip](https://github.com/hana-20092006)
- [Srijani Das](https://github.com/Srijani-Das07)

---

*This project was built as part of a Computer Networks course to demonstrate early congestion prediction using traffic trend analysis, without relying on packet loss as the primary congestion signal.*
