from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from beam_3d_models import Mesh, mesh_triangles, write_ascii_stl, write_obj


OUTPUT_DIR = Path("best-designs-20/3d-models-print-oriented")

SUPPORT_A_X_IN = 0.5
SUPPORT_B_X_IN = 8.5

# Project instructions require supports 8 in apart and at least 0.5 in wide.
# These are compact tapered blocks, not a beam-length base fixture.
BLOCK_BASE_X_IN = 0.80
BLOCK_BASE_Z_IN = 0.80
BLOCK_TOP_X_IN = 0.56
BLOCK_TOP_Z_IN = 0.62
BLOCK_HEIGHT_IN = 0.50


def add_tapered_support_block(
    mesh: Mesh,
    center_x: float,
    center_z: float,
    base_x: float = BLOCK_BASE_X_IN,
    base_z: float = BLOCK_BASE_Z_IN,
    top_x: float = BLOCK_TOP_X_IN,
    top_z: float = BLOCK_TOP_Z_IN,
    height: float = BLOCK_HEIGHT_IN,
) -> None:
    base = len(mesh.vertices)
    bx = base_x / 2.0
    bz = base_z / 2.0
    tx = top_x / 2.0
    tz = top_z / 2.0
    mesh.vertices.extend(
        [
            (center_x - bx, center_z - bz, 0.0),
            (center_x + bx, center_z - bz, 0.0),
            (center_x + bx, center_z + bz, 0.0),
            (center_x - bx, center_z + bz, 0.0),
            (center_x - tx, center_z - tz, height),
            (center_x + tx, center_z - tz, height),
            (center_x + tx, center_z + tz, height),
            (center_x - tx, center_z + tz, height),
        ]
    )
    faces = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (1, 2, 6),
        (1, 6, 5),
        (2, 3, 7),
        (2, 7, 6),
        (3, 0, 4),
        (3, 4, 7),
    ]
    mesh.faces.extend((base + a, base + b, base + c) for a, b, c in faces)


def build_pair_fixture() -> Mesh:
    mesh = Mesh(vertices=[], faces=[])
    for support_x in (SUPPORT_A_X_IN, SUPPORT_B_X_IN):
        add_tapered_support_block(mesh, center_x=support_x, center_z=0.0)
    return mesh


def build_single_fixture() -> Mesh:
    mesh = Mesh(vertices=[], faces=[])
    add_tapered_support_block(mesh, center_x=0.0, center_z=0.0)
    return mesh


def plot_preview(mesh: Mesh, output_path: Path, title: str) -> None:
    triangles = mesh_triangles(mesh)
    figure = plt.figure(figsize=(9, 4.5))
    axis = figure.add_subplot(111, projection="3d")
    collection = Poly3DCollection(triangles, alpha=0.92, facecolor="#d8d2c4", edgecolor="#424242", linewidths=0.08)
    axis.add_collection3d(collection)

    vertices = np.asarray(mesh.vertices, dtype=float)
    axis.set_xlim(float(np.min(vertices[:, 0])), float(np.max(vertices[:, 0])))
    axis.set_ylim(float(np.min(vertices[:, 1])), float(np.max(vertices[:, 1])))
    axis.set_zlim(float(np.min(vertices[:, 2])), float(np.max(vertices[:, 2])))
    axis.set_box_aspect(
        (
            max(float(np.ptp(vertices[:, 0])), 1.0e-6),
            max(float(np.ptp(vertices[:, 1])), 1.0e-6),
            max(float(np.ptp(vertices[:, 2])), 1.0e-6),
        )
    )
    axis.set_title(title)
    axis.set_xlabel("x [in]")
    axis.set_ylabel("z [in]")
    axis.set_zlabel("y [in]")
    axis.view_init(elev=20, azim=-62)
    figure.tight_layout()
    figure.savefig(output_path, dpi=220)
    plt.close(figure)


def write_fixture(mesh: Mesh, safe_name: str, title: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_ascii_stl(mesh, OUTPUT_DIR / f"{safe_name}.stl", solid_name=safe_name)
    write_obj(mesh, OUTPUT_DIR / f"{safe_name}.obj")
    plot_preview(mesh, OUTPUT_DIR / f"{safe_name}_preview.png", title=title)


def main() -> None:
    write_fixture(
        build_pair_fixture(),
        "support_block_pair_8in_span_tapered_flat_top",
        "Tapered support blocks, 8 in span",
    )
    write_fixture(
        build_single_fixture(),
        "support_block_single_tapered_flat_top",
        "Single tapered support block",
    )


if __name__ == "__main__":
    main()
