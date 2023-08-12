import numpy as np
from PIL import Image
from scipy.special import erf

from fluid import Fluid

RESOLUTION = 500, 500
DURATION = 100

INFLOW_PADDING = 50
INFLOW_DURATION = 30
INFLOW_RADIUS = 100  # Modifier le rayon de la balle ici (augmenter à 24 par exemple)
INFLOW_VELOCITY = 5
INFLOW_COUNT = 1

print('Generating fluid solver, this may take some time.')
fluid = Fluid(RESOLUTION, 'dye')

center = np.floor_divide(RESOLUTION, 2)
r = np.min(center) - INFLOW_PADDING

points = np.linspace(-np.pi, np.pi, INFLOW_COUNT, endpoint=False)
points = tuple(np.array((np.cos(p), np.sin(p))) for p in points)
normals = tuple(-p for p in points)
points = tuple(r * p + center for p in points)

inflow_velocity = np.zeros_like(fluid.velocity)
inflow_dye = np.zeros(fluid.shape)
for p, n in zip(points, normals):
    mask = np.linalg.norm(fluid.indices - p[:, None, None], axis=0) <= INFLOW_RADIUS
    inflow_velocity[:, mask] += n[:, None] * INFLOW_VELOCITY
    inflow_dye[mask] = 1

frames = []
for f in range(DURATION):
    print(f'Computing frame {f + 1} of {DURATION}.')
    if f <= INFLOW_DURATION:
        fluid.velocity += inflow_velocity
        fluid.dye += inflow_dye

    # Interagir avec la balle solide en fixant sa position dans le champ de vélocité
    fluid.velocity[:, fluid.ball_mask] = inflow_velocity[:, fluid.ball_mask]

    curl = fluid.step()[1]
    # Using the error function to make the contrast a bit higher. 
    # Any other sigmoid function e.g. smoothstep would work.
    curl = (erf(curl * 2) + 1) / 4

    color = np.dstack((curl, np.ones(fluid.shape), fluid.dye))
    color = (np.clip(color, 0, 1) * 255).astype('uint8')
    
    # Remplacer la couleur de la balle par du blanc
    ball_color = np.array([255, 255, 255], dtype='uint8')
    color[fluid.ball_mask] = ball_color
    
    frames.append(Image.fromarray(color, mode='HSV').convert('RGB'))

    # Mise à jour de la position de la balle dans le champ de vélocité
    fluid.velocity[:, fluid.ball_mask] = inflow_velocity[:, fluid.ball_mask]

print('Saving simulation result.')
frames[0].save('example2.gif', save_all=True, append_images=frames[1:], duration=20, loop=0)
