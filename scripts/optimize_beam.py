from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from beam_solver import (
    KNOWN_MATERIALS,
    Material,
    TaperedRectangularTube,
    analyze_load_case,
    build_load_cases,
    build_x_grid,
    default_material,
    plot_geometry,
    plot_load_case,
)


@dataclass(frozen=True)
class ConstraintConfig:
    min_factor_of_safety: float
    max_deflection_in: float | None


@dataclass(frozen=True)
class DurabilityConfig:
    min_web_ligament_in: float
    min_shell_area_ratio: float
    max_height_ratio: float
    max_width_ratio: float
    max_dim_slope_in_per_in: float
    stress_concentration_limit: float


@dataclass(frozen=True)
class SearchConfig:
    initial_samples: int
    refinement_rounds: int
    elite_count: int
    local_samples_per_elite: int
    min_feasible_designs: int
    excess_fos_weight: float
    underutilization_weight: float
    uniformity_weight: float
    symmetry_weight: float
    smoothness_weight: float
    envelope_stress_floor_ratio: float
    uniformity_case: str
    mirror_profile: bool
    seed: int


@dataclass(frozen=True)
class DesignVariableBounds:
    left_width_in: tuple[float, float]
    mid_width_in: tuple[float, float]
    right_width_in: tuple[float, float]
    left_height_in: tuple[float, float]
    mid_height_in: tuple[float, float]
    right_height_in: tuple[float, float]
    wall_thickness_in: tuple[float, float]
    left_web_opening_ratio: tuple[float, float]
    mid_web_opening_ratio: tuple[float, float]
    right_web_opening_ratio: tuple[float, float]

    def items(self) -> list[tuple[str, tuple[float, float]]]:
        return [
            ("left_width_in", self.left_width_in),
            ("mid_width_in", self.mid_width_in),
            ("right_width_in", self.right_width_in),
            ("left_height_in", self.left_height_in),
            ("mid_height_in", self.mid_height_in),
            ("right_height_in", self.right_height_in),
            ("wall_thickness_in", self.wall_thickness_in),
            ("left_web_opening_ratio", self.left_web_opening_ratio),
            ("mid_web_opening_ratio", self.mid_web_opening_ratio),
            ("right_web_opening_ratio", self.right_web_opening_ratio),
        ]


@dataclass
class LoadCaseSummary:
    name: str
    orientation: str
    load_lbf: float
    location_in: float
    reaction_a_lbf: float
    reaction_b_lbf: float
    max_von_mises_psi: float
    max_von_mises_x_in: float
    min_factor_of_safety: float
    min_factor_of_safety_x_in: float
    max_deflection_in: float
    max_deflection_x_in: float
    max_slope_rad: float


@dataclass
class DesignEvaluation:
    evaluation_id: int
    geometry: TaperedRectangularTube
    weight_lbf: float
    min_factor_of_safety: float
    max_deflection_in: float
    feasible: bool
    objective: float
    penalty: float
    excess_factor_of_safety: float
    underutilization_score: float
    uniformity_score: float
    symmetry_score: float
    smoothness_score: float
    governing_load_case: str
    governing_x_in: float
    durability_score: float
    constraint_violations: list[str]
    load_case_summaries: list[LoadCaseSummary]


def latin_hypercube_samples(
    bounds: DesignVariableBounds,
    sample_count: int,
    rng: np.random.Generator,
) -> list[dict[str, float]]:
    variable_items = bounds.items()
    dimension_count = len(variable_items)
    matrix = np.zeros((sample_count, dimension_count))

    for index, (_, (lower, upper)) in enumerate(variable_items):
        bins = (np.arange(sample_count, dtype=float) + rng.random(sample_count)) / sample_count
        rng.shuffle(bins)
        matrix[:, index] = lower + bins * (upper - lower)

    samples: list[dict[str, float]] = []
    for row in matrix:
        sample = {
            variable_items[index][0]: float(row[index])
            for index in range(dimension_count)
        }
        samples.append(sample)
    return samples


def local_refinement_samples(
    elite_geometries: list[TaperedRectangularTube],
    bounds: DesignVariableBounds,
    samples_per_elite: int,
    shrink_factor: float,
    rng: np.random.Generator,
) -> list[dict[str, float]]:
    bound_map = dict(bounds.items())
    candidates: list[dict[str, float]] = []

    for geometry in elite_geometries:
        center = asdict(geometry)
        for _ in range(samples_per_elite):
            sample: dict[str, float] = {}
            for name, (lower, upper) in bound_map.items():
                span = upper - lower
                sigma = max(span * shrink_factor, 1.0e-6)
                sample[name] = float(np.clip(rng.normal(center[name], sigma), lower, upper))
            candidates.append(sample)

    return candidates


def build_geometry_from_variables(
    variables: dict[str, float],
    span_in: float,
    total_length_in: float,
    mirror_profile: bool = False,
) -> TaperedRectangularTube:
    right_width_in = variables["left_width_in"] if mirror_profile else variables["right_width_in"]
    right_height_in = variables["left_height_in"] if mirror_profile else variables["right_height_in"]
    right_web_opening_ratio = (
        variables["left_web_opening_ratio"]
        if mirror_profile
        else variables["right_web_opening_ratio"]
    )
    return TaperedRectangularTube(
        span_in=span_in,
        total_length_in=total_length_in,
        left_width_in=variables["left_width_in"],
        mid_width_in=variables["mid_width_in"],
        right_width_in=right_width_in,
        left_height_in=variables["left_height_in"],
        mid_height_in=variables["mid_height_in"],
        right_height_in=right_height_in,
        wall_thickness_in=variables["wall_thickness_in"],
        left_web_opening_ratio=variables["left_web_opening_ratio"],
        mid_web_opening_ratio=variables["mid_web_opening_ratio"],
        right_web_opening_ratio=right_web_opening_ratio,
    )


def assess_shape_bias(
    geometry: TaperedRectangularTube,
    x_in: np.ndarray,
) -> tuple[float, float]:
    width = geometry.width_profile(x_in)
    height = geometry.height_profile(x_in)
    opening_ratio = geometry.web_opening_ratio_profile(x_in)

    width_scale = max(float(np.mean(width)), 1.0e-9)
    height_scale = max(float(np.mean(height)), 1.0e-9)

    mirrored_width_error = (width - width[::-1]) / width_scale
    mirrored_height_error = (height - height[::-1]) / height_scale
    mirrored_opening_error = opening_ratio - opening_ratio[::-1]
    symmetry_score = float(
        np.mean(mirrored_width_error**2)
        + np.mean(mirrored_height_error**2)
        + np.mean(mirrored_opening_error**2)
    )

    width_gradient = np.gradient(width, x_in) / width_scale
    height_gradient = np.gradient(height, x_in) / height_scale
    opening_gradient = np.gradient(opening_ratio, x_in)
    smoothness_score = float(
        np.mean(width_gradient**2)
        + np.mean(height_gradient**2)
        + 0.25 * np.mean(opening_gradient**2)
    )
    return symmetry_score, smoothness_score


def assess_uniformity(
    analysis_results: list[Any],
    target_stress_psi: float,
    stress_floor_ratio: float,
    uniformity_case: str,
) -> float:
    if uniformity_case == "load1":
        selected_results = analysis_results[:1]
    elif uniformity_case == "load2":
        selected_results = analysis_results[1:2]
    else:
        selected_results = analysis_results

    if not selected_results:
        return 0.0

    squared_error_terms: list[np.ndarray] = []
    stress_floor = stress_floor_ratio * target_stress_psi
    for result in selected_results:
        significant_mask = result.von_mises_psi >= stress_floor
        if not np.any(significant_mask):
            significant_mask = result.von_mises_psi > 0.0
        if not np.any(significant_mask):
            continue
        normalized_error = (
            (result.von_mises_psi[significant_mask] - target_stress_psi)
            / max(target_stress_psi, 1.0e-9)
        )
        squared_error_terms.append(normalized_error**2)

    if not squared_error_terms:
        return 0.0
    return float(np.mean(np.concatenate(squared_error_terms)))


