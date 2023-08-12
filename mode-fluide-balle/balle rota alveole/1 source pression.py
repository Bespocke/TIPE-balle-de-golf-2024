import numpy as np
from PIL import Image
from scipy.special import erf

from fluid import Fluid

RESOLUTION = 500, 500
DURATION = 100

INFLOW_PADDING = 50
INFLOW_DURATION = 100
INFLOW_RADIUS = 100
INFLOW_VELOCITY = 2
INFLOW_COUNT = 1

print('Generating fluid solver, this may take some time.')
fluid = Fluid(RESOLUTION, 'dye', pressure_order=2, advect_order=2)

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

    # Mettre à jour la position de la balle pour la faire tourner dans le sens anti-horaire
    dt = 2 * np.pi / DURATION
    fluid.step(dt)

    # Calculate pressure
    _, _, pressure = fluid.step()

    # Normalize pressure values to range [0, 1] for visualization
    pressure = (pressure - np.min(pressure)) / (np.max(pressure) - np.min(pressure))
    pressure = np.clip(pressure, 0, 1)

    # Convert pressure values to colors (example: blue to red colormap)
    pressure_color = np.zeros((*fluid.shape, 3), dtype='uint8')
    pressure_color[:, :, 0] = (pressure * 255).astype('uint8')  # Red channel
    pressure_color[:, :, 2] = ((1 - pressure) * 255).astype('uint8')  # Blue channel

    # Combine pressure with other visualizations (curl and dye)
    curl = fluid.step()[1]
    curl = (erf(curl * 2) + 1) / 4
    color = np.dstack((curl, np.ones(fluid.shape), fluid.dye))
    color = (np.clip(color, 0, 1) * 255).astype('uint8')

    # Apply pressure visualization on top of other visualizations
    color[:, :, :3] = pressure_color

    # Remplacer la couleur de la balle par du rouge
    ball_color = np.array([255, 0, 0], dtype='uint8')
    color[fluid.ball_mask] = ball_color

    frames.append(Image.fromarray(color, mode='HSV').convert('RGB'))

print('Saving simulation result.')
frames[0].save('example2.gif', save_all=True, append_images=frames[1:], duration=20, loop=0)
