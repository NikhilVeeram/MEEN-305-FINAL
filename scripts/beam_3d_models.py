from __future__ import annotations

import argparse
import json
import shutil
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


@dataclass
class DiscoveredDesign:
    name: str
    geometry: TaperedRectangularTube
    source_json_path: Path | None


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


def write_sketch_dxf(geometry: TaperedRectangularTube, output_path: Path, samples: int = 81) -> None:
    x_in = build_x_grid(geometry.span_in, stations=samples)
    front = geometry.height_profile(x_in)
    top = geometry.width_profile(x_in)
    clear_height = geometry.inner_height_profile(x_in)
    clear_width = geometry.inner_width_profile(x_in)
    opening_ratio = geometry.web_opening_ratio_profile(x_in)
    mid_index = len(x_in) // 2

    vertical_gap = 1.5 * max(float(np.max(front)), float(np.max(top))) + 0.75
    cross_section_x_shift = float(np.max(x_in)) + 1.5
    cross_section_y_shift = 0.0

    def segment_entity(x1: float, y1: float, x2: float, y2: float, layer: str) -> str:
        return (
            "0\nLINE\n8\n"
            f"{layer}\n10\n{x1:.6f}\n20\n{y1:.6f}\n30\n0.0\n11\n{x2:.6f}\n21\n{y2:.6f}\n31\n0.0\n"
        )

    entities: list[str] = []

    top_front = [(float(x), float(h / 2.0)) for x, h in zip(x_in, front, strict=True)]
    bottom_front = [(float(x), float(-h / 2.0)) for x, h in zip(x_in, front, strict=True)]
    for start, end in zip(top_front[:-1], top_front[1:], strict=True):
        entities.append(segment_entity(start[0], start[1], end[0], end[1], "FRONT"))
    for start, end in zip(bottom_front[:-1], bottom_front[1:], strict=True):
        entities.append(segment_entity(start[0], start[1], end[0], end[1], "FRONT"))
    entities.append(segment_entity(top_front[0][0], top_front[0][1], bottom_front[0][0], bottom_front[0][1], "FRONT"))
    entities.append(segment_entity(top_front[-1][0], top_front[-1][1], bottom_front[-1][0], bottom_front[-1][1], "FRONT"))

    top_top = [(float(x), float(vertical_gap + w / 2.0)) for x, w in zip(x_in, top, strict=True)]
    bottom_top = [(float(x), float(vertical_gap - w / 2.0)) for x, w in zip(x_in, top, strict=True)]
    for start, end in zip(top_top[:-1], top_top[1:], strict=True):
        entities.append(segment_entity(start[0], start[1], end[0], end[1], "TOP"))
    for start, end in zip(bottom_top[:-1], bottom_top[1:], strict=True):
        entities.append(segment_entity(start[0], start[1], end[0], end[1], "TOP"))
    entities.append(segment_entity(top_top[0][0], top_top[0][1], bottom_top[0][0], bottom_top[0][1], "TOP"))
    entities.append(segment_entity(top_top[-1][0], top_top[-1][1], bottom_top[-1][0], bottom_top[-1][1], "TOP"))

    half_width = float(top[mid_index] / 2.0)
    half_height = float(front[mid_index] / 2.0)
    inner_half_width = float(clear_width[mid_index] / 2.0)
    inner_half_height = float(clear_height[mid_index] / 2.0)
    opening_half_height = float(0.5 * opening_ratio[mid_index] * clear_height[mid_index])
    thickness = float(geometry.wall_thickness_in)

    outer_rect = [
        (cross_section_x_shift - half_width, cross_section_y_shift - half_height),
        (cross_section_x_shift + half_width, cross_section_y_shift - half_height),
        (cross_section_x_shift + half_width, cross_section_y_shift + half_height),
        (cross_section_x_shift - half_width, cross_section_y_shift + half_height),
        (cross_section_x_shift - half_width, cross_section_y_shift - half_height),
    ]
    for start, end in zip(outer_rect[:-1], outer_rect[1:], strict=True):
        entities.append(segment_entity(start[0], start[1], end[0], end[1], "SECTION"))

    inner_rect = [
        (cross_section_x_shift - inner_half_width, cross_section_y_shift - inner_half_height),
        (cross_section_x_shift + inner_half_width, cross_section_y_shift - inner_half_height),
        (cross_section_x_shift + inner_half_width, cross_section_y_shift + inner_half_height),
        (cross_section_x_shift - inner_half_width, cross_section_y_shift + inner_half_height),
        (cross_section_x_shift - inner_half_width, cross_section_y_shift - inner_half_height),
    ]
    for start, end in zip(inner_rect[:-1], inner_rect[1:], strict=True):
        entities.append(segment_entity(start[0], start[1], end[0], end[1], "SECTION"))

    left_web_x0 = cross_section_x_shift - inner_half_width
    left_web_x1 = left_web_x0 + thickness
    right_web_x1 = cross_section_x_shift + inner_half_width
    right_web_x0 = right_web_x1 - thickness
    top_ligament_y0 = cross_section_y_shift + opening_half_height
    top_ligament_y1 = cross_section_y_shift + inner_half_height
    bottom_ligament_y0 = cross_section_y_shift - inner_half_height
    bottom_ligament_y1 = cross_section_y_shift - opening_half_height

    ligament_rectangles = [
        [
            (left_web_x0, top_ligament_y0),
            (left_web_x1, top_ligament_y0),
            (left_web_x1, top_ligament_y1),
            (left_web_x0, top_ligament_y1),
            (left_web_x0, top_ligament_y0),
        ],
        [
            (left_web_x0, bottom_ligament_y0),
            (left_web_x1, bottom_ligament_y0),
            (left_web_x1, bottom_ligament_y1),
            (left_web_x0, bottom_ligament_y1),
            (left_web_x0, bottom_ligament_y0),
        ],
        [
            (right_web_x0, top_ligament_y0),
            (right_web_x1, top_ligament_y0),
            (right_web_x1, top_ligament_y1),
            (right_web_x0, top_ligament_y1),
            (right_web_x0, top_ligament_y0),
        ],
        [
            (right_web_x0, bottom_ligament_y0),
            (right_web_x1, bottom_ligament_y0),
            (right_web_x1, bottom_ligament_y1),
            (right_web_x0, bottom_ligament_y1),
            (right_web_x0, bottom_ligament_y0),
        ],
    ]
    for rectangle in ligament_rectangles:
        for start, end in zip(rectangle[:-1], rectangle[1:], strict=True):
            entities.append(segment_entity(start[0], start[1], end[0], end[1], "SECTION"))

    content = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "9",
        "$INSUNITS",
        "70",
        "1",
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
        *"".join(entities).splitlines(),
        "0",
        "ENDSEC",
        "0",
        "EOF",
    ]
    output_path.write_text("\n".join(content) + "\n", encoding="utf-8")


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


