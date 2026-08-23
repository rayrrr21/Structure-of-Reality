import numpy as np
from scipy.integrate import solve_ivp
import json
import os
import sys

SEED = 42
N_TRAJECTORIES = 3  # Very fast preview
DT = 0.01
T_MAX = 20.0
OBS_NOISE_STD = 0.5
GAP_FRACTIONS = np.array([0.01, 0.2, 0.6])

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
np.random.seed(SEED)

class Lorenz63:
    name = "Lorenz '63"
    short_name = "Lorenz"
    dim = 3
    @staticmethod
    def dynamics(t, state):
        x, y, z = state
        return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0/3.0) * z]
    @staticmethod
    def initial_state(rng):
        return np.array([1.0, 1.0, 1.0]) + rng.standard_normal(3) * 0.1

class DampedHarmonicOscillator:
    name = "Damped Harmonic Oscillator"
    short_name = "DHO"
    dim = 2
    @staticmethod
    def dynamics(t, state):
        x, v = state
        return [v, -2*0.1*1.0*v - 1.0**2*x]
    @staticmethod
    def initial_state(rng):
        return rng.standard_normal(2) * 2.0

SYSTEMS = [Lorenz63, DampedHarmonicOscillator]

def generate_trajectory(system, rng, dt=DT, t_max=T_MAX):
    x0 = system.initial_state(rng)
    t_eval = np.arange(0, t_max, dt)
    if system.short_name == "Lorenz":
        sol_warmup = solve_ivp(system.dynamics, (0, 30), x0, method='RK23', t_eval=[30])
        x0 = sol_warmup.y[:, -1]
    sol = solve_ivp(system.dynamics, (0, t_max), x0, method='RK23', t_eval=t_eval)
    return sol.t, sol.y.T if sol.status == 0 else (None, None)

def model_a_forward_filter(t_eval, obs, start_idx, end_idx, system):
    if start_idx <= 0: return np.zeros((end_idx - start_idx, system.dim))
    est = obs[start_idx-1]
    times = t_eval[start_idx:end_idx]
    if len(times) == 0: return np.zeros((0, system.dim))
    try:
        sol = solve_ivp(system.dynamics, (times[0], times[-1]), est, method='RK23', t_eval=times)
        if sol.status == 0: return sol.y.T
    except: pass
    return np.tile(est, (len(times), 1))

def model_b_backward_filter(t_eval, obs, start_idx, end_idx, system):
    if end_idx >= len(t_eval): return np.zeros((end_idx - start_idx, system.dim))
    est = obs[end_idx]
    times = t_eval[start_idx:end_idx]
    if len(times) == 0: return np.zeros((0, system.dim))
    try:
        rev_dyn = lambda t, s: [-x for x in system.dynamics(-t, s)]
        sol = solve_ivp(rev_dyn, (-times[-1], -times[0]), est, method='RK23', t_eval=-times[::-1])
        if sol.status == 0: return sol.y.T[::-1]
    except: pass
    return np.tile(est, (len(times), 1))

def model_c_smoother(t_eval, obs, start_idx, end_idx, system):
    gap_len = end_idx - start_idx
    if gap_len == 0: return np.zeros((0, system.dim))
    fwd = model_a_forward_filter(t_eval, obs, start_idx, end_idx, system)
    bwd = model_b_backward_filter(t_eval, obs, start_idx, end_idx, system)
    alpha = np.linspace(0, 1, gap_len).reshape(-1, 1)
    return (1 - alpha) * fwd + alpha * bwd

if __name__ == "__main__":
    results = {}
    for system in SYSTEMS:
        print(f"Running {system.name}...", flush=True)
        sys_res = []
        for gap_frac in GAP_FRACTIONS:
            gap_dur = gap_frac * T_MAX
            start_t, end_t = T_MAX/2 - gap_dur/2, T_MAX/2 + gap_dur/2
            errs = []
            for i in range(N_TRAJECTORIES):
                rng = np.random.default_rng(SEED + i)
                t, true_s = generate_trajectory(system, rng)
                if t is None: continue
                obs = true_s + rng.standard_normal(true_s.shape) * OBS_NOISE_STD
                start_idx, end_idx = np.searchsorted(t, start_t), np.searchsorted(t, end_t)
                if end_idx <= start_idx: continue
                
                recon = model_c_smoother(t, obs, start_idx, end_idx, system)
                true_gap = true_s[start_idx:end_idx]
                min_len = min(len(true_gap), len(recon))
                if min_len > 0:
                    errs.append(np.mean((true_gap[:min_len] - recon[:min_len])**2))
            
            sys_res.append({"gap": float(gap_frac), "mse": float(np.mean(errs)) if errs else None})
        results[system.short_name] = sys_res
    
    with open(os.path.join(RESULTS_DIR, "tsr_exp001_fast.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("DONE", flush=True)