def summarize_load_case(result: Any, load_case: Any) -> LoadCaseSummary:
    return LoadCaseSummary(
        name=load_case.name,
        orientation=load_case.orientation,
        load_lbf=load_case.load_lbf,
        location_in=load_case.location_in,
        reaction_a_lbf=float(result.reaction_a_lbf),
        reaction_b_lbf=float(result.reaction_b_lbf),
        max_von_mises_psi=float(result.max_von_mises_psi),
        max_von_mises_x_in=float(result.max_von_mises_x_in),
        min_factor_of_safety=float(result.min_factor_of_safety),
        min_factor_of_safety_x_in=float(result.min_factor_of_safety_x_in),
        max_deflection_in=float(result.max_deflection_in),
        max_deflection_x_in=float(result.max_deflection_x_in),
        max_slope_rad=float(np.max(np.abs(result.slope_rad))),
    )


def assess_durability(
    geometry: TaperedRectangularTube,
    analysis_results: list[Any],
    durability_config: DurabilityConfig,
) -> tuple[list[str], float]:
    x_in = analysis_results[0].x_in

    width = geometry.width_profile(x_in)
    height = geometry.height_profile(x_in)
    area = geometry.area(x_in)
    opening_ratio = geometry.web_opening_ratio_profile(x_in)
    clear_height = geometry.inner_height_profile(x_in)

    web_ligament = 0.5 * (1.0 - opening_ratio) * clear_height
    min_web_ligament = float(np.min(web_ligament))

    shell_area_ratio = np.divide(
        area,
        width * height,
        out=np.zeros_like(area),
        where=(width * height) > 1.0e-12,
    )
    min_shell_area_ratio = float(np.min(shell_area_ratio))

    height_ratio = float(np.max(height) / np.min(height))
    width_ratio = float(np.max(width) / np.min(width))

    height_slope = float(np.max(np.abs(np.gradient(height, x_in))))
    width_slope = float(np.max(np.abs(np.gradient(width, x_in))))
    max_dim_slope = max(height_slope, width_slope)

    envelope_von_mises = np.max(np.vstack([result.von_mises_psi for result in analysis_results]), axis=0)
    median_envelope = float(np.median(envelope_von_mises))
    stress_concentration = float(np.max(envelope_von_mises) / max(median_envelope, 1.0e-9))

    violations: list[str] = []
    if min_web_ligament < durability_config.min_web_ligament_in:
        violations.append(
            f"Durability check failed: minimum residual web ligament {min_web_ligament:.4f} in is below "
            f"{durability_config.min_web_ligament_in:.4f} in."
        )
    if min_shell_area_ratio < durability_config.min_shell_area_ratio:
        violations.append(
            f"Durability check failed: minimum shell area ratio {min_shell_area_ratio:.3f} is below "
            f"{durability_config.min_shell_area_ratio:.3f}."
        )
    if height_ratio > durability_config.max_height_ratio:
        violations.append(
            f"Durability check failed: height ratio {height_ratio:.3f} exceeds {durability_config.max_height_ratio:.3f}."
        )
    if width_ratio > durability_config.max_width_ratio:
        violations.append(
            f"Durability check failed: width ratio {width_ratio:.3f} exceeds {durability_config.max_width_ratio:.3f}."
        )
    if max_dim_slope > durability_config.max_dim_slope_in_per_in:
        violations.append(
            f"Durability check failed: max profile slope {max_dim_slope:.3f} in/in exceeds "
            f"{durability_config.max_dim_slope_in_per_in:.3f} in/in."
        )
    if stress_concentration > durability_config.stress_concentration_limit:
        violations.append(
            f"Durability check failed: stress concentration factor {stress_concentration:.3f} exceeds "
            f"{durability_config.stress_concentration_limit:.3f}."
        )

    normalized_terms = [
        max(0.0, (durability_config.min_web_ligament_in - min_web_ligament) / durability_config.min_web_ligament_in),
        max(0.0, (durability_config.min_shell_area_ratio - min_shell_area_ratio) / durability_config.min_shell_area_ratio),
        max(0.0, (height_ratio - durability_config.max_height_ratio) / durability_config.max_height_ratio),
        max(0.0, (width_ratio - durability_config.max_width_ratio) / durability_config.max_width_ratio),
        max(0.0, (max_dim_slope - durability_config.max_dim_slope_in_per_in) / durability_config.max_dim_slope_in_per_in),
        max(
            0.0,
            (stress_concentration - durability_config.stress_concentration_limit)
            / durability_config.stress_concentration_limit,
        ),
    ]
    durability_score = float(np.mean(np.square(normalized_terms)))
    return violations, durability_score


