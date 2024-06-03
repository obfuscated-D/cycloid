import numpy as np
import matplotlib.pyplot as plt

def cycloidal_rotor(R, R_r, E, N, num_points=1000):
    t = np.linspace(0, 2 * np.pi, num_points)
    atan_term = np.arctan2(np.sin((1 - N) * t), (R / (E * N)) - np.cos((1 - N) * t))
    X = (R * np.cos(t)) - (R_r * np.cos(t + atan_term)) - (E * np.cos(N * t))
    Y = (-R * np.sin(t)) + (R_r * np.sin(t + atan_term)) + (E * np.sin(N * t))
    return X, Y

def draw_cycloidal_rotor(R, R_r, E, N):
    x_rotor, y_rotor = cycloidal_rotor(R, R_r, E, N)
    plt.figure(figsize=(8, 8))
    plt.plot(x_rotor, y_rotor, label='Cycloidal Rotor')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('cycloidal')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)
    plt.show()
    
R = 20  
R_r = 3  
E = 1.5    
N = 10    

draw_cycloidal_rotor(R, R_r, E, N)
