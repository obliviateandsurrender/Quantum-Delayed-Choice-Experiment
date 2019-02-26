# Importing PyQuil Libraries
from pyquil import Program, get_qc
from pyquil.gates import *
from pyquil.quil import DefGate
from pyquil.api import WavefunctionSimulator
from pyquil.parameters import Parameter, quil_sin, quil_cos, quil_exp
from pyquil.latex import to_latex
from math import pi, log2, sqrt
import itertools
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

t1 = [x for x in np.linspace(-np.pi/2, 3*np.pi/2, 32)]  #phi
t2 = [x for x in np.linspace(0, np.pi/2, 32)]  #alpha

phi = Parameter('phi')
u_1 = np.array([[1, 0],
                [0, quil_exp(phi)]])

# Get the Quil definition for the new gate
u_1_definition = DefGate('U1', u_1, [phi])
# Get the gate constructor
U1 = u_1_definition.get_constructor()

alpha = Parameter('alpha')
u_2 = np.array([[quil_cos(alpha), 0],
                [0, quil_sin(alpha)]])

# Get the Quil definition for the new gate
u_2_definition = DefGate('U2', u_2, [alpha])
# Get the gate constructor
U2 = u_2_definition.get_constructor()

ch = np.array([[1,0,0,0],[0,1,0,0],[0,0,1/np.sqrt(2), 1/np.sqrt(2)],[0,0,1/np.sqrt(2), -1/np.sqrt(2)]])
ch_definition = DefGate('CH', ch)
CH = ch_definition.get_constructor()

a = Parameter('a')
norm = np.array([[a,0],[0,a]])
norm_definition = DefGate('NM', norm, [a])
NM = norm_definition.get_constructor()
# Program Init
l = 0
ans = []
ansk = []
ansl = []
ansm = []
tr = 10000


def f(x, y):
    return x*len(t1)+y


result_a = []
result_b = []
result_c = []

for i in t1:
    for j in t2:
        #print(l)
        l+=1
        p = Program()
        ro = p.declare('ro', 'BIT', 2)
        wf1 = WavefunctionSimulator()
        p += u_2_definition
        p += ch_definition
        p += norm_definition
        p += H(0)
        p += NM(np.sqrt(2))(0)
        p += U2(j)(0) 
        p += H(1)
        p += PHASE(i,1)
        p += CH(0,1)

        result_c.append(wf1.wavefunction(p).get_outcome_probs())
        results = wf1.run_and_measure(p, trials=tr)
        #print(results)
        p = 0
        for k in results:
            if k[1] == 0:
                p+=1
        result_a.append(p)
        result_b.append([i,j])
        p = None
        wf1 = None

for i in range(0,len(result_a)):
    print(result_b[i])
    print(result_a[i]/tr)
    print(result_c[i])

x = np.linspace(-np.pi/2, 3*np.pi/2, len(t1))  # [x for x in range(0,50)]
y = np.linspace(0, np.pi/2, len(t2))  # [x for x in range(0,50)]
X, Y = np.meshgrid(x, y)
F = f(X, Y)
G = f(X, Y)

for i in range(0, len(F)):
    for j in range(0, len(G)):
        a = j*len(F)+i
        b = i*len(G)+j
        F[i][j] = float(result_a[a]/tr)

ax.plot_surface(X, Y, F, cmap='viridis', linewidth=0.75, edgecolors='black')
ax.set_xlabel(r'$\varphi$', fontsize=30)
ax.set_ylabel(r'$\alpha$',  fontsize=30)
ax.set_zlabel(r"$I_{D}$", rotation=180, fontsize=30)
ax.set_xticks([-.5*np.pi, 0, .5*np.pi, np.pi, 1.5*np.pi])
ax.set_xticklabels(
    [r"$\frac{-\pi}{2}$", "", "", "", r"$\frac{3\pi}{2}$"], fontsize=20)
ax.set_yticks([0, .125*np.pi ,.25*np.pi,.375*np.pi, .5*np.pi])
ax.set_yticklabels(
    [r"$0$", "", "", "", r"$\frac{1}{2}\pi$"], fontsize=20)
ax.set_zticks([0.0, 0.25 ,0.5, 0.75, 1.0])
ax.set_zticklabels(
    [r"$0.0$", "", "", "", r"$1.0$"], fontsize=20)
ax.grid(False)

plt.show()
