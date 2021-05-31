"""

Functions that act on DynSys or DynMap objects

"""

import numpy as np

from .utils import *

def sample_initial_conditions(model, points_to_sample, traj_length=1000, pts_per_period=30):
    """
    Generate a random sample of initial conditions from a dynamical system
    
    Args:
        model (callable): the right hand side of a differential equation, in format func(X, t)
        points_to_sample (int): the number of random initial conditions to sample
        traj_length (int): the total length of the reference trajectory from which points are drawn
        pts_per_period (int): the sampling density of the trajectory
        
    Returns:
        sample_points (ndarray): The points with shape (points_to_sample, d)
    
    """

    initial_sol = model.make_trajectory(traj_length, resample=True, pts_per_period=pts_per_period)
    sample_inds = np.random.choice(np.arange(initial_sol.shape[1]), points_to_sample, replace=False)
    sample_pts = initial_sol[:, sample_inds].T
    
    return sample_pts


def find_lyapunov_exponents(model, traj_length, pts_per_period=500):
    """
    Given a dynamical system, compute its spectrum of Lyapunov exponents
    
    Args:
        model (callable): the right hand side of a differential equation, in format func(X, t)
        traj_length (int): the length of each trajectory used to calulate Lyapunov 
            exponents
        pts_per_period (int): the sampling density of the trajectory
        
    Returns:
        final_lyap (ndarray): A list of computed Lyapunov exponents
            
    """
    d = np.asarray(model.ic).shape[-1]
    tpts, traj = model.make_trajectory(traj_length, pts_per_period=pts_per_period, resample=True, return_times=True)
    dt = np.median(np.diff(tpts))
    
    u = np.identity(d)
    all_lyap = list()
    for i in range(traj_length):
        yval = traj[:, i]
        fcast = lambda x : np.array(model.rhs(x, tpts[i]))
        jacval = jac_fd(fcast, yval)
        u_n = np.matmul(np.identity(d) + jacval * dt, u)
        q, r = np.linalg.qr(u_n)
        all_lyap.append(np.log(abs(r.diagonal())))
        u = q #new axes after iteration
    
    all_lyap = np.array(all_lyap)
    final_lyap = np.sum(all_lyap, axis=0) / (dt * traj_length)
    return final_lyap