# Early Congestion Prediction and Adaptive Routing

This repository contains **two working versions** of the project:

## 📁 `nodes_6/` — Original 6-Node Version
The original working implementation with a small 6-node network topology.
- Easier to visualize and debug
- Faster simulation runs
- Good for understanding the core logic

**Run:**
```bash
cd nodes_6
python run.py
```

## 📁 `nodes_100/` — Scaled 100-Node Version
The scaled-up implementation supporting a 100-node network.
- Realistic large-scale topology
- Updated graphs and visualizations for 100 nodes
- `package-lock.json` included for frontend dependencies

**Run:**
```bash
cd nodes_100
python run.py
```

## Files in Each Version
| File | Purpose |
|------|---------|
| `network_setup.py` | Defines the network topology (6 or 100 nodes) |
| `simulation.py` | Traffic simulation logic |
| `adaptive_routing.py` | Routing algorithm |
| `congestion_monitor.py` | Congestion detection & prediction |
| `compare.py` | Comparison graphs and analysis |
| `visualize.py` | Visualization helpers |
| `run.py` | Entry point |
| `index.html` | Frontend demo |

## Requirements
```bash
pip install -r requirements.txt
```