def evaluate_design(
    evaluation_id: int,
    geometry: TaperedRectangularTube,
    material: Material,
    load_cases: list[Any],
    constraint_config: ConstraintConfig,
    durability_config: DurabilityConfig,
    search_config: SearchConfig,
    stations: int,
) -> DesignEvaluation:
    violations: list[str] = []

    try:
        geometry.validate()
    except ValueError as exc:
        return DesignEvaluation(
            evaluation_id=evaluation_id,
            geometry=geometry,
            weight_lbf=float("inf"),
            min_factor_of_safety=0.0,
            max_deflection_in=float("inf"),
            feasible=False,
            objective=float("inf"),
            penalty=float("inf"),
            excess_factor_of_safety=float("inf"),
            underutilization_score=float("inf"),
            uniformity_score=float("inf"),
            symmetry_score=float("inf"),
            smoothness_score=float("inf"),
            governing_load_case="invalid",
            governing_x_in=float("nan"),
            durability_score=float("inf"),
            constraint_violations=[str(exc)],
            load_case_summaries=[],
        )

    load_case_summaries: list[LoadCaseSummary] = []
    analysis_results: list[Any] = []
    weight_lbf = 0.0

    for load_case in load_cases:
        result = analyze_load_case(
            geometry=geometry,
            material=material,
            load_case=load_case,
            stations=stations,
        )
        analysis_results.append(result)
        load_case_summaries.append(summarize_load_case(result, load_case))
        weight_lbf = float(result.weight_lbf)

    min_factor_of_safety = min(summary.min_factor_of_safety for summary in load_case_summaries)
    max_deflection_in = max(summary.max_deflection_in for summary in load_case_summaries)
    governing_summary = min(load_case_summaries, key=lambda summary: summary.min_factor_of_safety)

    fos_gap = max(0.0, constraint_config.min_factor_of_safety - min_factor_of_safety)
    if fos_gap > 0.0:
        violations.append(
            f"Minimum factor of safety {min_factor_of_safety:.3f} is below the target {constraint_config.min_factor_of_safety:.3f}."
        )

    deflection_gap = 0.0
    if constraint_config.max_deflection_in is not None:
        deflection_gap = max(0.0, max_deflection_in - constraint_config.max_deflection_in)
        if deflection_gap > 0.0:
            violations.append(
                f"Maximum deflection {max_deflection_in:.5f} in exceeds the limit {constraint_config.max_deflection_in:.5f} in."
            )

    excess_factor_of_safety = max(0.0, min_factor_of_safety - constraint_config.min_factor_of_safety)

    target_stress_psi = material.effective_allowable_stress_psi / constraint_config.min_factor_of_safety
    envelope_von_mises_psi = np.max(
        np.vstack([result.von_mises_psi for result in analysis_results]),
        axis=0,
    )
    significant_mask = envelope_von_mises_psi >= (
        search_config.envelope_stress_floor_ratio * target_stress_psi
    )
    if not np.any(significant_mask):
        significant_mask = envelope_von_mises_psi > 0.0

    underutilization_score = 0.0
    if np.any(significant_mask):
        underutilization_ratio = np.clip(
            (target_stress_psi - envelope_von_mises_psi[significant_mask]) / target_stress_psi,
            a_min=0.0,
            a_max=None,
        )
        underutilization_score = float(np.mean(underutilization_ratio**2))

    uniformity_score = assess_uniformity(
        analysis_results=analysis_results,
        target_stress_psi=target_stress_psi,
        stress_floor_ratio=search_config.envelope_stress_floor_ratio,
        uniformity_case=search_config.uniformity_case,
    )

    symmetry_score, smoothness_score = assess_shape_bias(
        geometry=geometry,
        x_in=analysis_results[0].x_in,
    )

    durability_violations, durability_score = assess_durability(
        geometry=geometry,
        analysis_results=analysis_results,
        durability_config=durability_config,
    )
    violations.extend(durability_violations)

    penalty = 500.0 * fos_gap**2 + 10_000.0 * deflection_gap**2
    objective = (
        weight_lbf
        + penalty
        + search_config.excess_fos_weight * excess_factor_of_safety**2
        + search_config.underutilization_weight * underutilization_score
        + search_config.uniformity_weight * uniformity_score
        + search_config.symmetry_weight * symmetry_score
        + search_config.smoothness_weight * smoothness_score
        + 50.0 * durability_score
    )

    return DesignEvaluation(
        evaluation_id=evaluation_id,
        geometry=geometry,
        weight_lbf=weight_lbf,
        min_factor_of_safety=min_factor_of_safety,
        max_deflection_in=max_deflection_in,
        feasible=not violations,
        objective=objective,
        penalty=penalty,
        excess_factor_of_safety=excess_factor_of_safety,
        underutilization_score=underutilization_score,
        uniformity_score=uniformity_score,
        symmetry_score=symmetry_score,
        smoothness_score=smoothness_score,
        governing_load_case=governing_summary.name,
        governing_x_in=governing_summary.min_factor_of_safety_x_in,
        durability_score=durability_score,
        constraint_violations=violations,
        load_case_summaries=load_case_summaries,
    )


def choose_elites(evaluations: list[DesignEvaluation], elite_count: int) -> list[TaperedRectangularTube]:
    ordered = sorted(
        evaluations,
        key=lambda evaluation: (
            not evaluation.feasible,
            evaluation.objective,
            evaluation.weight_lbf,
        ),
    )
    return [evaluation.geometry for evaluation in ordered[:elite_count]]


def export_design_study_csv(evaluations: list[DesignEvaluation], csv_path: Path) -> None:
    fieldnames = [
        "evaluation_id",
        "feasible",
                "objective",
                "penalty",
                "weight_lbf",
                "min_factor_of_safety",
                "max_deflection_in",
                "excess_factor_of_safety",
                "underutilization_score",
                "uniformity_score",
                "symmetry_score",
                "smoothness_score",
                "durability_score",
                "governing_load_case",
                "governing_x_in",
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
        "violations",
    ]

    for suffix in ("load_case_1", "load_case_2"):
        fieldnames.extend(
            [
                f"{suffix}_max_von_mises_psi",
                f"{suffix}_max_von_mises_x_in",
                f"{suffix}_min_factor_of_safety",
                f"{suffix}_min_factor_of_safety_x_in",
                f"{suffix}_max_deflection_in",
                f"{suffix}_max_deflection_x_in",
                f"{suffix}_max_slope_rad",
            ]
        )

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for evaluation in evaluations:
            row = {
                "evaluation_id": evaluation.evaluation_id,
                "feasible": evaluation.feasible,
                "objective": evaluation.objective,
                "penalty": evaluation.penalty,
                "weight_lbf": evaluation.weight_lbf,
                "min_factor_of_safety": evaluation.min_factor_of_safety,
                "max_deflection_in": evaluation.max_deflection_in,
                "excess_factor_of_safety": evaluation.excess_factor_of_safety,
                "underutilization_score": evaluation.underutilization_score,
                "uniformity_score": evaluation.uniformity_score,
                "symmetry_score": evaluation.symmetry_score,
                "smoothness_score": evaluation.smoothness_score,
                "durability_score": evaluation.durability_score,
                "governing_load_case": evaluation.governing_load_case,
                "governing_x_in": evaluation.governing_x_in,
                "left_width_in": evaluation.geometry.left_width_in,
                "mid_width_in": evaluation.geometry.mid_width_in,
                "right_width_in": evaluation.geometry.right_width_in,
                "left_height_in": evaluation.geometry.left_height_in,
                "mid_height_in": evaluation.geometry.mid_height_in,
                "right_height_in": evaluation.geometry.right_height_in,
                "wall_thickness_in": evaluation.geometry.wall_thickness_in,
                "left_web_opening_ratio": evaluation.geometry.left_web_opening_ratio,
                "mid_web_opening_ratio": evaluation.geometry.mid_web_opening_ratio,
                "right_web_opening_ratio": evaluation.geometry.right_web_opening_ratio,
                "violations": " | ".join(evaluation.constraint_violations),
            }

            for index, summary in enumerate(evaluation.load_case_summaries, start=1):
                prefix = f"load_case_{index}"
                row[f"{prefix}_max_von_mises_psi"] = summary.max_von_mises_psi
                row[f"{prefix}_max_von_mises_x_in"] = summary.max_von_mises_x_in
                row[f"{prefix}_min_factor_of_safety"] = summary.min_factor_of_safety
                row[f"{prefix}_min_factor_of_safety_x_in"] = summary.min_factor_of_safety_x_in
                row[f"{prefix}_max_deflection_in"] = summary.max_deflection_in
                row[f"{prefix}_max_deflection_x_in"] = summary.max_deflection_x_in
                row[f"{prefix}_max_slope_rad"] = summary.max_slope_rad

            writer.writerow(row)


