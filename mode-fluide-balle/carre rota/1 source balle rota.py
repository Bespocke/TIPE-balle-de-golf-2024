
import numpy as np
from PIL import Image
from scipy.special import erf

from fluid import Fluid

RESOLUTION = 500, 500
DURATION = 100

INFLOW_PADDING = 50
INFLOW_DURATION = 100
INFLOW_RADIUS = 24  # Modifier le rayon du cercle ici (augmenter à 24 par exemple)
INFLOW_VELOCITY = 10
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

    curl, _ = fluid.step()

    # Using the error function to make the contrast a bit higher.
    # Any other sigmoid function e.g. smoothstep would work.
    curl = (erf(curl * 2) + 1) / 4

    color = np.dstack((curl, np.ones(fluid.shape), fluid.dye))
    color = (np.clip(color, 0, 1) * 255).astype('uint8')

    # Update the position and rotation of the square for each frame
    fluid.square_rotation_center = np.array([RESOLUTION[0] / 2, RESOLUTION[1] / 2])
    fluid.square_rotation_speed = 1 * (f + 1)  # Adjust the rotation speed as needed

    # Set the square pixels to red color
    red_color = np.array([255, 0, 0], dtype='uint8')
    color[fluid.square_mask] = red_color

    frames.append(Image.fromarray(color, mode='HSV').convert('RGB'))

print('Saving simulation result.')
frames[0].save('example2.gif', save_all=True, append_images=frames[1:], duration=20, loop=0)
