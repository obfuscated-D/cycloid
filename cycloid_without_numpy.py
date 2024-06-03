import math
import matplotlib.pyplot as plt

def generate_coordinates(num_points, R, E, N, R_r):
    t = [i * 2 * math.pi / (num_points - 1) for i in range(num_points)]
    atan_term = [math.atan2(math.sin((1 - N) * ti), (R / (E * N)) - math.cos((1 - N) * ti)) for ti in t]
    
    X = [(R * math.cos(ti)) - (R_r * math.cos(ti + at)) - (E * math.cos(N * ti)) for ti, at in zip(t, atan_term)]
    Y = [(-R * math.sin(ti)) + (R_r * math.sin(ti + at)) + (E * math.sin(N * ti)) for ti, at in zip(t, atan_term)]
    
    return X, Y

def draw_cycloidal_rotor(num_points,R, E,N,R_r):
    x_rotor, y_rotor = generate_coordinates(num_points,R, E,N,R_r)
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
num_points = 1000

draw_cycloidal_rotor(num_points,R, E,N,R_r)