def load_case_table_markdown(load_case_summaries: list[LoadCaseSummary]) -> str:
    lines = [
        "| Load Case | Orientation | Load [lbf] | Location [in] | Min FoS | FoS x [in] | Max Deflection [in] | Max von Mises [psi] |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in load_case_summaries:
        lines.append(
            f"| {summary.name} | {summary.orientation} | {summary.load_lbf:.3f} | "
            f"{summary.location_in:.3f} | {summary.min_factor_of_safety:.3f} | {summary.min_factor_of_safety_x_in:.3f} | "
            f"{summary.max_deflection_in:.5f} | {summary.max_von_mises_psi:.1f} |"
        )
    return "\n".join(lines)


def piecewise_profile_latex(symbol: str, left_value: float, mid_value: float, right_value: float, span_in: float) -> str:
    first_slope = 2.0 * (mid_value - left_value) / span_in
    second_slope = 2.0 * (right_value - mid_value) / span_in
    half_span = span_in / 2.0
    return (
        rf"{symbol}(x)=\begin{{cases}}"
        rf"{left_value:.4f} + ({first_slope:.4f})x, & 0 \le x \le {half_span:.4f}\\"
        rf"{mid_value:.4f} + ({second_slope:.4f})(x-{half_span:.4f}), & {half_span:.4f} < x \le {span_in:.4f}"
        rf"\end{{cases}}"
    )


def load_case_substitution_markdown(
    geometry: TaperedRectangularTube,
    material: Material,
    load_case_summaries: list[LoadCaseSummary],
    weight_lbf: float,
) -> str:
    lines = [
        "## Automatic Equation Substitution",
        "",
        "### Effective Material Properties",
        "",
        f"- $E_{{eff}} = E \\times k_{{orientation}} \\times k_{{infill}} = "
        f"{material.elastic_modulus_psi:.1f} \\times {material.orientation_factor:.3f} \\times {material.infill_factor:.3f} = {material.effective_modulus_psi:.1f}\\ \\text{{psi}}$",
        f"- $\\sigma_{{allow,eff}} = \\sigma_{{allow}} \\times k_{{orientation}} \\times k_{{infill}} = "
        f"{material.allowable_stress_psi:.1f} \\times {material.orientation_factor:.3f} \\times {material.infill_factor:.3f} = {material.effective_allowable_stress_psi:.1f}\\ \\text{{psi}}$",
        f"- $W = \\rho \\int_0^L A(x)\\,dx = {weight_lbf:.5f}\\ \\text{{lbf}}$",
        "- Global governing factor of safety is the minimum value over all beam stations and over both load cases.",
        "",
    ]

    for summary in load_case_summaries:
        reaction_a = summary.load_lbf * (geometry.span_in - summary.location_in) / geometry.span_in
        reaction_b = summary.load_lbf * summary.location_in / geometry.span_in
        active_axis = "upright section properties" if summary.orientation == "upright" else "side-rotated section properties"
        lines.extend(
            [
                f"### {summary.name}",
                "",
                f"- Active bending orientation: {summary.orientation} ({active_axis})",
                f"- $R_A = P(L-a)/L = {summary.load_lbf:.3f}({geometry.span_in:.3f}-{summary.location_in:.3f})/{geometry.span_in:.3f} = {reaction_a:.3f}\\ \\text{{lbf}}$",
                f"- $R_B = Pa/L = {summary.load_lbf:.3f}({summary.location_in:.3f})/{geometry.span_in:.3f} = {reaction_b:.3f}\\ \\text{{lbf}}$",
                f"- $FoS_{{min}} = \\sigma_{{allow,eff}}/\\sigma_{{vm,max}} = {material.effective_allowable_stress_psi:.1f}/{summary.max_von_mises_psi:.1f} = {summary.min_factor_of_safety:.3f}$",
                f"- Governing location for this load case: $x = {summary.min_factor_of_safety_x_in:.3f}\\ \\text{{in}}$",
                f"- $\\max |v(x)| = {summary.max_deflection_in:.5f}\\ \\text{{in}}$",
                f"- $\\max |\\theta(x)| = {summary.max_slope_rad:.6f}\\ \\text{{rad}}$",
                "",
            ]
        )

    return "\n".join(lines)


def load_case_substitution_latex(
    geometry: TaperedRectangularTube,
    material: Material,
    load_case_summaries: list[LoadCaseSummary],
    weight_lbf: float,
) -> str:
    blocks = [
        r"\section*{Automatic Equation Substitution}",
        r"\subsection*{Effective Material Properties}",
        r"\["
        + rf"E_{{eff}} = E \cdot k_{{orientation}} \cdot k_{{infill}} = {material.elastic_modulus_psi:.1f}"
        + rf" \cdot {material.orientation_factor:.3f} \cdot {material.infill_factor:.3f} = {material.effective_modulus_psi:.1f}\ \mathrm{{psi}}"
        + r"\]",
        r"\["
        + rf"\sigma_{{allow,eff}} = \sigma_{{allow}} \cdot k_{{orientation}} \cdot k_{{infill}} = {material.allowable_stress_psi:.1f}"
        + rf" \cdot {material.orientation_factor:.3f} \cdot {material.infill_factor:.3f} = {material.effective_allowable_stress_psi:.1f}\ \mathrm{{psi}}"
        + r"\]",
        r"\["
        + rf"W = \rho \int_0^L A(x)\,dx = {weight_lbf:.5f}\ \mathrm{{lbf}}"
        + r"\]",
        r"Global governing factor of safety is the minimum value over all beam stations and over both load cases.",
    ]

    for summary in load_case_summaries:
        reaction_a = summary.load_lbf * (geometry.span_in - summary.location_in) / geometry.span_in
        reaction_b = summary.load_lbf * summary.location_in / geometry.span_in
        active_axis = "upright section properties" if summary.orientation == "upright" else "side-rotated section properties"
        blocks.extend(
            [
                rf"\subsection*{{{latex_escape(summary.name)}}}",
                rf"Active bending orientation: {latex_escape(summary.orientation)} ({latex_escape(active_axis)}).",
                r"\["
                + rf"R_A = \frac{{P(L-a)}}{{L}} = \frac{{{summary.load_lbf:.3f}({geometry.span_in:.3f}-{summary.location_in:.3f})}}{{{geometry.span_in:.3f}}} = {reaction_a:.3f}\ \mathrm{{lbf}}"
                + r"\]",
                r"\["
                + rf"R_B = \frac{{Pa}}{{L}} = \frac{{{summary.load_lbf:.3f}({summary.location_in:.3f})}}{{{geometry.span_in:.3f}}} = {reaction_b:.3f}\ \mathrm{{lbf}}"
                + r"\]",
                r"\["
                + rf"FoS_{{min}} = \frac{{\sigma_{{allow,eff}}}}{{\sigma_{{vm,max}}}} = \frac{{{material.effective_allowable_stress_psi:.1f}}}{{{summary.max_von_mises_psi:.1f}}} = {summary.min_factor_of_safety:.3f}"
                + r"\]",
                r"\["
                + rf"x_{{FoS,min}} = {summary.min_factor_of_safety_x_in:.3f}\ \mathrm{{in}}"
                + r"\]",
                r"\["
                + rf"\max |v(x)| = {summary.max_deflection_in:.5f}\ \mathrm{{in}}, \qquad \max |\theta(x)| = {summary.max_slope_rad:.6f}\ \mathrm{{rad}}"
                + r"\]",
            ]
        )

    return "\n".join(blocks)


def write_markdown_report(
    output_dir: Path,
    best_evaluation: DesignEvaluation,
    feasible_evaluations: list[DesignEvaluation],
    total_evaluations: int,
    search_config: SearchConfig,
    constraint_config: ConstraintConfig,
    material: Material,
    parameter_map_path: Path,
    best_plot_dir: Path,
) -> None:
    geometry = best_evaluation.geometry
    report_path = output_dir / "optimization_report.md"

    lines = [
        "# Beam Optimization Report",
        "",
        "## Search Summary",
        "",
        f"- Search method: stratified global sampling with elite local refinement",
        f"- Total evaluated designs: {total_evaluations}",
        f"- Feasible designs found: {len(feasible_evaluations)}",
        f"- Minimum required factor of safety: {constraint_config.min_factor_of_safety:.3f}",
        f"- Objective shaping: penalize excess FoS margin and underutilized stress envelope so the design approaches the 1.5 target more closely",
        (
            f"- Maximum allowed deflection: {constraint_config.max_deflection_in:.5f} in"
            if constraint_config.max_deflection_in is not None
            else "- Maximum allowed deflection: not enforced in this run"
        ),
        f"- Random seed: {search_config.seed}",
        "",
        "## Best Design",
        "",
        f"- Weight: {best_evaluation.weight_lbf:.5f} lbf",
        f"- Minimum factor of safety: {best_evaluation.min_factor_of_safety:.3f}",
        f"- Excess FoS above target: {best_evaluation.excess_factor_of_safety:.3f}",
        f"- Governing minimum-FoS load case: {best_evaluation.governing_load_case} at x = {best_evaluation.governing_x_in:.3f} in",
        f"- Maximum deflection: {best_evaluation.max_deflection_in:.5f} in",
        f"- Uniformity score toward FoS target (0 is best): {best_evaluation.uniformity_score:.6f}",
        f"- Symmetry score (0 is best): {best_evaluation.symmetry_score:.6f}",
        f"- Smoothness score (0 is best): {best_evaluation.smoothness_score:.6f}",
        f"- Durability score (0 is best): {best_evaluation.durability_score:.6f}",
        (
            "- Constraint status: feasible"
            if best_evaluation.feasible
            else f"- Constraint status: infeasible ({'; '.join(best_evaluation.constraint_violations)})"
        ),
        "",
        "### Geometry Variables",
        "",
        "| Variable | Value |",
        "| --- | ---: |",
        f"| $L$ [in] | {geometry.span_in:.3f} |",
        f"| $L_{{total}}$ [in] | {geometry.total_length_in:.3f} |",
        f"| $b_L$ [in] | {geometry.left_width_in:.3f} |",
        f"| $b_M$ [in] | {geometry.mid_width_in:.3f} |",
        f"| $b_R$ [in] | {geometry.right_width_in:.3f} |",
        f"| $h_L$ [in] | {geometry.left_height_in:.3f} |",
        f"| $h_M$ [in] | {geometry.mid_height_in:.3f} |",
        f"| $h_R$ [in] | {geometry.right_height_in:.3f} |",
        f"| $t$ [in] | {geometry.wall_thickness_in:.3f} |",
        f"| $r_L$ [-] | {geometry.left_web_opening_ratio:.3f} |",
        f"| $r_M$ [-] | {geometry.mid_web_opening_ratio:.3f} |",
        f"| $r_R$ [-] | {geometry.right_web_opening_ratio:.3f} |",
        f"| $E_{{eff}}$ [psi] | {material.effective_modulus_psi:.1f} |",
        f"| $\\sigma_{{allow,eff}}$ [psi] | {material.effective_allowable_stress_psi:.1f} |",
        "",
        "### Best-Design Load-Case Metrics",
        "",
        load_case_table_markdown(best_evaluation.load_case_summaries),
        "",
        "## Beam Structure and Parameters",
        "",
        f"![Beam parameter map]({parameter_map_path.name})",
        "",
        f"![Outer dimension views]({(best_plot_dir / 'outer_dimension_views.png').relative_to(output_dir).as_posix()})",
        "",
        "## General Equations",
        "",
        "### Geometry",
        "",
        f"- $${piecewise_profile_latex('b', geometry.left_width_in, geometry.mid_width_in, geometry.right_width_in, geometry.span_in)}$$",
        f"- $${piecewise_profile_latex('h', geometry.left_height_in, geometry.mid_height_in, geometry.right_height_in, geometry.span_in)}$$",
        f"- $${piecewise_profile_latex('r', geometry.left_web_opening_ratio, geometry.mid_web_opening_ratio, geometry.right_web_opening_ratio, geometry.span_in)}$$",
        "- Hollow tube area with lightening openings: $A(x)=2b(x)t + [1-r(x)]2t[h(x)-2t]$",
        "- Upright bending second moment: $I(x)=\\frac{b(x)h(x)^3-[b(x)-2t][h(x)-2t]^3}{12}-2\\frac{t[r(x)(h(x)-2t)]^3}{12}$",
        "- Side-rotated bending second moment: $I_{side}(x)=\\frac{h(x)b(x)^3-[h(x)-2t][b(x)-2t]^3}{12}-2\\frac{t[r(x)(b(x)-2t)]^3}{12}$",
        "- Section modulus: $S(x)=I(x)/c(x)$ with $c(x)=\\text{outer vertical dimension}/2$",
        "",
        "### Statics and Stress",
        "",
        "- Reactions for a point load $P$ at $x=a$: $R_A=P(L-a)/L$, $R_B=Pa/L$",
        "- Shear and moment: $V(x)$ and $M(x)$ are computed piecewise from the reactions and applied load",
        "- Bending stress: $\\sigma_b(x)=|M(x)|/S(x)$",
        "- Shear stress estimate: $\\tau(x)=|V(x)|/A_{shear}(x)$ with $A_{shear}(x)=[1-r(x)]2t\\,h_{clear}(x)$ for the active orientation",
        "- von Mises stress: $\\sigma_{vm}(x)=\\sqrt{\\sigma_b(x)^2+3\\tau(x)^2}$",
        "- Factor of safety: $FoS(x)=\\sigma_{allow,eff}/\\sigma_{vm}(x)$",
        "",
        "### Deflection and Objective",
        "",
        "- Euler-Bernoulli relation: $E_{eff}I(x)v''(x)=M(x)$",
        "- Weight objective: $W=\\rho\\int_0^L A(x)\\,dx$",
        "- Search objective used here: minimize weight while enforcing factor-of-safety and optional deflection constraints",
        "",
        load_case_substitution_markdown(
            geometry=geometry,
            material=material,
            load_case_summaries=best_evaluation.load_case_summaries,
            weight_lbf=best_evaluation.weight_lbf,
        ),
        "",
        "## Automatic Trail of Tried Designs",
        "",
        "- Full design study table: `design_study.csv`",
        "- Best design record: `best_design.json`",
        "- Best-design plots folder: `best_design/`",
    ]

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_escape(value: str) -> str:
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("&", r"\&")
    )


