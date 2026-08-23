import numpy as np
from scipy.integrate import solve_ivp
import os

SEED = 42
DT = 0.05
T_MAX = 200.0
OBS_NOISE_STD = 0.5
GAP_FRACTIONS = np.array([0.05, 0.1, 0.2, 0.4]) # 10s, 20s, 40s, 80s gaps

def rossler_deriv(t, state):
    x, y, z = state
    a, b, c = 0.2, 0.2, 5.7
    return [-y - z, x + a*y, b + z*(x - c)]

def rossler_jacobian(state):
    x, y, z = state
    a, c = 0.2, 5.7
    return np.array([
        [0.0, -1.0, -1.0],
        [1.0, a, 0.0],
        [z, 0.0, x - c]
    ])

def extended_kalman_smoother(t, obs, start_idx, end_idx):
    n_steps = len(t)
    dim = 3
    x_est = np.zeros((n_steps, dim))
    P_est = np.zeros((n_steps, dim, dim))
    x_pred = np.zeros((n_steps, dim))
    P_pred = np.zeros((n_steps, dim, dim))
    
    x_est[0] = obs[0]
    P_est[0] = np.eye(dim) * (OBS_NOISE_STD**2)
    Q = np.eye(dim) * 1e-4
    R = np.eye(dim) * (OBS_NOISE_STD**2)
    
    for k in range(1, n_steps):
        dt = t[k] - t[k-1]
        x_prev = x_est[k-1]
        
        sol = solve_ivp(rossler_deriv, (0, dt), x_prev, method='RK45')
        x_pred[k] = sol.y[:, -1]
        
        F = np.eye(dim) + rossler_jacobian(x_prev) * dt
        P_pred[k] = F @ P_est[k-1] @ F.T + Q * dt
        
        if start_idx <= k < end_idx:
            x_est[k] = x_pred[k]
            P_est[k] = P_pred[k]
        else:
            y = obs[k] - x_pred[k]
            S = P_pred[k] + R
            K = P_pred[k] @ np.linalg.inv(S)
            x_est[k] = x_pred[k] + K @ y
            P_est[k] = (np.eye(dim) - K) @ P_pred[k]
            
    x_smooth = np.copy(x_est)
    P_smooth = np.copy(P_est)
    
    for k in range(n_steps - 2, -1, -1):
        dt = t[k+1] - t[k]
        F = np.eye(dim) + rossler_jacobian(x_smooth[k]) * dt
        C = P_est[k] @ F.T @ np.linalg.inv(P_pred[k+1])
        x_smooth[k] = x_est[k] + C @ (x_smooth[k+1] - x_pred[k+1])
        P_smooth[k] = P_est[k] + C @ (P_smooth[k+1] - P_pred[k+1]) @ C.T
        
    return x_smooth

if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    x0 = np.array([1.0, 1.0, 1.0])
    sol_warmup = solve_ivp(rossler_deriv, (0, 50), x0, method='RK45', t_eval=[50])
    x0 = sol_warmup.y[:, -1]
    
    t_eval = np.arange(0, T_MAX, DT)
    sol = solve_ivp(rossler_deriv, (0, T_MAX), x0, method='RK45', t_eval=t_eval)
    t = sol.t
    true_s = sol.y.T
    obs = true_s + rng.standard_normal(true_s.shape) * OBS_NOISE_STD
    
    for gap_frac in GAP_FRACTIONS:
        gap_dur = gap_frac * T_MAX
        start_t, end_t = T_MAX/2 - gap_dur/2, T_MAX/2 + gap_dur/2
        
        start_idx = np.searchsorted(t, start_t)
        end_idx = np.searchsorted(t, end_t)
        
        smoothed = extended_kalman_smoother(t, obs, start_idx, end_idx)
        gap_mse = np.mean((true_s[start_idx:end_idx] - smoothed[start_idx:end_idx])**2)
        print(f"Rossler Gap {gap_frac} (Dur {gap_dur}s): MSE = {gap_mse:.2f}", flush=True)
