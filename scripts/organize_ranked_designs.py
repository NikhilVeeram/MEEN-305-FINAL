from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from beam_solver import (  # noqa: E402
    LoadCase,
    TaperedRectangularTube,
    analyze_load_case,
    build_x_grid,
    default_material,
    plot_geometry,
    plot_load_case,
)
from optimize_beam import plot_parameter_map  # noqa: E402


GEOMETRY_FIELDS = [
    "left_width_in",
    "mid_width_in",
    "right_width_in",
    "left_height_in",
    "mid_height_in",
    "right_height_in",
    "wall_thickness_in",
    "left_web_opening_ratio",
    "mid_web_opening_ratio",
    "right_web_opening_ratio",
]


def slugify(value: str) -> str:
    safe = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")


def load_cases_from_payload(payload: dict[str, Any]) -> list[LoadCase]:
    cases: list[LoadCase] = []
    for item in payload["load_cases"]:
        cases.append(
            LoadCase(
                name=item["name"],
                load_lbf=float(item["load_lbf"]),
                location_in=float(item["location_in"]),
                orientation=item["orientation"],
            )
        )
    return cases


def geometry_from_row(row: dict[str, str], source_payload: dict[str, Any]) -> TaperedRectangularTube:
    source_geometry = source_payload["geometry"]
    geometry_payload: dict[str, float] = {
        "span_in": float(source_geometry["span_in"]),
        "total_length_in": float(source_geometry["total_length_in"]),
        "support_a_x_in": float(source_geometry.get("support_a_x_in", 0.5)),
        "support_b_x_in": float(source_geometry.get("support_b_x_in", 8.5)),
    }
    for field in GEOMETRY_FIELDS:
        geometry_payload[field] = float(row[field])
    return TaperedRectangularTube(**geometry_payload)


def summarize_load_case(result: Any, load_case: LoadCase) -> dict[str, Any]:
    return {
        "name": load_case.name,
        "orientation": load_case.orientation,
        "load_lbf": load_case.load_lbf,
        "location_in": load_case.location_in,
        "reaction_a_lbf": float(result.reaction_a_lbf),
        "reaction_b_lbf": float(result.reaction_b_lbf),
        "max_von_mises_psi": float(result.max_von_mises_psi),
        "max_von_mises_x_in": float(result.max_von_mises_x_in),
        "min_factor_of_safety": float(result.min_factor_of_safety),
        "min_factor_of_safety_x_in": float(result.min_factor_of_safety_x_in),
        "max_deflection_in": float(result.max_deflection_in),
        "max_deflection_x_in": float(result.max_deflection_x_in),
        "max_slope_rad": float(np.max(np.abs(result.slope_rad))),
    }