def write_latex_report(
    output_dir: Path,
    best_evaluation: DesignEvaluation,
    feasible_evaluations: list[DesignEvaluation],
    total_evaluations: int,
    search_config: SearchConfig,
    constraint_config: ConstraintConfig,
    material: Material,
    parameter_map_path: Path,
    best_plot_dir: Path,
) -> None:
    geometry = best_evaluation.geometry
    tex_path = output_dir / "optimization_report.tex"
    relative_parameter_map = parameter_map_path.relative_to(output_dir).as_posix()
    relative_outer_plot = (best_plot_dir / "outer_dimension_views.png").relative_to(output_dir).as_posix()

    load_case_rows = "\n".join(
        [
            (
                f"{latex_escape(summary.name)} & {latex_escape(summary.orientation)} & "
                f"{summary.load_lbf:.3f} & {summary.location_in:.3f} & "
                f"{summary.min_factor_of_safety:.3f} & {summary.min_factor_of_safety_x_in:.3f} & {summary.max_deflection_in:.5f} & "
                f"{summary.max_von_mises_psi:.1f} \\\\"
            )
            for summary in best_evaluation.load_case_summaries
        ]
    )

    tex_content = rf"""\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{float}}
\title{{Beam Optimization Report}}
\date{{}}
\begin{{document}}
\maketitle

\section*{{Search Summary}}
\begin{{itemize}}
\item Search method: stratified global sampling with elite local refinement
\item Total evaluated designs: {total_evaluations}
\item Feasible designs found: {len(feasible_evaluations)}
\item Minimum required factor of safety: {constraint_config.min_factor_of_safety:.3f}
\item Objective shaping: penalize excess FoS margin and underutilized stress envelope so the design approaches the 1.5 target more closely
\item Maximum allowed deflection: {"not enforced" if constraint_config.max_deflection_in is None else f"{constraint_config.max_deflection_in:.5f} in"}
\item Random seed: {search_config.seed}
\end{{itemize}}

\section*{{Best Design}}
\begin{{itemize}}
\item Weight: {best_evaluation.weight_lbf:.5f} lbf
\item Minimum factor of safety: {best_evaluation.min_factor_of_safety:.3f}
\item Excess FoS above target: {best_evaluation.excess_factor_of_safety:.3f}
\item Governing minimum-FoS load case: {latex_escape(best_evaluation.governing_load_case)} at $x={best_evaluation.governing_x_in:.3f}$ in
\item Maximum deflection: {best_evaluation.max_deflection_in:.5f} in
\item Uniformity score toward FoS target (0 is best): {best_evaluation.uniformity_score:.6f}
\item Symmetry score (0 is best): {best_evaluation.symmetry_score:.6f}
\item Smoothness score (0 is best): {best_evaluation.smoothness_score:.6f}
\item Durability score (0 is best): {best_evaluation.durability_score:.6f}
\item Effective modulus: {material.effective_modulus_psi:.1f} psi
\item Effective allowable stress: {material.effective_allowable_stress_psi:.1f} psi
\end{{itemize}}

\subsection*{{Geometry Variables}}
\begin{{center}}
\begin{{tabular}}{{lr}}
\toprule
Variable & Value \\
\midrule
$L$ [in] & {geometry.span_in:.3f} \\
$L_{{total}}$ [in] & {geometry.total_length_in:.3f} \\
$b_L$ [in] & {geometry.left_width_in:.3f} \\
$b_M$ [in] & {geometry.mid_width_in:.3f} \\
$b_R$ [in] & {geometry.right_width_in:.3f} \\
$h_L$ [in] & {geometry.left_height_in:.3f} \\
$h_M$ [in] & {geometry.mid_height_in:.3f} \\
$h_R$ [in] & {geometry.right_height_in:.3f} \\
$t$ [in] & {geometry.wall_thickness_in:.3f} \\
$r_L$ [-] & {geometry.left_web_opening_ratio:.3f} \\
$r_M$ [-] & {geometry.mid_web_opening_ratio:.3f} \\
$r_R$ [-] & {geometry.right_web_opening_ratio:.3f} \\
\bottomrule
\end{{tabular}}
\end{{center}}

\subsection*{{Beam Structure and Parameters}}
\begin{{figure}}[H]
\centering
\includegraphics[width=0.85\textwidth]{{{relative_parameter_map}}}
\caption{{Variable map used in the optimization run.}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.9\textwidth]{{{relative_outer_plot}}}
\caption{{Outer dimension views for the best design.}}
\end{{figure}}

\subsection*{{Best-Design Load-Case Metrics}}
\begin{{center}}
\begin{{tabular}}{{llllllll}}
\toprule
Load Case & Orientation & Load [lbf] & Location [in] & Min FoS & FoS x [in] & Max Defl. [in] & Max $\sigma_{{vm}}$ [psi] \\
\midrule
{load_case_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{General Equations}}
\subsection*{{Geometry}}
\[
{piecewise_profile_latex('b', geometry.left_width_in, geometry.mid_width_in, geometry.right_width_in, geometry.span_in)}
\]
\[
{piecewise_profile_latex('h', geometry.left_height_in, geometry.mid_height_in, geometry.right_height_in, geometry.span_in)}
\]
\[
{piecewise_profile_latex('r', geometry.left_web_opening_ratio, geometry.mid_web_opening_ratio, geometry.right_web_opening_ratio, geometry.span_in)}
\]
\[
A(x)=2b(x)t+[1-r(x)]2t[h(x)-2t]
\]
\[
I_{{upright}}(x)=\frac{{b(x)h(x)^3-[b(x)-2t][h(x)-2t]^3}}{{12}}-2\frac{{t[r(x)(h(x)-2t)]^3}}{{12}}
\]
\[
I_{{side}}(x)=\frac{{h(x)b(x)^3-[h(x)-2t][b(x)-2t]^3}}{{12}}-2\frac{{t[r(x)(b(x)-2t)]^3}}{{12}}
\]
\[
S(x)=\frac{{I(x)}}{{c(x)}}
\]

\subsection*{{Statics, Stress, and Deflection}}
\[
R_A=\frac{{P(L-a)}}{{L}}, \qquad R_B=\frac{{Pa}}{{L}}
\]
\[
\sigma_b(x)=\frac{{|M(x)|}}{{S(x)}}
\]
\[
\tau(x)=\frac{{|V(x)|}}{{A_{{shear}}(x)}}, \qquad A_{{shear}}(x)=[1-r(x)]2t\,h_{{clear}}(x)
\]
\[
\sigma_{{vm}}(x)=\sqrt{{\sigma_b(x)^2+3\tau(x)^2}}
\]
\[
FoS(x)=\frac{{\sigma_{{allow,eff}}}}{{\sigma_{{vm}}(x)}}
\]
\[
E_{{eff}}I(x)v''(x)=M(x)
\]
\[
W=\rho\int_0^L A(x)\,dx
\]

{load_case_substitution_latex(
    geometry=geometry,
    material=material,
    load_case_summaries=best_evaluation.load_case_summaries,
    weight_lbf=best_evaluation.weight_lbf,
)}

\section*{{Automatic Trail of Tried Designs}}
The optimizer writes every evaluated candidate to \texttt{{design\_study.csv}}, the selected best design to \texttt{{best\_design.json}}, and the best-design plots to the \texttt{{best\_design/}} folder.

\end{{document}}
"""
    tex_path.write_text(tex_content, encoding="utf-8")


