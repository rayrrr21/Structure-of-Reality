import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Toy Model for Quantum Darwinism / Environmental Decoherence
N_env = 1000 # Total degrees of freedom in the environment

def mutual_information_curve(f_size, N_total):
    """
    Phenomenological model of Zurek's Quantum Darwinism redundancy plateau.
    I(S:F) = H(S) + H(F) - H(S,F)
    """
    fraction = f_size / N_total
    
    if fraction == 0: return 0.0
    if fraction == 1: return 2.0 # Total information for a pure global state (System + Env)
    
    # 1. The Redundancy Plateau: Information about the system's pointer state
    # is acquired almost immediately from a tiny fraction of the environment.
    # It saturates at H(S) = 1.0 bit.
    plateau = 1.0 * (1.0 - np.exp(-100 * fraction))
    
    # 2. The Entanglement Tail: To get the full quantum phase information,
    # the observer must capture the ENTIRE environment (fraction -> 1.0).
    tail = 1.0 * np.exp(100 * (fraction - 1))
    
    return plateau + tail

f_sizes = np.arange(0, N_env + 1)
I_SF = [mutual_information_curve(f, N_env) for f in f_sizes]

# Visualization
plt.style.use('dark_background')
plt.figure(figsize=(10,6))
plt.plot(f_sizes / N_env, I_SF, 'c-', lw=3, label="Mutual Information I(S:F)")

# Annotate Classical Reality Threshold
plt.axhline(1.0, color='r', linestyle='--', label="Classical Threshold H(S)")
plt.fill_between(f_sizes / N_env, 0, I_SF, where=(np.array(I_SF) >= 0.99) & (np.array(I_SF) <= 1.01), color='cyan', alpha=0.2, label="Redundancy Plateau (Classical Reality)")

plt.xlabel("Environment Fragment Size (Fraction of Total Env)", fontsize=12)
plt.ylabel("Information Shared (Bits)", fontsize=12)
plt.title("Quantum Darwinism: The Redundancy Plateau", fontsize=14, pad=15)
plt.legend(loc="lower right")

# Annotations for JIT rendering
plt.text(0.1, 1.1, 'The "Render" happens here:\nInformation is massively duplicated.', color='white', fontsize=10)
plt.text(0.7, 0.2, 'To see quantum coherence,\nyou need 100% of the universe.', color='white', fontsize=10)

plt.tight_layout()
save_path = os.path.join(RESULTS_DIR, "darwinism_plateau.png")
plt.savefig(save_path, dpi=300)
print(f"DONE. Quantum Darwinism simulation saved to {save_path}", flush=True)
