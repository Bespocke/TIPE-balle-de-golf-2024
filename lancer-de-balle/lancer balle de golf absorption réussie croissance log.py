#%%
import pygame
import numpy as np
from colorama import Fore, Style
import random as rd
import time

aaa = True
temps_rota = 0.3

def print_red(text):
    print("\033[91m" + text + "\033[0m")
def print_blue(text):
    print("\033[94m" + text + "\033[0m")
def print_green(text):
    print("\033[32m" + text + "\033[0m")

def max_dico(D):
    m = 0
    c = 0
    for e in D:
        if D[e] > m:
            m = D[e]
            c = e
    return (m, c)

def min_dico(D):
    m = float('inf')  # Initialiser m à une valeur infinie
    c = None  # Initialiser c à None
    for cle, valeur in D.items():
        if valeur < m:
            m = valeur
            c = cle
    return (m, c)    

def print_dico(D):
    m, c = max_dico(D)
    for e in D:
        if e == c:
            texte = f"{np.degrees(e)}: {D[e]}"
            texte_colore = f"{Fore.RED}{texte}{Style.RESET_ALL}"
            print(texte_colore)
        else:
            texte = f"{np.degrees(e)}: {D[e]}"
            print(texte)

class Masse:
    def __init__(self, masse, rayon, pos, vit, acc, ang, couleur):
        self.x, self.y = pos
        self.vit_x, self.vit_y = vit * np.cos(ang), vit * np.sin(ang)
        self.acc_x, self.acc_y = acc, acc
        self.masse = masse
        self.rayon = rayon
        self.couleur = couleur
        self.ang = ang
        self.spin = True
    def rota(self):
        global aaa
        global temps_rota

        if self.spin:
            if aaa:
                self.temps_debut = time.time()  # Enregistrer l'heure de début du chronomètre
                aaa = False

            temps_ecoule = time.time() - self.temps_debut
            if temps_ecoule >= temps_rota:
                self.spin = False
            else:
                # Calculer la vitesse angulaire progressive en utilisant une fonction logarithmique
                temps_ecoule_normalise = temps_ecoule / temps_rota  # Normaliser le temps écoulé entre 0 et 1
                vitesse_angulaire_max = 10  # Vitesse angulaire maximale (vous pouvez ajuster cette valeur)
                vitesse_angulaire = vitesse_angulaire_max * np.log(1 + temps_ecoule_normalise)

                # Mettre à jour la vitesse angulaire de la balle
                self.ang += vitesse_angulaire

class Sol:
    def __init__(self, altitude, hauteur, largeur, absor):
        self.altitude = altitude
        self.hauteur = hauteur
        self.largeur = largeur
        self.absor = absor

class main:
    def __init__(self, width, height, Sol, grav, frot, frot_s):
        self.width, self.height = width, height
        self.batis_x, self.batis_y = self.width // 2, 100
        self.Masse = []
        self.Sol = Sol
        self.grav = grav
        self.frot = frot
        self.frot_s = frot_s

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    def ajouter_masse(self, masse):
        self.Masse.append(masse)
    
    def update(self, masse):
        masse.rota()

        if masse.y == self.Sol.altitude - self.Sol.hauteur//2 - masse.rayon + 1 and masse.x >= self.width // 2 - self.Sol.largeur // 2 + 30:
            masse.acc_x = (-self.frot * masse.vit_x - self.frot_s * masse.vit_x) / masse.masse
            masse.vit_x += masse.acc_x
            masse.x += masse.vit_x
            masse.acc_y = (-self.frot * masse.vit_y) / masse.masse  + self.grav
            masse.vit_y += masse.acc_y
            masse.y += masse.vit_y
        else:
            masse.acc_x = -self.frot * masse.vit_x / masse.masse
            masse.vit_x += masse.acc_x
            masse.x += masse.vit_x
            if masse.spin:
                masse.acc_y = -self.frot * masse.vit_y / masse.masse + self.grav - 1
            else: 
                masse.acc_y = -self.frot * masse.vit_y / masse.masse + self.grav
            masse.vit_y += masse.acc_y
            masse.y += masse.vit_y 

        if (masse.y + masse.rayon) >= self.Sol.altitude - self.Sol.hauteur//2 and not masse.x >= 50:
            masse.vit_y *= -1
            masse.y = self.Sol.altitude - self.Sol.hauteur//2 - masse.rayon + 1
        
        if (masse.y + masse.rayon) >= self.Sol.altitude - self.Sol.hauteur//2 and masse.x >= 50:
            masse.vit_y *= -self.Sol.absor
            masse.y = self.Sol.altitude - self.Sol.hauteur//2 - masse.rayon + 1

        
        return int(masse.x), int(masse.y), int(masse.vit_x), int(masse.vit_y)


    def run(self):
        global angle
        self.init_pygame()
        termine = []
        en_cours = [self.Masse[0]]
        i = 0
        bool = True
        D = {}
        D_y = []


        try:
            while True:

                self.handle_events()
                self.screen.fill((255, 255, 255))

                pygame.draw.line(self.screen, (0, 0, 0), (self.width // 2 - self.Sol.largeur // 2, self.Sol.altitude), (self.width // 2 + self.Sol.largeur // 2, self.Sol.altitude), self.Sol.hauteur)
                
                for masse in en_cours:
                    x, y, vx, vy = self.update(masse)
                    D_y.append(y)
                    pygame.draw.circle(self.screen, masse.couleur, (x, y), masse.rayon)
                    if vx == 0 and vy == 0:
                        termine.append(self.Masse[i])
                        en_cours = []
                        i += 1
                        if i < len(self.Masse):
                            en_cours.append(self.Masse[i])

                
                for masse in termine:
                    x, y, vx, vy = self.update(masse)
                    pygame.draw.circle(self.screen, masse.couleur, (x, y), masse.rayon)
                    if masse.ang not in D:
                        D[angle] = x

                pygame.display.flip()
                self.clock.tick(60)
                
                if len(termine) == len(self.Masse) and bool == True:
                    m, c = max_dico(D)
                    p, q = min_dico(D)
                    print("\n")
                    print_red("angle maximal :" + str(np.degrees(c)))
                    print_blue("distance maximale :" + str(m)) 
                    print_green("hauteur maximale :"+ str(max(D_y)))
                    print("\n")
                    bool = False 
                    

        except Exception as e:
            print("Une erreur s'est produite:", str(e))
        finally:
            pygame.quit()

width, height = 1200, 600

alti = height - 50
hauteur = 10
largeur = width
absor = 0.5

masse = 10
rayon = 10
pos = (width // 2 - largeur // 2, alti - hauteur//2 - rayon + 1)
vit = 20
acc = 0

grav = 1
frot = 0.1
frot_s = 1

ran = 50

angle = np.pi/4
couleur = (rd.randint(0, 255), rd.randint(0, 255), rd.randint(0, 255))

sol = Sol(alti, hauteur, largeur, 1 - absor)

simu = main(width, height, sol, grav, frot, frot_s)
simu.ajouter_masse(Masse(masse, rayon, pos, vit, acc, angle, couleur))

simu.run()




#%%