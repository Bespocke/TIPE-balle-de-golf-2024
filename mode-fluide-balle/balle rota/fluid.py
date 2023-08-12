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

        # Ajouter une balle solide au centre du domaine
        self.ball_radius = 40
        ball_center = np.floor_divide(shape, 2)
        self.ball_mask = np.linalg.norm(self.indices - ball_center[:, None, None], axis=0) <= self.ball_radius
        self.ball_rotation_speed = 1  # Vitesse angulaire de rotation de la balle

    def step(self, dt=1):
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

        # Compute the jacobian at each point in the
        # velocity field to extract curl and divergence.
        jacobian_shape = (self.dimensions,) * 2
        partials = tuple(np.gradient(d) for d in self.velocity)
        jacobian = np.stack(partials).reshape(*jacobian_shape, *self.shape)

        divergence = jacobian.trace()

        # If this curl calculation is extended to 3D, the y-axis value must be negated.
        # This corresponds to the coefficients of the levi-civita symbol in that dimension.
        # Higher dimensions do not have a vector -> scalar, or vector -> vector,
        # correspondence between velocity and curl due to differing isomorphisms
        # between exterior powers in dimensions != 2 or 3 respectively.
        curl_mask = np.triu(np.ones(jacobian_shape, dtype=bool), k=1)
        curl = (jacobian[curl_mask] - jacobian[curl_mask.T]).squeeze()

        # Apply the pressure correction to the fluid's velocity field.
        pressure = self.pressure_solver(divergence.flatten()).reshape(self.shape)
        self.velocity -= np.gradient(pressure)

        # Mettre à jour la position de la balle en fonction de la vitesse angulaire
        ball_center = np.array([self.shape[0] / 2, self.shape[1] / 2])
        ball_center += self.ball_rotation_speed * np.array([np.cos(dt * self.ball_rotation_speed),
                                                            np.sin(dt * self.ball_rotation_speed)])

        # Mettre à jour le masque de la balle avec la nouvelle position
        self.ball_mask = np.linalg.norm(self.indices - ball_center[:, None, None], axis=0) <= self.ball_radius

        # Interagir avec le fluide en définissant la vitesse autour de la balle
        solid_velocity = np.zeros_like(self.velocity)
        ball_indices = np.nonzero(self.ball_mask)
        solid_velocity[:, ball_indices[0], ball_indices[1]] = self.ball_rotation_speed * np.array([-ball_indices[1] + ball_center[1], ball_indices[0] - ball_center[0]])
        self.velocity += solid_velocity

        return divergence, curl, pressure
