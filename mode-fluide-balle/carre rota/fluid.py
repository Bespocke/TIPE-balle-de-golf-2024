import numpy as np
from scipy.ndimage import map_coordinates, spline_filter
from scipy.sparse.linalg import factorized

from numerical import difference, operator


class Fluid:
    def __init__(self, shape, *quantities, pressure_order=1, advect_order=3):
        self.shape = shape
        self.dimensions = len(shape)

        # Prototyping is simplified by dynamically
        # creating advected quantities as needed.
        self.quantities = quantities
        for q in quantities:
            setattr(self, q, np.zeros(shape))

        self.indices = np.indices(shape)
        self.velocity = np.zeros((self.dimensions, *shape))

        laplacian = operator(shape, difference(2, pressure_order))
        self.pressure_solver = factorized(laplacian)

        self.advect_order = advect_order

        # Add a solid square at the center of the domain
        self.square_side = 80
        square_min = np.floor_divide(shape, 2) - self.square_side // 2
        square_max = square_min + self.square_side
        self.square_mask = np.zeros(shape, dtype=bool)
        self.square_mask[square_min[0]:square_max[0], square_min[1]:square_max[1]] = True

        # Add rotation parameters for the square
        self.square_rotation_center = np.mean([square_min, square_max], axis=0)
        self.square_rotation_speed = 0.01  # Adjust the rotation speed as needed

    def step(self):
        # Advection is computed backwards in time as described in Stable Fluids.
        advection_map = self.indices - self.velocity

        # SciPy's spline filter introduces checkerboard divergence.
        # A linear blend of the filtered and unfiltered fields based
        # on some value epsilon eliminates this error.
        def advect(field, filter_epsilon=10e-2, mode='constant'):
            filtered = spline_filter(field, order=self.advect_order, mode=mode)
            field = filtered * (1 - filter_epsilon) + field * filter_epsilon
            return map_coordinates(field, advection_map, prefilter=False, order=self.advect_order, mode=mode)

        # Apply advection to each axis of the
        # velocity field and each user-defined quantity.
        for d in range(self.dimensions):
            self.velocity[d] = advect(self.velocity[d])

        for q in self.quantities:
            setattr(self, q, advect(getattr(self, q)))

        # Compute the Jacobian at each point in the
        # velocity field to extract curl and divergence.
        jacobian_shape = (self.dimensions,) * 2
        partials = tuple(np.gradient(d) for d in self.velocity)
        jacobian = np.stack(partials).reshape(*jacobian_shape, *self.shape)

        divergence = jacobian.trace()

        # Interact with the rotating square by updating its velocity
        square_velocity = np.zeros_like(self.velocity)
        y, x = np.where(self.square_mask)
        positions = np.stack((y, x))
        center = self.square_rotation_center[:, None]
        rotation_matrix = np.array([[np.cos(self.square_rotation_speed), -np.sin(self.square_rotation_speed)],
                                    [np.sin(self.square_rotation_speed), np.cos(self.square_rotation_speed)]])
        rotated_positions = rotation_matrix @ (positions - center) + center
        rotated_positions = np.clip(rotated_positions, 0, np.array(self.shape)[:, None] - 1).astype(int)
        square_velocity[:, self.square_mask] = rotated_positions - positions
        self.velocity += square_velocity

        # Apply the pressure correction to the fluid's velocity field.
        pressure = self.pressure_solver(divergence.flatten()).reshape(self.shape)
        self.velocity -= np.gradient(pressure)

        return divergence, pressure
