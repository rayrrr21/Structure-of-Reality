import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Simulation Parameters for the Spatiotemporal Chaotic System
N_SITES = 101 # 1D Spatial grid representing the "bulk" of the causal diamond
CENTER = N_SITES // 2
T_STEPS = 50
COUPLING = 0.4 # Diffusive spatial coupling
R = 3.99 # Highly chaotic logistic map parameter

def logistic_map(x):
    return R * x * (1 - x)

def step(x):
    # Apply local chaotic map
    fx = logistic_map(x)
    
    # Apply spatial coupling to neighbors (simulating the metric spread of information)
    x_new = np.copy(fx)
    for i in range(1, N_SITES - 1):
        x_new[i] = (1 - COUPLING) * fx[i] + (COUPLING / 2) * (fx[i-1] + fx[i+1])
    
    # Absorbing boundaries (the holographic edge of the causal diamond)
    x_new[0] = (1 - COUPLING) * fx[0] + COUPLING * fx[1]
    x_new[-1] = (1 - COUPLING) * fx[-1] + COUPLING * fx[-2]
    return x_new

if __name__ == "__main__":
    np.random.seed(42)
    # Generate a random initial state for the bulk
    x_base = np.random.rand(N_SITES)

    # Create a clone universe with a microscopic perturbation at the dead center
    x_pert = np.copy(x_base)
    x_pert[CENTER] += 1e-10

    diff_history = np.zeros((T_STEPS, N_SITES))

    for t in range(T_STEPS):
        # Record the difference (analogue to the OTOC / Information Spread)
        diff_history[t, :] = np.abs(x_pert - x_base)
        
        # Evolve both universes
        x_base = step(x_base)
        x_pert = step(x_pert)

    # Plot the Causal Diamond / Information Scrambling
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    
    # We plot the log of the difference to see the wavefront clearly
    plt.imshow(np.log10(diff_history + 1e-15), aspect='auto', cmap='magma', origin='lower')
    cbar = plt.colorbar()
    cbar.set_label('Log10(Information Difference)', fontsize=12)
    
    plt.xlabel('Spatial Coordinate (Bulk)', fontsize=12)
    plt.ylabel('Time Steps', fontsize=12)
    plt.title('Holographic Scrambling: Information Leaking to the Boundaries', fontsize=14, pad=15)

    # Draw the causal light cone (Lieb-Robinson Bound)
    # The effective "speed of light" in this lattice is bounded by the coupling
    c = 1.0 # arbitrary speed for visual bounds
    plt.plot([CENTER, 0], [0, CENTER/c], 'w--', alpha=0.5, label='Causal Horizon (Lieb-Robinson Bound)')
    plt.plot([CENTER, N_SITES-1], [0, CENTER/c], 'w--', alpha=0.5)

    plt.legend(loc='upper right')
    plt.tight_layout()
    
    save_path = os.path.join(RESULTS_DIR, 'holographic_scrambling.png')
    plt.savefig(save_path, dpi=300)
    print(f"DONE. Holographic scrambling simulation saved to {save_path}", flush=True)