def save_best_design_json(
    output_dir: Path,
    best_evaluation: DesignEvaluation,
    search_config: SearchConfig,
    constraint_config: ConstraintConfig,
    durability_config: DurabilityConfig,
) -> None:
    json_path = output_dir / "best_design.json"
    payload = {
        "search_config": asdict(search_config),
        "constraint_config": asdict(constraint_config),
        "durability_config": asdict(durability_config),
        "geometry": asdict(best_evaluation.geometry),
        "metrics": {
            "weight_lbf": best_evaluation.weight_lbf,
            "min_factor_of_safety": best_evaluation.min_factor_of_safety,
            "max_deflection_in": best_evaluation.max_deflection_in,
            "governing_load_case": best_evaluation.governing_load_case,
            "governing_x_in": best_evaluation.governing_x_in,
            "feasible": best_evaluation.feasible,
            "objective": best_evaluation.objective,
            "penalty": best_evaluation.penalty,
            "uniformity_score": best_evaluation.uniformity_score,
            "symmetry_score": best_evaluation.symmetry_score,
            "smoothness_score": best_evaluation.smoothness_score,
            "durability_score": best_evaluation.durability_score,
            "constraint_violations": best_evaluation.constraint_violations,
        },
        "load_cases": [asdict(summary) for summary in best_evaluation.load_case_summaries],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def plot_parameter_map(
    output_path: Path,
    geometry: TaperedRectangularTube,
    load_cases: list[Any],
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10, 7))
    x_positions = np.array([0.0, geometry.span_in / 2.0, geometry.span_in])
    x_in = build_x_grid(geometry.span_in, stations=401)

    front = geometry.height_profile(x_in)
    top = geometry.width_profile(x_in)

    axes[0].fill_between(x_in, -front / 2.0, front / 2.0, color="#d0e3f4", alpha=0.85)
    axes[0].plot(x_in, front / 2.0, color="tab:blue", linewidth=2.0)
    axes[0].plot(x_in, -front / 2.0, color="tab:blue", linewidth=2.0)
    for x_pos, height, label in zip(
        x_positions,
        [geometry.left_height_in, geometry.mid_height_in, geometry.right_height_in],
        [r"$h_L$", r"$h_M$", r"$h_R$"],
        strict=True,
    ):
        axes[0].annotate(
            label + f" = {height:.3f} in",
            xy=(x_pos, height / 2.0),
            xytext=(x_pos + 0.1, height / 2.0 + 0.22),
            arrowprops={"arrowstyle": "->", "linewidth": 1.0},
            fontsize=9,
        )
    axes[0].set_title("Front View Variable Map")
    axes[0].set_xlabel("x [in]")
    axes[0].set_ylabel("y [in]")
    axes[0].grid(True, alpha=0.3)

    axes[1].fill_between(x_in, -top / 2.0, top / 2.0, color="#f3ddc5", alpha=0.85)
    axes[1].plot(x_in, top / 2.0, color="tab:orange", linewidth=2.0)
    axes[1].plot(x_in, -top / 2.0, color="tab:orange", linewidth=2.0)
    for x_pos, width, label in zip(
        x_positions,
        [geometry.left_width_in, geometry.mid_width_in, geometry.right_width_in],
        [r"$b_L$", r"$b_M$", r"$b_R$"],
        strict=True,
    ):
        axes[1].annotate(
            label + f" = {width:.3f} in",
            xy=(x_pos, width / 2.0),
            xytext=(x_pos + 0.1, width / 2.0 + 0.18),
            arrowprops={"arrowstyle": "->", "linewidth": 1.0},
            fontsize=9,
        )
    axes[1].annotate(
        rf"$t = {geometry.wall_thickness_in:.3f}$ in",
        xy=(geometry.span_in * 0.85, geometry.right_width_in / 2.0),
        xytext=(geometry.span_in * 0.62, geometry.right_width_in / 2.0 + 0.35),
        arrowprops={"arrowstyle": "->", "linewidth": 1.0},
        fontsize=9,
    )
    axes[1].text(
        geometry.span_in * 0.18,
        -0.72 * np.max(top),
        rf"$r_L,r_M,r_R = ({geometry.left_web_opening_ratio:.2f}, {geometry.mid_web_opening_ratio:.2f}, {geometry.right_web_opening_ratio:.2f})$",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.75, "edgecolor": "0.7"},
    )

    for load_case in load_cases:
        axes[1].axvline(load_case.location_in, color="tab:red", linestyle="--", linewidth=1.0)
        axes[1].text(
            load_case.location_in,
            0.0,
            f"{load_case.name}\nP={load_case.load_lbf:.2f} lbf",
            ha="center",
            va="center",
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.75, "edgecolor": "0.7"},
        )

    axes[1].set_title("Top View Variable Map and Load Locations")
    axes[1].set_xlabel("x [in]")
    axes[1].set_ylabel("z [in]")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def save_best_design_plots(
    output_dir: Path,
    best_evaluation: DesignEvaluation,
    material: Material,
    load_cases: list[Any],
    stations: int,
) -> Path:
    best_plot_dir = output_dir / "best_design"
    best_plot_dir.mkdir(parents=True, exist_ok=True)

    x_in = build_x_grid(best_evaluation.geometry.span_in, stations=stations)
    plot_geometry(best_evaluation.geometry, best_plot_dir, x_in)

    for load_case in load_cases:
        result = analyze_load_case(
            geometry=best_evaluation.geometry,
            material=material,
            load_case=load_case,
            stations=stations,
        )
        plot_load_case(result, load_case, best_plot_dir)

    return best_plot_dir


