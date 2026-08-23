import numpy as np
from scipy.integrate import solve_ivp
import json
import os

SEED = 42
DT = 0.01
T_MAX = 20.0
OBS_NOISE_STD = 0.5
GAP_FRACTIONS = np.array([0.01, 0.05, 0.1, 0.2, 0.4, 0.6])

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
np.random.seed(SEED)

def lorenz_deriv(t, state):
    x, y, z = state
    return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0/3.0) * z]

def lorenz_jacobian(state):
    x, y, z = state
    return np.array([
        [-10.0, 10.0, 0.0],
        [28.0 - z, -1.0, -x],
        [y, x, -8.0/3.0]
    ])

def generate_lorenz(rng):
    x0 = np.array([1.0, 1.0, 1.0]) + rng.standard_normal(3) * 0.1
    sol_warmup = solve_ivp(lorenz_deriv, (0, 30), x0, method='RK45', t_eval=[30])
    x0 = sol_warmup.y[:, -1]
    
    t_eval = np.arange(0, T_MAX, DT)
    sol = solve_ivp(lorenz_deriv, (0, T_MAX), x0, method='RK45', t_eval=t_eval)
    return sol.t, sol.y.T

def extended_kalman_smoother(t, obs, start_idx, end_idx):
    """
    Runs an EKF forward over the whole trajectory (ignoring obs in the gap),
    then runs an RTS smoother backward.
    """
    n_steps = len(t)
    dim = 3
    
    # Storage
    x_est = np.zeros((n_steps, dim))
    P_est = np.zeros((n_steps, dim, dim))
    x_pred = np.zeros((n_steps, dim))
    P_pred = np.zeros((n_steps, dim, dim))
    
    # EKF Initialization
    x_est[0] = obs[0]
    P_est[0] = np.eye(dim) * (OBS_NOISE_STD**2)
    
    Q = np.eye(dim) * 1e-4  # Process noise
    R = np.eye(dim) * (OBS_NOISE_STD**2)  # Measurement noise
    H = np.eye(dim)
    
    # Forward Pass (EKF)
    for k in range(1, n_steps):
        # Predict
        dt = t[k] - t[k-1]
        x_prev = x_est[k-1]
        
        # Integrate forward one step
        sol = solve_ivp(lorenz_deriv, (0, dt), x_prev, method='RK45')
        x_pred[k] = sol.y[:, -1]
        
        # State transition matrix F approx
        F = np.eye(dim) + lorenz_jacobian(x_prev) * dt
        P_pred[k] = F @ P_est[k-1] @ F.T + Q * dt
        
        # Update (if not in gap)
        if start_idx <= k < end_idx:
            # In gap: no observation update
            x_est[k] = x_pred[k]
            P_est[k] = P_pred[k]
        else:
            # Have observation
            y = obs[k] - x_pred[k]  # Innovation
            S = P_pred[k] + R
            K = P_pred[k] @ np.linalg.inv(S)
            x_est[k] = x_pred[k] + K @ y
            P_est[k] = (np.eye(dim) - K) @ P_pred[k]
            
    # Backward Pass (RTS Smoother)
    x_smooth = np.copy(x_est)
    P_smooth = np.copy(P_est)
    
    for k in range(n_steps - 2, -1, -1):
        dt = t[k+1] - t[k]
        F = np.eye(dim) + lorenz_jacobian(x_smooth[k]) * dt
        
        C = P_est[k] @ F.T @ np.linalg.inv(P_pred[k+1])
        x_smooth[k] = x_est[k] + C @ (x_smooth[k+1] - x_pred[k+1])
        P_smooth[k] = P_est[k] + C @ (P_smooth[k+1] - P_pred[k+1]) @ C.T
        
    return x_smooth, P_smooth

if __name__ == "__main__":
    results = []
    
    for gap_frac in GAP_FRACTIONS:
        gap_dur = gap_frac * T_MAX
        start_t, end_t = T_MAX/2 - gap_dur/2, T_MAX/2 + gap_dur/2
        
        rng = np.random.default_rng(SEED)
        t, true_s = generate_lorenz(rng)
        obs = true_s + rng.standard_normal(true_s.shape) * OBS_NOISE_STD
        
        start_idx = np.searchsorted(t, start_t)
        end_idx = np.searchsorted(t, end_t)
        
        smoothed, P_smooth = extended_kalman_smoother(t, obs, start_idx, end_idx)
        
        # Calculate MSE exactly in the middle of the gap (the hardest point)
        mid_idx = (start_idx + end_idx) // 2
        
        gap_mse = np.mean((true_s[start_idx:end_idx] - smoothed[start_idx:end_idx])**2)
        midpoint_mse = np.mean((true_s[mid_idx] - smoothed[mid_idx])**2)
        
        # Calculate theoretical variance from the Smoother Covariance Matrix
        # This is the Cramér-Rao Lower Bound that correctly diverges monotonically
        theo_var = np.trace(P_smooth[mid_idx])
        
        results.append({
            "gap_fraction": float(gap_frac),
            "lyapunov_times": float(gap_dur / 1.1), # Lorenz lyapunov time ~ 1.1s
            "mean_gap_mse": float(gap_mse),
            "midpoint_mse": float(midpoint_mse),
            "theoretical_variance": float(theo_var)
        })
        print(f"Gap {gap_frac}: MSE = {gap_mse:.2f}, Theo Var = {theo_var:.2e}", flush=True)

    with open(os.path.join(RESULTS_DIR, "tsr_exp002_eks.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("DONE", flush=True)
