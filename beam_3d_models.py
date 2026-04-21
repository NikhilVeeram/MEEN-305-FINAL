from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from beam_solver import TaperedRectangularTube, build_x_grid, default_geometry


@dataclass
class Mesh:
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]


def load_geometry_from_json(json_path: Path) -> TaperedRectangularTube:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    return TaperedRectangularTube(**payload["geometry"])


def rectangle_profile(z_min: float, z_max: float, y_min: float, y_max: float) -> list[tuple[float, float]]:
    return [
        (z_min, y_min),
        (z_max, y_min),
        (z_max, y_max),
        (z_min, y_max),
    ]


def component_profiles(geometry: TaperedRectangularTube, x_in: np.ndarray) -> dict[str, list[list[tuple[float, float]]]]:
    width = geometry.width_profile(x_in)
    height = geometry.height_profile(x_in)
    thickness = geometry.wall_thickness_in
    clear_height = geometry.inner_height_profile(x_in)
    opening_ratio = geometry.web_opening_ratio_profile(x_in)
    opening_height = opening_ratio * clear_height

    profiles: dict[str, list[list[tuple[float, float]]]] = {
        "top_flange": [],
        "bottom_flange": [],
        "left_top_web": [],
        "left_bottom_web": [],
        "right_top_web": [],
        "right_bottom_web": [],
    }

    for b, h, clear_h, open_h in zip(width, height, clear_height, opening_height, strict=True):
        half_width = b / 2.0
        half_height = h / 2.0
        top_ligament_bottom = open_h / 2.0
        bottom_ligament_top = -open_h / 2.0

        profiles["top_flange"].append(
            rectangle_profile(
                z_min=-half_width,
                z_max=half_width,
                y_min=half_height - thickness,
                y_max=half_height,
            )
        )
        profiles["bottom_flange"].append(
            rectangle_profile(
                z_min=-half_width,
                z_max=half_width,
                y_min=-half_height,
                y_max=-half_height + thickness,
            )
        )
        profiles["left_top_web"].append(
            rectangle_profile(
                z_min=-half_width,
                z_max=-half_width + thickness,
                y_min=top_ligament_bottom,
                y_max=half_height - thickness,
            )
        )
        profiles["left_bottom_web"].append(
            rectangle_profile(
                z_min=-half_width,
                z_max=-half_width + thickness,
                y_min=-half_height + thickness,
                y_max=bottom_ligament_top,
            )
        )
        profiles["right_top_web"].append(
            rectangle_profile(
                z_min=half_width - thickness,
                z_max=half_width,
                y_min=top_ligament_bottom,
                y_max=half_height - thickness,
            )
        )
        profiles["right_bottom_web"].append(
            rectangle_profile(
                z_min=half_width - thickness,
                z_max=half_width,
                y_min=-half_height + thickness,
                y_max=bottom_ligament_top,
            )
        )

    return profiles


def add_lofted_rectangle_mesh(
    mesh: Mesh,
    x_in: np.ndarray,
    profiles: list[list[tuple[float, float]]],
) -> None:
    if len(x_in) != len(profiles):
        raise ValueError("x stations and profiles must have the same length.")

    base_index = len(mesh.vertices)
    for x_value, profile in zip(x_in, profiles, strict=True):
        for z_value, y_value in profile:
            mesh.vertices.append((float(x_value), float(z_value), float(y_value)))

    slice_count = len(x_in)
    corners_per_slice = 4
    edge_pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]

    for slice_index in range(slice_count - 1):
        start = base_index + slice_index * corners_per_slice
        end = base_index + (slice_index + 1) * corners_per_slice
        for edge_start, edge_end in edge_pairs:
            a = start + edge_start
            b = start + edge_end
            c = end + edge_end
            d = end + edge_start
            mesh.faces.append((a, b, c))
            mesh.faces.append((a, c, d))

    first = base_index
    mesh.faces.append((first + 0, first + 2, first + 1))
    mesh.faces.append((first + 0, first + 3, first + 2))

    last = base_index + (slice_count - 1) * corners_per_slice
    mesh.faces.append((last + 0, last + 1, last + 2))
    mesh.faces.append((last + 0, last + 2, last + 3))


def build_beam_mesh(geometry: TaperedRectangularTube, stations: int) -> Mesh:
    x_in = build_x_grid(geometry.span_in, stations=stations)
    mesh = Mesh(vertices=[], faces=[])
    for profiles in component_profiles(geometry, x_in).values():
        add_lofted_rectangle_mesh(mesh, x_in, profiles)
    return mesh


