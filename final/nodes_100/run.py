import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run(file, desc):
    print(f"\n{'='*55}")
    print(f"  {desc}")
    print(f"{'='*55}")
    result = subprocess.run([sys.executable, file], capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ {file} failed. Fix errors above before continuing.")
        sys.exit(1)
    print(f"✅ {file} completed successfully.")

print("\n" + "="*55)
print("  CN PROJECT — Full Pipeline Runner")
print("="*55)
print("Running all files in order...\n")

run("network_setup.py",      "Step 1/6 — Building the Network")
run("congestion_monitor.py", "Step 2/6 — Testing Congestion Monitor")
run("adaptive_routing.py",   "Step 3/6 — Testing Adaptive Routing")
run("simulation.py",         "Step 4/6 — Running Simulation")
run("visualize.py",          "Step 5/6 — Generating Charts")
run("compare.py",            "Step 6/6 — Baseline vs Early Prediction Comparison")

print("\n" + "="*55)
print("  ALL STEPS COMPLETE!")
print("  results.png    — simulation output charts")
print("  comparison.png — baseline vs early prediction")
print("="*55 + "\n")