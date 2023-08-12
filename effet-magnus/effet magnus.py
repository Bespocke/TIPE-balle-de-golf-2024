#%%


import numpy as np
import sympy as sp
import sympy.vector as sv
import matplotlib.pyplot as plt

# Définition du système de coordonnées
R0 = sv.CoordSys3D('R_0')
x = R0.x
y = R0.y

# Définition des symboles
U0, R, K, Gamma = sp.symbols('U_0 R K Gamma')

# Définition du potentiel et de la fonction de courant
psi1 = U0 * y  # Champ uniforme
psi2 = -K * y / (x**2 + y**2)  # Doublet
psi3 = -Gamma / (2 * sp.pi) * sp.log(x**2 + y**2)  # Tourbillon
psi = psi1 + psi2.subs(K, U0 * R**2) + psi3  # Solution générale

# Fonction pour tracer les solutions
def trace_solution(psi, R, titre):
    # Conversion en fonction numpy
    F = sp.lambdify([R0.x, R0.y], psi, 'numpy')
    # Grille de calcul
    N = 40
    X1 = np.linspace(-3 * R, 3 * R, N)
    Y1 = np.linspace(-2 * R, 2 * R, N)
    X, Y = np.meshgrid(X1, Y1)
    FXY = F(X, Y)
    # Filtrage
    for i in range(N):
        for j in range(N):
            if (X[i, j]**2 + Y[i, j]**2) < 0.8 * R**2:
                FXY[i, j] = 0.
    # Tracer
    plt.figure(figsize=(10, 8))
    ax = plt.gca()
    CS = ax.contour(X, Y, FXY, levels=31)
    ax.clabel(CS, inline=1, fontsize=10)
    plt.axis('equal')
    if titre != None:
        ax.set_title(titre)
    cercle = plt.Circle((0., 0.), R, color='k', zorder=10)
    ax.add_artist(cercle)
    return

# Cas uniforme psi=psi1
#rayon = 1
#valnum = {U0: 2, R: 0, Gamma: 0}
#psi0 = psi.subs(valnum)
#trace_solution(psi0, rayon, "Ecoulement uniforme")

# Cas sans rotation psi=psi1+psi2
#valnum = {U0: 2, R: rayon, Gamma: 0}
#psi0 = psi.subs(valnum)
#trace_solution(psi0, rayon, "Balle")

# Cas avec rotation: psi=psi1+psi2+psi3
#valnum = {U0: 2, R: rayon, Gamma: 15}
#psi0 = psi.subs(valnum)
#trace_solution(psi0, rayon, "Balle en rotation")

# Cas avec rotation : psi = psi1 + psi2 + psi3
#valnum = {U0: 2, R: rayon, Gamma: -15}  # Utiliser un nombre négatif pour inverser le sens de rotation
#psi0 = psi.subs(valnum)
#trace_solution(psi0, rayon, "Balle en rotation (sens inverse)")

# Cas avec rotation et tourbillon : psi = psi1 + psi2 + psi3
rayon = 1
valnum = {U0: 2, R: rayon, K: 5, Gamma: 5}
psi0 = psi + psi3.subs(Gamma, valnum[Gamma])  # Ajout de la contribution du tourbillon
trace_solution(psi0, rayon, "Balle en rotation avec tourbillon")



# Calcul de la pression
Nabla = sv.Del()
rho0 = sp.symbols('rho_0')
p = sp.Function('p')(x, y)
u = sp.Function('u')(x, y)
v = sp.Function('v')(x, y)
U = u * R0.i + v * R0.j
pr = rho0 * U0**2 / 2 - rho0 / 2 * sv.gradient(psi).dot(sv.gradient(psi))

# Affichage des résultats pour les cas sans rotation et avec rotation
#valnum = {rho0: 1, U0: 2, R: rayon, Gamma: 0}
#pr0 = pr.subs(valnum)
#trace_solution(pr0, rayon, "Pression cylindre immobile")

#valnum = {rho0: 1, U0: 2, R: rayon, Gamma: 5}
#pr0 = pr.subs(valnum)
#trace_solution(pr0, rayon, "Pression cylindre en rotation")


#%%