def run_search(
    bounds: DesignVariableBounds,
    span_in: float,
    total_length_in: float,
    material: Material,
    load_cases: list[Any],
    constraint_config: ConstraintConfig,
    durability_config: DurabilityConfig,
    search_config: SearchConfig,
    stations: int,
) -> list[DesignEvaluation]:
    rng = np.random.default_rng(search_config.seed)
    evaluations: list[DesignEvaluation] = []
    evaluation_id = 1

    for sample in latin_hypercube_samples(bounds, search_config.initial_samples, rng):
        geometry = build_geometry_from_variables(
            sample,
            span_in,
            total_length_in,
            mirror_profile=search_config.mirror_profile,
        )
        evaluations.append(
                    evaluate_design(
                        evaluation_id=evaluation_id,
                        geometry=geometry,
                        material=material,
                        load_cases=load_cases,
                        constraint_config=constraint_config,
                        durability_config=durability_config,
                        search_config=search_config,
                        stations=stations,
                    )
                )
        evaluation_id += 1

    for refinement_round in range(search_config.refinement_rounds):
        elites = choose_elites(evaluations, search_config.elite_count)
        shrink_factor = 0.18 / (refinement_round + 1.0)
        refinement_samples = local_refinement_samples(
            elite_geometries=elites,
            bounds=bounds,
            samples_per_elite=search_config.local_samples_per_elite,
            shrink_factor=shrink_factor,
            rng=rng,
        )

        for sample in refinement_samples:
            geometry = build_geometry_from_variables(
                sample,
                span_in,
                total_length_in,
                mirror_profile=search_config.mirror_profile,
            )
            evaluations.append(
                    evaluate_design(
                        evaluation_id=evaluation_id,
                        geometry=geometry,
                        material=material,
                        load_cases=load_cases,
                        constraint_config=constraint_config,
                        durability_config=durability_config,
                        search_config=search_config,
                        stations=stations,
                    )
                )
            evaluation_id += 1

        feasible_count = sum(evaluation.feasible for evaluation in evaluations)
        if feasible_count >= search_config.min_feasible_designs:
            break

    return evaluations


def select_best_evaluation(evaluations: list[DesignEvaluation]) -> DesignEvaluation:
    ordered = sorted(
        evaluations,
        key=lambda evaluation: (
            not evaluation.feasible,
            evaluation.objective,
            evaluation.weight_lbf,
        ),
    )
    return ordered[0]


def build_bounds_from_args(args: argparse.Namespace) -> DesignVariableBounds:
    return DesignVariableBounds(
        left_width_in=(args.min_width_in, args.max_width_in),
        mid_width_in=(args.min_width_in, args.max_width_in),
        right_width_in=(args.min_width_in, args.max_width_in),
        left_height_in=(args.min_height_in, args.max_height_in),
        mid_height_in=(args.min_height_in, args.max_height_in),
        right_height_in=(args.min_height_in, args.max_height_in),
        wall_thickness_in=(args.min_wall_thickness_in, args.max_wall_thickness_in),
        left_web_opening_ratio=(args.min_web_opening_ratio, args.max_web_opening_ratio),
        mid_web_opening_ratio=(args.min_web_opening_ratio, args.max_web_opening_ratio),
        right_web_opening_ratio=(args.min_web_opening_ratio, args.max_web_opening_ratio),
    )