def evaluate_candidate(
    source_run: str,
    source_payload: dict[str, Any],
    row: dict[str, str],
    stations: int,
    flat_x_min: float,
    flat_x_max: float,
    min_wall_thickness_in: float,
    max_web_opening_ratio: float,
    min_web_ligament_in: float,
    min_shell_area_ratio: float,
    max_dim_slope_in_per_in: float,
    max_deflection_in: float | None,
) -> dict[str, Any] | None:
    geometry = geometry_from_row(row, source_payload)
    source_geometry = source_payload["geometry"]
    if "support_a_x_in" not in source_geometry or "support_b_x_in" not in source_geometry:
        return None
    corrected = (
        np.isclose(geometry.total_length_in, 9.0)
        and np.isclose(geometry.support_a_x_in, 0.5)
        and np.isclose(geometry.support_b_x_in, 8.5)
    )
    if not corrected:
        return None

    try:
        geometry.validate()
    except ValueError:
        return None

    x_print = build_x_grid(
        geometry.total_length_in,
        stations=stations,
        critical_positions_in=[geometry.support_a_x_in, geometry.support_b_x_in],
    )
    width = geometry.width_profile(x_print)
    height = geometry.height_profile(x_print)
    opening_ratio = geometry.web_opening_ratio_profile(x_print)
    clear_height = geometry.inner_height_profile(x_print)
    web_ligament = 0.5 * (1.0 - opening_ratio) * clear_height
    shell_area_ratio = np.divide(
        geometry.area(x_print),
        width * height,
        out=np.zeros_like(width),
        where=(width * height) > 1.0e-12,
    )
    max_dim_slope = max(
        float(np.max(np.abs(np.gradient(width, x_print)))),
        float(np.max(np.abs(np.gradient(height, x_print)))),
    )
    if geometry.wall_thickness_in < min_wall_thickness_in:
        return None
    if float(np.max(opening_ratio)) > max_web_opening_ratio:
        return None
    if float(np.min(web_ligament)) < min_web_ligament_in:
        return None
    if float(np.min(shell_area_ratio)) < min_shell_area_ratio:
        return None
    if max_dim_slope > max_dim_slope_in_per_in:
        return None

    material = default_material()
    load_cases = load_cases_from_payload(source_payload)
    x_grid = build_x_grid(
        geometry.total_length_in,
        stations=stations,
        critical_positions_in=[
            geometry.support_a_x_in,
            geometry.support_b_x_in,
            *[geometry.support_a_x_in + load_case.location_in for load_case in load_cases],
        ],
    )
    results = [
        analyze_load_case(
            geometry=geometry,
            material=material,
            load_case=load_case,
            stations=stations,
            x_grid_in=x_grid,
        )
        for load_case in load_cases
    ]
    summaries = [
        summarize_load_case(result, load_case)
        for result, load_case in zip(results, load_cases, strict=True)
    ]

    min_summary = min(summaries, key=lambda summary: summary["min_factor_of_safety"])
    min_fos = float(min_summary["min_factor_of_safety"])
    max_deflection = float(max(summary["max_deflection_in"] for summary in summaries))
    if min_fos < 1.5:
        return None
    if max_deflection_in is not None and max_deflection > max_deflection_in:
        return None

    lc2_result = next(result for result, load_case in zip(results, load_cases, strict=True) if load_case.name == "Load Case 2")
    flat_mask = (
        (lc2_result.x_in >= flat_x_min)
        & (lc2_result.x_in <= flat_x_max)
        & np.isfinite(lc2_result.factor_of_safety)
    )
    flat_fos = lc2_result.factor_of_safety[flat_mask]
    if flat_fos.size == 0:
        return None

    weight = float(results[0].weight_lbf)
    flat_std = float(np.std(flat_fos))
    flat_range = float(np.max(flat_fos) - np.min(flat_fos))
    flat_mean = float(np.mean(flat_fos))

    # Lower is better. Weight is the primary project target, so the rank score is
    # the beam weight itself. Deflection, FoS closeness, and flatness are used only
    # as deterministic tie-breakers in the global sort.
    rank_score = weight

    payload = {
        "search_config": source_payload.get("search_config", {}),
        "constraint_config": source_payload.get("constraint_config", {}),
        "durability_config": source_payload.get("durability_config", {}),
        "geometry": asdict(geometry),
        "metrics": {
            "weight_lbf": weight,
            "min_factor_of_safety": min_fos,
            "max_deflection_in": max_deflection,
            "governing_load_case": min_summary["name"],
            "governing_x_in": float(min_summary["min_factor_of_safety_x_in"]),
            "feasible": True,
            "objective": float(row.get("objective", rank_score) or rank_score),
            "penalty": 0.0,
            "uniformity_score": float(row.get("uniformity_score", 0.0) or 0.0),
            "symmetry_score": float(row.get("symmetry_score", 0.0) or 0.0),
            "smoothness_score": float(row.get("smoothness_score", 0.0) or 0.0),
            "durability_score": 0.0,
            "constraint_violations": [],
            "rank_score": rank_score,
            "fos_3to7_mean": flat_mean,
            "fos_3to7_std": flat_std,
            "fos_3to7_range": flat_range,
            "fos_3to7_min": float(np.min(flat_fos)),
            "fos_3to7_max": float(np.max(flat_fos)),
            "min_print_web_ligament_in": float(np.min(web_ligament)),
            "min_shell_area_ratio": float(np.min(shell_area_ratio)),
            "max_web_opening_ratio": float(np.max(opening_ratio)),
            "max_dim_slope_in_per_in": max_dim_slope,
        },
        "load_cases": summaries,
    }
    return {
        "source_run": source_run,
        "source_evaluation_id": int(row["evaluation_id"]),
        "rank_score": rank_score,
        "payload": payload,
    }


