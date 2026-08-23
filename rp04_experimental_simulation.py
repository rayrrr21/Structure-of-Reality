import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Simulation Parameters
theta = np.linspace(0, np.pi/2, 100) # Angle of initial superposition

# Probabilities of the rendered states
p0 = np.cos(theta/2)**2
p1 = np.sin(theta/2)**2

# Shannon Entropy (Information erased during the reset/render)
# Using np.maximum to avoid log(0)
entropy = -p0 * np.log(np.maximum(p0, 1e-15)) - p1 * np.log(np.maximum(p1, 1e-15))

# By Landauer's Principle, Qdiss / kT >= Entropy (in nats)
q_diss_expected = entropy

# Simulate experimental noise in the NIS calorimeter readings
np.random.seed(42)
noise = np.random.normal(0, 0.03, size=len(theta))
q_diss_measured = np.maximum(q_diss_expected + noise, 0) # Heat cannot be negative

# Theoretical Landauer Limit
landauer_limit = np.log(2) # ~0.693

# Visualization
plt.style.use('dark_background')
plt.figure(figsize=(10,6))

plt.scatter(entropy, q_diss_measured, color='cyan', alpha=0.6, label='Simulated NIS Calorimeter Data')
plt.plot(entropy, q_diss_expected, 'w--', lw=2, label='Theoretical Landauer Bound (Q/kT = S)')

# Annotate the max limit
plt.axhline(landauer_limit, color='r', linestyle=':', lw=2, label=r'Maximum Entropy Render Limit (ln 2)')
plt.axvline(landauer_limit, color='r', linestyle=':', lw=2)

plt.xlabel('Rendered Information Entropy $S$ (nats)', fontsize=12)
plt.ylabel(r'Normalized Dissipated Heat $\langle Q_{diss} \rangle / kT$', fontsize=12)
plt.title('Theoretical Forecast of the "Render Trigger" Experiment\nSuperconducting Qubit Calorimetry', fontsize=14, pad=15)
plt.legend(loc='upper left')

plt.tight_layout()
save_path = os.path.join(RESULTS_DIR, 'landauer_render_experiment.png')
plt.savefig(save_path, dpi=300)
print(f"DONE. Experimental simulation saved to {save_path}", flush=True)
