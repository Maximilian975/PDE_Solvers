import numpy as np
import scipy.sparse.linalg as spsplg
import scipy.linalg as splg
import scipy.sparse as spsp
from scipy.sparse import kron, csc_matrix, eye, vstack, bmat
from mpl_toolkits.mplot3d import Axes3D

import operators as ops
import matplotlib.pyplot as plt
import time
import rungekutta4 as rk4
import pylab
from matplotlib import cm
# Model parameters
c = 3 # wave speed
T = 3 # end time
xl = -1 # left boundary
xr = 1 # right boundary
yl = -1/2
yr = 1/2

L = xr - xl # domain length
k = 2*np.pi
def run_simulation(mx, my, show_animation=True):
    """Solves the advection equation using finite differences
    and Runge-Kutta 4.
    
    Method parameters: 
    mx:     Number of grid points, integer > 15.
    order:  Order of accuracy, 2, 4, 6, 8, 10 or 12
    """
    # Space discretization
    hx = (xr - xl)/(mx-1)
    hy = (yr - yl)/(my-1)
    
    eyex = np.identity(mx)
    eyey = np.identity(my)
    
    xvec = np.linspace(xl, xr-hx, mx)
    yvec = np.linspace(yl, yr-hy, my)
    X,Y = np.meshgrid(yvec,xvec)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    # _, _, D1 = ops.periodic_expl(mx, hx, order)
    H,HIx,D1,D2x,e_lx,e_rx,d1_lx,d1_rx = ops.sbp_cent_6th(mx,hx)
    H,HIy,D1,D2y,e_ly,e_ry,d1_ly,d1_ry = ops.sbp_cent_6th(my,hy)
    # print(D2x[125])
    c = 3
    tauL = c**2
    tauR = -c**2
    D2xx = c**2*D2x + tauL*HIx@e_lx.T@d1_lx + tauR*HIx@e_rx.T@d1_rx
    D2yy = c**2*D2y + tauR*HIy@e_ly.T@d1_ly + tauR*HIy@e_ry.T@d1_ry
    D = kron(eyey,D2xx) + kron(D2yy,eyex) 

    # Define right-hand-side function
    def rhs(u):
        HL = np.array([u[1],D@u[0]])
        
        # print(HL)
        return HL
    # Time discretization
    ht_try = 0.1*hx/c
    mt = int(np.ceil(T/ht_try)) # round up so that (mt-1)*ht = T
    tvec, ht = np.linspace(0, T, mt, retstep=True)

    # Initialize time variable and solution vector
    t = 0

    u = np.zeros((mx*my))
    u_t = np.zeros((mx*my))
    for y in range(my):
        for x in range(mx):
            # print(hx*x-1)
        
            u[y*mx + x] = np.exp((-(hx*x-1)**2-(hy*y-1/2)**2)/0.05**2)
    
    # print(u.tolist())
    
    w = np.array([u,u_t])

    # Initialize plot for animation
    if show_animation:
        
        plt.show()
    # Loop over all time steps
    for tidx in range(mt):

        # Take one step with the fourth order Runge-Kutta method.
        w, t = rk4.step(rhs, w, t, ht)
        # Update plot every 50th time step
        if tidx % 1 == 0 and show_animation: 
            solution = np.reshape(w[0],(mx,my))
            ax.contour3D(X, Y, solution, 50, cmap='binary')
            
            ax.set_title(t)
            # print(t)
            #line.set_ydata(w[0])
            #title.set_text(f't = {t:.2f}')
            plt.draw()
            plt.pause(1e-8)

    # Close figure window
    if show_animation:
        plt.close()

    return w, T, X, Y, hx, hy, L, c

def exact_solution(t, xvec, L, c):
    # T1 = L/c  # Time for one lap
    # t_eff = (t/T1 - np.floor(t/T1))*T1  # "Effective" time, using periodicity
    # u_exact = f(xvec - c*t_eff)

    
    u_exact = np.cos(k*xvec)*np.cos(c*k*T)
    return u_exact

def l2_norm(vec, h):
    return np.sqrt(h)*np.sqrt(np.sum(vec**2))

def compute_error(u, u_exact, hx):
    """Compute discrete l2 error"""
    error_vec = u - u_exact
    relative_l2_error = l2_norm(error_vec, hx)/l2_norm(u_exact, hx)
    return relative_l2_error
    # error = l2_norm(error_vec,hx)
    # return error

def plot_final_solution(u, u_exact, X, Y, T):
    ax = plt.axes(projection='3d')
    ax.contour3D(X, Y, u, 50, cmap="rainbow")
    plt.show()
    




def main():
    mx = 200
    my = 100
    u, T, X, Y, hx, hy, L, c = run_simulation(mx=mx, my=my, show_animation=False)  
    solution = np.reshape(u[0],(mx,my))
    plot_final_solution(solution,0,X,Y,0)


if __name__ == '__main__':
    main()