def discover_candidates(
    active_runs_dir: Path,
    stations: int,
    flat_x_min: float,
    flat_x_max: float,
    min_wall_thickness_in: float,
    max_web_opening_ratio: float,
    min_web_ligament_in: float,
    min_shell_area_ratio: float,
    max_dim_slope_in_per_in: float,
    max_deflection_in: float | None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for run_dir in sorted(path for path in active_runs_dir.iterdir() if path.is_dir()):
        design_study_path = run_dir / "design_study.csv"
        best_design_path = run_dir / "best_design.json"
        if not design_study_path.exists() or not best_design_path.exists():
            continue
        source_payload = json.loads(best_design_path.read_text(encoding="utf-8"))
        with design_study_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("feasible") != "True":
                    continue
                candidate = evaluate_candidate(
                    source_run=run_dir.name,
                    source_payload=source_payload,
                    row=row,
                    stations=stations,
                    flat_x_min=flat_x_min,
                    flat_x_max=flat_x_max,
                    min_wall_thickness_in=min_wall_thickness_in,
                    max_web_opening_ratio=max_web_opening_ratio,
                    min_web_ligament_in=min_web_ligament_in,
                    min_shell_area_ratio=min_shell_area_ratio,
                    max_dim_slope_in_per_in=max_dim_slope_in_per_in,
                    max_deflection_in=max_deflection_in,
                )
                if candidate is not None:
                    candidates.append(candidate)
    return candidates


def write_candidate_folder(candidate: dict[str, Any], rank: int, ranked_dir: Path, stations: int) -> dict[str, str]:
    source_run = candidate["source_run"]
    evaluation_id = candidate["source_evaluation_id"]
    payload = candidate["payload"]
    metrics = payload["metrics"]
    folder_name = (
        f"{rank:02d}_overall_rank__"
        f"{slugify(source_run)}__eval_{evaluation_id:04d}__"
        f"w_{metrics['weight_lbf']:.5f}__fos_{metrics['min_factor_of_safety']:.3f}"
    )
    design_dir = ranked_dir / folder_name
    if design_dir.exists():
        shutil.rmtree(design_dir)
    design_dir.mkdir(parents=True, exist_ok=True)

    (design_dir / "best_design.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (design_dir / "source_metadata.json").write_text(
        json.dumps(
            {
                "rank": rank,
                "source_run": source_run,
                "source_evaluation_id": evaluation_id,
                "rank_score": candidate["rank_score"],
                "ranking_formula": "weight_lbf, with tie-breakers max_deflection_in, abs(min_fos - 1.5), fos_3to7_std",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    geometry = TaperedRectangularTube(**payload["geometry"])
    load_cases = load_cases_from_payload(payload)
    material = default_material()
    best_plot_dir = design_dir / "best_design"
    best_plot_dir.mkdir(parents=True, exist_ok=True)
    x_in = build_x_grid(
        geometry.total_length_in,
        stations=stations,
        critical_positions_in=[geometry.support_a_x_in, geometry.support_b_x_in],
    )
    plot_geometry(geometry, best_plot_dir, x_in)
    for load_case in load_cases:
        result = analyze_load_case(geometry, material, load_case, stations=stations)
        plot_load_case(result, load_case, best_plot_dir)
    plot_parameter_map(design_dir / "beam_parameter_map.png", geometry, load_cases)

    report_lines = [
        f"# Rank {rank:02d}: {source_run} eval {evaluation_id}",
        "",
        f"- Weight-first rank score: `{candidate['rank_score']:.6f}`",
        f"- Weight: `{metrics['weight_lbf']:.5f} lbf`",
        f"- Minimum FoS: `{metrics['min_factor_of_safety']:.3f}`",
        f"- Max deflection: `{metrics['max_deflection_in']:.5f} in`",
        f"- LC2 FoS, x=3..7: mean `{metrics['fos_3to7_mean']:.3f}`, std `{metrics['fos_3to7_std']:.3f}`, range `{metrics['fos_3to7_range']:.3f}`",
        f"- Print checks: wall `{payload['geometry']['wall_thickness_in']:.3f} in`, max opening `{metrics['max_web_opening_ratio']:.3f}`, min ligament `{metrics['min_print_web_ligament_in']:.3f} in`",
        f"- Governing case/location: `{metrics['governing_load_case']}` at `x = {metrics['governing_x_in']:.3f} in`",
        f"- Source run: `{source_run}`",
        f"- Source evaluation id: `{evaluation_id}`",
        "",
        "This folder is a ranked report artifact generated from a feasible, corrected 9 in design candidate.",
    ]
    (design_dir / "README.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "rank": str(rank),
        "folder": str(design_dir),
        "source_run": source_run,
        "source_evaluation_id": str(evaluation_id),
        "rank_score": f"{candidate['rank_score']:.8f}",
        "weight_lbf": f"{metrics['weight_lbf']:.8f}",
        "min_fos": f"{metrics['min_factor_of_safety']:.8f}",
        "max_deflection_in": f"{metrics['max_deflection_in']:.8f}",
        "fos_3to7_std": f"{metrics['fos_3to7_std']:.8f}",
        "fos_3to7_range": f"{metrics['fos_3to7_range']:.8f}",
        "wall_thickness_in": f"{payload['geometry']['wall_thickness_in']:.8f}",
        "max_web_opening_ratio": f"{metrics['max_web_opening_ratio']:.8f}",
        "min_print_web_ligament_in": f"{metrics['min_print_web_ligament_in']:.8f}",
        "min_shell_area_ratio": f"{metrics['min_shell_area_ratio']:.8f}",
        "max_dim_slope_in_per_in": f"{metrics['max_dim_slope_in_per_in']:.8f}",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank feasible corrected beam designs and organize report artifacts.")
    parser.add_argument("--active-runs-dir", default="designs/active_runs")
    parser.add_argument("--output-dir", default="best-designs-20")
    parser.add_argument("--archive-dir", default="archive/ranked-design-candidates")
    parser.add_argument("--top-count", type=int, default=20)
    parser.add_argument("--stations", type=int, default=1601)
    parser.add_argument("--flat-x-min-in", type=float, default=3.0)
    parser.add_argument("--flat-x-max-in", type=float, default=7.0)
    parser.add_argument("--min-wall-thickness-in", type=float, default=0.060)
    parser.add_argument("--max-web-opening-ratio", type=float, default=0.35)
    parser.add_argument("--min-web-ligament-in", type=float, default=0.120)
    parser.add_argument("--min-shell-area-ratio", type=float, default=0.280)
    parser.add_argument("--max-dim-slope-in-per-in", type=float, default=0.140)
    parser.add_argument("--max-deflection-in", type=float, default=0.165)
    args = parser.parse_args()

    active_runs_dir = Path(args.active_runs_dir)
    output_dir = Path(args.output_dir)
    ranked_dir = output_dir / "ranked-designs"
    archive_dir = Path(args.archive_dir)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    if archive_dir.exists():
        shutil.rmtree(archive_dir)
    ranked_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    candidates = discover_candidates(
        active_runs_dir=active_runs_dir,
        stations=args.stations,
        flat_x_min=args.flat_x_min_in,
        flat_x_max=args.flat_x_max_in,
        min_wall_thickness_in=args.min_wall_thickness_in,
        max_web_opening_ratio=args.max_web_opening_ratio,
        min_web_ligament_in=args.min_web_ligament_in,
        min_shell_area_ratio=args.min_shell_area_ratio,
        max_dim_slope_in_per_in=args.max_dim_slope_in_per_in,
        max_deflection_in=args.max_deflection_in,
    )
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            candidate["payload"]["metrics"]["weight_lbf"],
            candidate["payload"]["metrics"]["max_deflection_in"],
            abs(candidate["payload"]["metrics"]["min_factor_of_safety"] - 1.5),
            candidate["payload"]["metrics"]["fos_3to7_std"],
        ),
    )
    top = ranked[: args.top_count]
    rest = ranked[args.top_count :]

    summary_rows = [
        write_candidate_folder(candidate, rank, ranked_dir, args.stations)
        for rank, candidate in enumerate(top, start=1)
    ]
    write_csv(output_dir / "ranking_summary.csv", summary_rows)

    archive_rows: list[dict[str, str]] = []
    for rank, candidate in enumerate(rest, start=args.top_count + 1):
        metrics = candidate["payload"]["metrics"]
        archive_rows.append(
            {
                "rank": str(rank),
                "source_run": candidate["source_run"],
                "source_evaluation_id": str(candidate["source_evaluation_id"]),
                "rank_score": f"{candidate['rank_score']:.8f}",
                "weight_lbf": f"{metrics['weight_lbf']:.8f}",
                "min_fos": f"{metrics['min_factor_of_safety']:.8f}",
                "max_deflection_in": f"{metrics['max_deflection_in']:.8f}",
                "fos_3to7_std": f"{metrics['fos_3to7_std']:.8f}",
                "fos_3to7_range": f"{metrics['fos_3to7_range']:.8f}",
                "wall_thickness_in": f"{candidate['payload']['geometry']['wall_thickness_in']:.8f}",
                "max_web_opening_ratio": f"{metrics['max_web_opening_ratio']:.8f}",
                "min_print_web_ligament_in": f"{metrics['min_print_web_ligament_in']:.8f}",
                "min_shell_area_ratio": f"{metrics['min_shell_area_ratio']:.8f}",
                "max_dim_slope_in_per_in": f"{metrics['max_dim_slope_in_per_in']:.8f}",
            }
        )
    write_csv(archive_dir / "ranked_candidates_after_top20.csv", archive_rows)

    readme_lines = [
        "# Best Designs 20",
        "",
        "Top 20 feasible corrected 9 in beam candidates for report review.",
        "",
        "Ranking formula: `weight_lbf`, with tie-breakers `max_deflection_in`, `abs(min_fos - 1.5)`, then `fos_3to7_std`.",
        "",
        "Weight is the primary ranking target. Load Case 2 flatness over x=3..7 is retained as a reported metric and late tie-breaker.",
        "",
        "## Folders",
        "",
        "- `ranked-designs/`: one folder per top-20 candidate, prefixed with report rank.",
        "- `3d-models/`: generated STL/OBJ/DXF/preview assets after running `scripts/beam_3d_models.py`.",
        "- `report-packages/`: packaged copies of each ranked candidate after 3D generation.",
        "- `ranking_summary.csv`: compact table for report selection.",
        "",
        f"Archived non-top-20 ranked candidates: `{archive_dir.as_posix()}/ranked_candidates_after_top20.csv`.",
    ]
    (output_dir / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    print(f"Ranked candidates discovered: {len(ranked)}")
    print(f"Top folders written: {len(top)}")
    print(f"Remaining candidates archived in: {archive_dir.resolve()}")
    print(f"Best designs folder: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