def discover_designs(search_roots: list[Path], include_sample_geometry: bool) -> list[DiscoveredDesign]:
    designs: list[DiscoveredDesign] = []
    if include_sample_geometry:
        designs.append(
            DiscoveredDesign(name="sample_geometry", geometry=default_geometry(), source_json_path=None)
        )

    for root in search_roots:
        if root.is_file() and root.name == "best_design.json":
            designs.append(
                DiscoveredDesign(
                    name=root.parent.name,
                    geometry=load_geometry_from_json(root),
                    source_json_path=root,
                )
            )
            continue

        if not root.exists():
            continue

        for json_path in sorted(root.rglob("best_design.json")):
            design_name = json_path.parent.name
            if json_path.parent.parent.name:
                design_name = json_path.parent.parent.name
            designs.append(
                DiscoveredDesign(
                    name=design_name,
                    geometry=load_geometry_from_json(json_path),
                    source_json_path=json_path,
                )
            )

    deduplicated: dict[str, DiscoveredDesign] = {}
    for design in designs:
        deduplicated[design.name] = design
    return list(deduplicated.values())


def write_manifest(
    output_dir: Path,
    generated_paths: list[tuple[str, Path, Path, Path, Path | None]],
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

    for design_name, stl_path, obj_path, png_path, dxf_path in generated_paths:
        lines.extend(
            [
                f"### {design_name}",
                "",
                f"- STL: [{stl_path.name}]({stl_path.name})",
                f"- OBJ: [{obj_path.name}]({obj_path.name})",
                f"- Preview: [{png_path.name}]({png_path.name})",
                *([f"- DXF sketch: [{dxf_path.name}]({dxf_path.name})"] if dxf_path is not None else []),
                "",
            ]
        )

    lines.extend(
        [
            "## How to view them",
            "",
            "- Double-click an `.obj` or `.stl` file in a local 3D viewer if you have one installed.",
            "- Use the `.png` previews for quick comparison inside the repo.",
            "- Re-run `python scripts/beam_3d_models.py` after optimization updates to refresh the models.",
        ]
    )
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_if_exists(source_path: Path, destination_path: Path) -> None:
    if source_path.exists():
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)