def triangle_normal(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    normal = np.cross(b - a, c - a)
    magnitude = np.linalg.norm(normal)
    if magnitude <= 1.0e-12:
        return np.zeros(3)
    return normal / magnitude


def write_ascii_stl(mesh: Mesh, output_path: Path, solid_name: str) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(f"solid {solid_name}\n")
        vertices = np.asarray(mesh.vertices, dtype=float)
        for face in mesh.faces:
            a, b, c = (vertices[index] for index in face)
            normal = triangle_normal(a, b, c)
            handle.write(f"  facet normal {normal[0]:.8e} {normal[1]:.8e} {normal[2]:.8e}\n")
            handle.write("    outer loop\n")
            for point in (a, b, c):
                handle.write(f"      vertex {point[0]:.8e} {point[1]:.8e} {point[2]:.8e}\n")
            handle.write("    endloop\n")
            handle.write("  endfacet\n")
        handle.write(f"endsolid {solid_name}\n")


def write_obj(mesh: Mesh, output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for x_value, z_value, y_value in mesh.vertices:
            handle.write(f"v {x_value:.8f} {z_value:.8f} {y_value:.8f}\n")
        for face in mesh.faces:
            a, b, c = face
            handle.write(f"f {a + 1} {b + 1} {c + 1}\n")


def mesh_triangles(mesh: Mesh) -> list[np.ndarray]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    return [vertices[list(face)] for face in mesh.faces]


def plot_mesh_preview(mesh: Mesh, output_path: Path, title: str) -> None:
    triangles = mesh_triangles(mesh)
    figure = plt.figure(figsize=(9, 6.5))
    axis = figure.add_subplot(111, projection="3d")

    collection = Poly3DCollection(triangles, alpha=0.90, facecolor="#c7d7e8", edgecolor="#2f4f69", linewidths=0.08)
    axis.add_collection3d(collection)

    vertices = np.asarray(mesh.vertices, dtype=float)
    x_values = vertices[:, 0]
    z_values = vertices[:, 1]
    y_values = vertices[:, 2]
    axis.set_xlim(np.min(x_values), np.max(x_values))
    axis.set_ylim(np.min(z_values), np.max(z_values))
    axis.set_zlim(np.min(y_values), np.max(y_values))
    axis.set_box_aspect(
        (
            max(np.ptp(x_values), 1.0e-6),
            max(np.ptp(z_values), 1.0e-6),
            max(np.ptp(y_values), 1.0e-6),
        )
    )

    axis.set_title(title)
    axis.set_xlabel("x [in]")
    axis.set_ylabel("z [in]")
    axis.set_zlabel("y [in]")
    axis.view_init(elev=22, azim=-58)
    axis.grid(True, alpha=0.25)

    figure.tight_layout()
    figure.savefig(output_path, dpi=220)
    plt.close(figure)


def discover_designs(search_roots: list[Path]) -> list[tuple[str, TaperedRectangularTube]]:
    designs: list[tuple[str, TaperedRectangularTube]] = [("sample_geometry", default_geometry())]

    for root in search_roots:
        if root.is_file() and root.name == "best_design.json":
            designs.append((root.parent.name, load_geometry_from_json(root)))
            continue

        if not root.exists():
            continue

        for json_path in sorted(root.rglob("best_design.json")):
            design_name = json_path.parent.name
            if json_path.parent.parent.name:
                design_name = json_path.parent.parent.name
            designs.append((design_name, load_geometry_from_json(json_path)))

    deduplicated: dict[str, TaperedRectangularTube] = {}
    for name, geometry in designs:
        deduplicated[name] = geometry
    return list(deduplicated.items())


def write_manifest(
    output_dir: Path,
    generated_paths: list[tuple[str, Path, Path, Path]],
) -> None:
    manifest_path = output_dir / "README.md"
    lines = [
        "# 3D Beam Models",
        "",
        "This folder contains generated 3D models and preview renders for the beam designs found in the repo.",
        "",
        "## Generated designs",
        "",
    ]

    for design_name, stl_path, obj_path, png_path in generated_paths:
        lines.extend(
            [
                f"### {design_name}",
                "",
                f"- STL: [{stl_path.name}]({stl_path.name})",
                f"- OBJ: [{obj_path.name}]({obj_path.name})",
                f"- Preview: [{png_path.name}]({png_path.name})",
                "",
            ]
        )

    lines.extend(
        [
            "## How to view them",
            "",
            "- Double-click an `.obj` or `.stl` file in a local 3D viewer if you have one installed.",
            "- Use the `.png` previews for quick comparison inside the repo.",
            "- Re-run `python beam_3d_models.py` after optimization updates to refresh the models.",
        ]
    )
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 3D beam models and preview renders from optimized beam designs."
    )
    parser.add_argument(
        "--search-root",
        action="append",
        default=["optimization_outputs", "optimization_targeted", "optimization_opening_smoke"],
        help="Folder or best_design.json path to scan. Can be provided multiple times.",
    )
    parser.add_argument("--output-dir", default="models_3d")
    parser.add_argument("--stations", type=int, default=121)
    args = parser.parse_args()

    search_roots = [Path(path) for path in args.search_root]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_paths: list[tuple[str, Path, Path, Path]] = []

    for design_name, geometry in discover_designs(search_roots):
        safe_name = design_name.replace(" ", "_").lower()
        mesh = build_beam_mesh(geometry, stations=args.stations)

        stl_path = output_dir / f"{safe_name}.stl"
        obj_path = output_dir / f"{safe_name}.obj"
        png_path = output_dir / f"{safe_name}_preview.png"

        write_ascii_stl(mesh, stl_path, solid_name=safe_name)
        write_obj(mesh, obj_path)
        plot_mesh_preview(mesh, png_path, title=design_name)
        generated_paths.append((design_name, stl_path, obj_path, png_path))
        print(f"Generated 3D model for {design_name}:")
        print(f"  STL: {stl_path.resolve()}")
        print(f"  OBJ: {obj_path.resolve()}")
        print(f"  Preview: {png_path.resolve()}")

    write_manifest(output_dir, generated_paths)
    print(f"\n3D models written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
