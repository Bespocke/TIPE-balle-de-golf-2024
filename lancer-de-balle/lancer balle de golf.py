#%%

import pygame
import numpy as np
from time import time

aaa = True

class Balle:
    def __init__(self, masse=float, rayon=float, pos=tuple, vit=float, acc=float, ang=float, couleur=tuple):
        self.x, self.y = pos
        self.vit_x, self.vit_y = vit * np.cos(ang), vit * np.sin(ang)
        self.acc_x, self.acc_y = acc, acc
        self.masse = masse
        self.rayon = rayon
        self.couleur = couleur
        self.ang = ang
        self.spin = True

    def afficher(self, screen):
        pygame.draw.circle(screen, self.couleur, (int(self.x), int(self.y)), int(self.rayon))

    def mouvement(self, update):
        x, y = update(self.masse)
        return False if self.x == x and self.y == y else True

    def contact(self, Sol):
        return True if self.y == Sol.altitude - Sol.hauteur//2 - self.rayon + 1 else False

    def rotation(self):
        global aaa
        global temps_rota
        if aaa: 
            start = time()
            aaa = False
        if time() - start >= temps_rota:
            self.spin = False

class Sol:
    def __init__(self, altitude=int, hauteur=int, largeur=int, absor=float):
        self.altitude = altitude
        self.hauteur = hauteur
        self.largeur = largeur
        self.absor = 1 - absor

    def afficher(self, screen):
        pygame.draw.line(screen, (0, 0, 0), (-self.largeur // 2, self.altitude), (self.largeur, self.altitude), self.hauteur)

class main:
    def __init__(self, width=int, height=int, sol=object, grav=float, frot=float, frot_s=float, absor=float):
        self.width, self.height = width, height
        self.Balles = []  # Changed the name to avoid confusion with the class name "Balle"
        self.sol = sol
        self.grav = grav
        self.frot = frot
        self.frot_s = frot_s
        self.absor = absor

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    def ajouter_balle(self, balle=object):
        self.Balles.append(balle)  # Changed the name to match the instance variable

    def update(self, balle):
        depart = True if balle.x <= 100 else False
        contact = balle.contact(self.sol)  # Changed "self.masse.contact" to "balle.contact"
        if depart and contact:
            balle.acc_x = (-self.frot * balle.vit_x - self.frot_s * balle.vit_x) / balle.masse
            balle.vit_x += balle.acc_x
            balle.x += balle.vit_x
            balle.acc_y = (-self.frot * balle.vit_y - self.frot_s * balle.vit_y) / balle.masse + self.grav
            balle.vit_y += balle.acc_y
            balle.y += balle.vit_y
        elif depart and not contact:
            balle.acc_x = (-self.frot * balle.vit_x) / balle.masse
            balle.vit_x += balle.acc_x
            balle.x += balle.vit_x
            balle.acc_y = (-self.frot * balle.vit_y) / balle.masse + self.grav
            balle.vit_y += balle.acc_y
            balle.y += balle.vit_y
        elif not depart and contact:
            balle.acc_x = (-self.frot * balle.vit_x - self.frot_s * balle.vit_x) / balle.masse
            balle.vit_x += balle.acc_x
            balle.x += balle.vit_x
            balle.acc_y = (-self.frot * balle.vit_y - self.frot_s * balle.vit_y) / balle.masse + self.grav
            balle.vit_y += balle.acc_y
            balle.y += balle.vit_y
        elif not depart and not contact:
            balle.acc_x = (-self.frot * balle.vit_x) / balle.masse
            balle.vit_x += balle.acc_x
            balle.x += balle.vit_x
            balle.acc_y = (-self.frot * balle.vit_y) / balle.masse  + self.grav
            balle.vit_y += balle.acc_y
            balle.y += balle.vit_y

        if (balle.y + balle.rayon) >= self.sol.altitude - self.sol.hauteur//2 and balle.x >= 500:  # Corrected "self.Sol" to "self.sol"
            balle.y = self.sol.altitude - self.sol.hauteur//2 - balle.rayon + 1 
            balle.vit_y *= -self.absor

    def run(self):
        self.init_pygame()

        try:
            while True:
                self.handle_events()
                self.screen.fill((255, 255, 255))

                self.sol.afficher(self.screen)
                self.update(self.Balles[0])  # Changed to access the first ball in the list
                self.Balles[0].afficher(self.screen)  # Changed to access the first ball in the list

                pygame.display.flip()
                self.clock.tick(60)

        except Exception as e:
            print("Une erreur s'est produite:", str(e))
        finally:
            pygame.quit()

#écran
width, height = 1400, 600

#sol
alti = height - 100
hauteur = 10
largeur = width
absor = 1

#balle
masse = 10
rayon = 10
pos = (width // 2 - largeur // 2, alti - hauteur//2 - rayon - 1)
vit = 50
acc = 0

#environnement
grav = 0.5
frot = 0
frot_s = 0.8

angle= np.pi / 4

sol = Sol(alti, hauteur, largeur, absor)
simu = main(width, height, sol, grav, frot, frot_s, absor)
simu.ajouter_balle(Balle(masse, rayon, pos, vit, acc, angle, (0, 0, 0)))

simu.run() 





#%%