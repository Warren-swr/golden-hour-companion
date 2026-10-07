"""Finite-depth gravity-capillary basin modes, baked to a portable MDD cache.

Cosine eigenfunctions enforce zero normal flow at all four pool walls. Each
mode obeys the linear free-surface dispersion relation, not an arbitrary
texture scroll. Small wave steepness keeps this potential-flow model valid.
The narrow spillway has a separate gravity-driven ballistic sheet.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent
FPS = 24
FRAMES = 1056
NX, NY = 241, 157
X0, X1 = -2.30, 5.30
Y0, Y1 = -15.40, -10.50
LEVEL, BOTTOM = -.255, -1.52


def topology():
    x = np.linspace(X0, X1, NX)
    y = np.linspace(Y0, Y1, NY)
    xx, yy = np.meshgrid(x, y)
    top = np.column_stack((xx.ravel(), yy.ravel(), np.full(NX * NY, LEVEL)))
    perimeter = (list(range(NX)) + [j * NX + NX - 1 for j in range(1, NY)] +
                 list(range(NX * NY - 2, (NY - 1) * NX - 1, -1)) +
                 [j * NX for j in range(NY - 2, 0, -1)])
    lower = top[perimeter].copy()
    lower[:, 2] = BOTTOM
    vertices = np.concatenate((top, lower))
    faces = []
    for j in range(NY - 1):
        for i in range(NX - 1):
            a = j * NX + i
            faces.append((a, a + 1, a + 1 + NX, a + NX))
    base = NX * NY
    for i, a in enumerate(perimeter):
        k = (i + 1) % len(perimeter)
        faces.append((a, base + i, base + k, perimeter[k]))
    faces.append(tuple(reversed(range(base, len(vertices)))))
    return vertices, faces


def basin_solver():
    rng = np.random.default_rng(260926)
    mx, my = np.arange(44), np.arange(32)
    kx, ky = mx * np.pi / (X1 - X0), my * np.pi / (Y1 - Y0)
    kk = np.hypot(kx[:, None], ky[None, :])
    omega = np.sqrt((9.81 * kk + .072 / 998.2 * kk ** 3) * np.tanh(kk * (LEVEL - BOTTOM)))
    wavelength = 2 * np.pi / np.maximum(kk, 1e-6)
    envelope = np.exp(-((np.log(np.maximum(wavelength, 1e-4)) - np.log(.95)) / .68) ** 2)
    envelope *= .3 + .7 * kx[:, None] ** 2 / np.maximum(kk ** 2, 1e-6)
    amplitude = rng.normal(size=kk.shape) * envelope
    amplitude[0, 0] = 0
    amplitude *= .010 / np.sqrt(np.sum(amplitude ** 2))
    phase = rng.uniform(0, 2 * np.pi, kk.shape)
    cx = np.cos(np.outer(np.linspace(0, X1 - X0, NX), kx)).astype(np.float32)
    cy = np.cos(np.outer(np.linspace(0, Y1 - Y0, NY), ky)).astype(np.float32)
    # A confined inlet excites a second, damped set of basin modes.
    inlet = np.cos(kx[:, None] * (4.98 - X0)) * np.cos(ky[None, :] * (-12.8 - Y0))
    inlet *= np.exp(-.04 * kk ** 2)
    inlet[0, 0] = 0
    inlet *= .0020 / max(np.sqrt(np.sum(inlet ** 2)), 1e-8)

    def surface(time):
        q = amplitude * np.cos(omega * time + phase)
        q += inlet * (np.cos(omega * time + phase * .7) + .2 * np.sin(3.2 * time))
        return cy @ q.astype(np.float32).T @ cx.T

    return surface, float(np.max(omega))


def bake():
    OUT.joinpath('cache').mkdir(exist_ok=True)
    vertices, faces = topology()
    surface, max_omega = basin_solver()
    cache = OUT / 'cache' / 'pool_gravity_capillary.mdd'
    stats = []
    with cache.open('wb') as handle:
        handle.write(struct.pack('>2i', FRAMES, len(vertices)))
        handle.write(np.arange(FRAMES, dtype='>f4').__mul__(1 / FPS).astype('>f4').tobytes())
        for frame in range(FRAMES):
            height = surface(frame / FPS + 12)
            vertices[:NX * NY, 2] = LEVEL + height.ravel()
            handle.write(vertices.astype('>f4').tobytes())
            if frame % 120 == 0:
                stats.append(dict(frame=frame + 1, min_m=float(height.min()),
                                  max_m=float(height.max()), rms_m=float(np.sqrt(np.mean(height ** 2)))))
                print('WATER_FRAME', frame + 1, flush=True)
    report = dict(model='linear finite-depth gravity-capillary potential flow',
                  boundary='Neumann cosine eigenmodes: reflection at all four walls',
                  gravity_m_s2=9.81, density_kg_m3=998.2, surface_tension_n_m=.072,
                  grid=[NX, NY], modes=[44, 32], fps=FPS, frames=FRAMES,
                  pool_bounds=[X0, X1, Y0, Y1], water_level_m=LEVEL,
                  depth_m=LEVEL - BOTTOM, max_angular_frequency=max_omega,
                  cache=str(cache.relative_to(OUT)), bytes=cache.stat().st_size,
                  sha256=hashlib.file_digest(cache.open('rb'), 'sha256').hexdigest(),
                  samples=stats,
                  limitations='Small-amplitude free-surface model; not a breaking-wave or volumetric Navier-Stokes solver. Spillway sheet follows gravity separately.')
    (OUT / 'review' / 'water_simulation.json').write_text(json.dumps(report, indent=2))
    print('WATER_CACHE_COMPLETE', cache.stat().st_size, flush=True)


if __name__ == '__main__':
    bake()