def main() -> None:
    material_defaults = default_material()

    parser = argparse.ArgumentParser(
        description="Run a constrained design-study and lightweight optimization for the MEEN 305 beam."
    )
    parser.add_argument("--team-number", type=int, default=1)
    parser.add_argument("--output-dir", default="designs/active_runs/optimization_run")
    parser.add_argument("--span-in", type=float, default=8.0)
    parser.add_argument("--total-length-in", type=float, default=9.0)
    parser.add_argument("--stations", type=int, default=801)

    parser.add_argument("--min-width-in", type=float, default=0.35)
    parser.add_argument("--max-width-in", type=float, default=1.60)
    parser.add_argument("--min-height-in", type=float, default=0.35)
    parser.add_argument("--max-height-in", type=float, default=2.20)
    parser.add_argument("--min-wall-thickness-in", type=float, default=0.06)
    parser.add_argument("--max-wall-thickness-in", type=float, default=0.20)
    parser.add_argument("--min-web-opening-ratio", type=float, default=0.0)
    parser.add_argument("--max-web-opening-ratio", type=float, default=0.90)

    parser.add_argument("--load1-lbf", type=float, default=5.0)
    parser.add_argument("--load1-location-in", type=float, default=4.0)
    parser.add_argument("--load2-lbf", type=float, default=None)
    parser.add_argument("--load2-location-in", type=float, default=None)

    parser.add_argument(
        "--material",
        choices=list(KNOWN_MATERIALS.keys()),
        default="PLA",
        help="Select a preconfigured FDM material. Individual property flags below override the selection.",
    )
    parser.add_argument("--elastic-modulus-psi", type=float, default=None)
    parser.add_argument("--allowable-stress-psi", type=float, default=None)
    parser.add_argument("--weight-density-lbf-per-in3", type=float, default=None)
    parser.add_argument("--orientation-factor", type=float, default=None)
    parser.add_argument("--infill-factor", type=float, default=None)

    parser.add_argument("--min-factor-of-safety", type=float, default=1.5)
    parser.add_argument("--max-deflection-in", type=float, default=None)

    parser.add_argument("--durability-min-web-ligament-in", type=float, default=0.080)
    parser.add_argument("--durability-min-shell-area-ratio", type=float, default=0.180)
    parser.add_argument("--durability-max-height-ratio", type=float, default=2.40)
    parser.add_argument("--durability-max-width-ratio", type=float, default=2.40)
    parser.add_argument("--durability-max-dim-slope-in-per-in", type=float, default=0.25)
    parser.add_argument("--durability-stress-concentration-limit", type=float, default=10.0)

    parser.add_argument("--initial-samples", type=int, default=240)
    parser.add_argument("--refinement-rounds", type=int, default=3)
    parser.add_argument("--elite-count", type=int, default=12)
    parser.add_argument("--local-samples-per-elite", type=int, default=18)
    parser.add_argument("--min-feasible-designs", type=int, default=20)
    parser.add_argument("--excess-fos-weight", type=float, default=0.02)
    parser.add_argument("--underutilization-weight", type=float, default=0.12)
    parser.add_argument("--uniformity-weight", type=float, default=0.0)
    parser.add_argument("--symmetry-weight", type=float, default=0.0)
    parser.add_argument("--smoothness-weight", type=float, default=0.0)
    parser.add_argument("--envelope-stress-floor-ratio", type=float, default=0.15)
    parser.add_argument("--uniformity-case", choices=["all", "load1", "load2"], default="all")
    parser.add_argument("--mirror-profile", action="store_true")
    parser.add_argument("--seed", type=int, default=305)
    args = parser.parse_args()

    base = KNOWN_MATERIALS[args.material]
    material = Material(
        name=args.material,
        elastic_modulus_psi=args.elastic_modulus_psi if args.elastic_modulus_psi is not None else base.elastic_modulus_psi,
        allowable_stress_psi=args.allowable_stress_psi if args.allowable_stress_psi is not None else base.allowable_stress_psi,
        weight_density_lbf_per_in3=args.weight_density_lbf_per_in3 if args.weight_density_lbf_per_in3 is not None else base.weight_density_lbf_per_in3,
        orientation_factor=args.orientation_factor if args.orientation_factor is not None else base.orientation_factor,
        infill_factor=args.infill_factor if args.infill_factor is not None else base.infill_factor,
    )
    load_cases = build_load_cases(
        team_number=args.team_number,
        load1_lbf=args.load1_lbf,
        load1_location_in=args.load1_location_in,
        load2_lbf=args.load2_lbf,
        load2_location_in=args.load2_location_in,
    )
    bounds = build_bounds_from_args(args)
    constraint_config = ConstraintConfig(
        min_factor_of_safety=args.min_factor_of_safety,
        max_deflection_in=args.max_deflection_in,
    )
    durability_config = DurabilityConfig(
        min_web_ligament_in=args.durability_min_web_ligament_in,
        min_shell_area_ratio=args.durability_min_shell_area_ratio,
        max_height_ratio=args.durability_max_height_ratio,
        max_width_ratio=args.durability_max_width_ratio,
        max_dim_slope_in_per_in=args.durability_max_dim_slope_in_per_in,
        stress_concentration_limit=args.durability_stress_concentration_limit,
    )
    search_config = SearchConfig(
        initial_samples=args.initial_samples,
        refinement_rounds=args.refinement_rounds,
        elite_count=args.elite_count,
        local_samples_per_elite=args.local_samples_per_elite,
        min_feasible_designs=args.min_feasible_designs,
        excess_fos_weight=args.excess_fos_weight,
        underutilization_weight=args.underutilization_weight,
        uniformity_weight=args.uniformity_weight,
        symmetry_weight=args.symmetry_weight,
        smoothness_weight=args.smoothness_weight,
        envelope_stress_floor_ratio=args.envelope_stress_floor_ratio,
        uniformity_case=args.uniformity_case,
        mirror_profile=args.mirror_profile,
        seed=args.seed,
    )

    evaluations = run_search(
        bounds=bounds,
        span_in=args.span_in,
        total_length_in=args.total_length_in,
        material=material,
        load_cases=load_cases,
        constraint_config=constraint_config,
        durability_config=durability_config,
        search_config=search_config,
        stations=args.stations,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    feasible_evaluations = [evaluation for evaluation in evaluations if evaluation.feasible]
    best_evaluation = select_best_evaluation(evaluations)

    export_design_study_csv(evaluations, output_dir / "design_study.csv")
    save_best_design_json(output_dir, best_evaluation, search_config, constraint_config, durability_config)

    best_plot_dir = save_best_design_plots(
        output_dir=output_dir,
        best_evaluation=best_evaluation,
        material=material,
        load_cases=load_cases,
        stations=args.stations,
    )

    parameter_map_path = output_dir / "beam_parameter_map.png"
    plot_parameter_map(parameter_map_path, best_evaluation.geometry, load_cases)

    write_markdown_report(
        output_dir=output_dir,
        best_evaluation=best_evaluation,
        feasible_evaluations=feasible_evaluations,
        total_evaluations=len(evaluations),
        search_config=search_config,
        constraint_config=constraint_config,
        material=material,
        parameter_map_path=parameter_map_path,
        best_plot_dir=best_plot_dir,
    )
    write_latex_report(
        output_dir=output_dir,
        best_evaluation=best_evaluation,
        feasible_evaluations=feasible_evaluations,
        total_evaluations=len(evaluations),
        search_config=search_config,
        constraint_config=constraint_config,
        material=material,
        parameter_map_path=parameter_map_path,
        best_plot_dir=best_plot_dir,
    )

    print("Optimization run complete.")
    print(f"  Designs evaluated: {len(evaluations)}")
    print(f"  Feasible designs: {len(feasible_evaluations)}")
    print(f"  Best design feasible: {best_evaluation.feasible}")
    print(f"  Best design weight: {best_evaluation.weight_lbf:.5f} lbf")
    print(f"  Best design minimum FoS: {best_evaluation.min_factor_of_safety:.3f}")
    print(f"  Best design maximum deflection: {best_evaluation.max_deflection_in:.5f} in")
    print(f"  Outputs written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