def package_design_assets(
    package_dir: Path,
    design: DiscoveredDesign,
    stl_path: Path,
    obj_path: Path,
    preview_path: Path,
    dxf_path: Path | None,
) -> None:
    safe_name = design.name.replace(" ", "_").lower()
    design_dir = package_dir / safe_name
    design_dir.mkdir(parents=True, exist_ok=True)

    copy_if_exists(stl_path, design_dir / stl_path.name)
    copy_if_exists(obj_path, design_dir / obj_path.name)
    copy_if_exists(preview_path, design_dir / preview_path.name)
    if dxf_path is not None:
        copy_if_exists(dxf_path, design_dir / dxf_path.name)

    if design.source_json_path is not None:
        source_root = design.source_json_path.parent
        for filename in ("best_design.json", "optimization_report.md", "optimization_report.tex", "beam_parameter_map.png", "design_study.csv"):
            copy_if_exists(source_root / filename, design_dir / filename)
        best_design_dir = source_root / "best_design"
        if best_design_dir.exists():
            for png_path in sorted(best_design_dir.glob("*.png")):
                copy_if_exists(png_path, design_dir / "best_design" / png_path.name)

    readme_lines = [
        f"# {design.name}",
        "",
        "- Included files:",
        f"  - `{stl_path.name}`",
        f"  - `{obj_path.name}`",
        f"  - `{preview_path.name}`",
    ]
    if dxf_path is not None:
        readme_lines.append(f"  - `{dxf_path.name}`")
    if design.source_json_path is not None:
        readme_lines.extend(
            [
                "  - `best_design.json`",
                "  - `optimization_report.md`",
                "  - `optimization_report.tex`",
                "  - `beam_parameter_map.png`",
                "  - `best_design/*.png`",
            ]
        )
    readme_lines.extend(
        [
            "",
            "The PNG preview is the 3D look. The DXF file is a lightweight 2D sketch export.",
        ]
    )
    (design_dir / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 3D beam models and preview renders from optimized beam designs."
    )
    parser.add_argument(
        "--search-root",
        action="append",
        default=[],
        help="Folder or best_design.json path to scan. Can be provided multiple times.",
    )
    parser.add_argument("--output-dir", default="designs/model_exports/generated_mesh_exports")
    parser.add_argument("--package-dir", default=None, help="Optional folder for per-design packaged assets.")
    parser.add_argument("--write-dxf", action="store_true", help="Also export a simple DXF sketch for each design.")
    parser.add_argument("--include-sample-geometry", action="store_true")
    parser.add_argument("--stations", type=int, default=121)
    args = parser.parse_args()

    search_roots = [Path(path) for path in args.search_root] if args.search_root else [
        Path("designs/active_runs/continuous_uniform_load_case_1"),
        Path("designs/active_runs/continuous_uniform_load_case_2"),
        Path("designs/active_runs/continuous_uniform_both_load_cases"),
    ]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    package_dir = Path(args.package_dir) if args.package_dir is not None else None
    if package_dir is not None:
        package_dir.mkdir(parents=True, exist_ok=True)

    generated_paths: list[tuple[str, Path, Path, Path, Path | None]] = []

    for design in discover_designs(search_roots, include_sample_geometry=args.include_sample_geometry):
        design_name = design.name
        geometry = design.geometry
        safe_name = design_name.replace(" ", "_").lower()
        mesh = build_beam_mesh(geometry, stations=args.stations)

        stl_path = output_dir / f"{safe_name}.stl"
        obj_path = output_dir / f"{safe_name}.obj"
        png_path = output_dir / f"{safe_name}_preview.png"
        dxf_path = output_dir / f"{safe_name}.dxf" if args.write_dxf else None

        write_ascii_stl(mesh, stl_path, solid_name=safe_name)
        write_obj(mesh, obj_path)
        plot_mesh_preview(mesh, png_path, title=design_name)
        if dxf_path is not None:
            write_sketch_dxf(geometry, dxf_path)
        if package_dir is not None:
            package_design_assets(
                package_dir=package_dir,
                design=design,
                stl_path=stl_path,
                obj_path=obj_path,
                preview_path=png_path,
                dxf_path=dxf_path,
            )
        generated_paths.append((design_name, stl_path, obj_path, png_path, dxf_path))
        print(f"Generated 3D model for {design_name}:")
        print(f"  STL: {stl_path.resolve()}")
        print(f"  OBJ: {obj_path.resolve()}")
        print(f"  Preview: {png_path.resolve()}")
        if dxf_path is not None:
            print(f"  DXF: {dxf_path.resolve()}")

    write_manifest(output_dir, generated_paths)
    print(f"\n3D models written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
