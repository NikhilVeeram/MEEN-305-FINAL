from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


UPRIGHT_ORIENTATION = "upright"
SIDE_ORIENTATION = "side"


@dataclass(frozen=True)
class Material:
    name: str
    elastic_modulus_psi: float
    allowable_stress_psi: float
    weight_density_lbf_per_in3: float
    orientation_factor: float = 1.0
    infill_factor: float = 1.0

    @property
    def effective_modulus_psi(self) -> float:
        return (
            self.elastic_modulus_psi
            * self.orientation_factor
            * self.infill_factor
        )

    @property
    def effective_allowable_stress_psi(self) -> float:
        return (
            self.allowable_stress_psi
            * self.orientation_factor
            * self.infill_factor
        )


# Nominal FDM material properties for Creality K1 (0.4 mm nozzle, ~40% rectilinear infill).
# orientation_factor (0.65-0.75): FDM parts are weaker perpendicular to the print
# plane because interlayer bond strength is ~30-35% below bulk tensile strength.
# infill_factor (0.85-0.90): less-than-100% infill reduces effective stiffness/strength.
# Both factors are applied as multipliers to the nominal isotropic properties.
KNOWN_MATERIALS: dict[str, "Material"] = {
    "PLA": Material(
        name="PLA",
        elastic_modulus_psi=500_000,
        allowable_stress_psi=4_000,
        weight_density_lbf_per_in3=0.045,
        orientation_factor=0.70,
        infill_factor=0.85,
    ),
    "ASA": Material(
        name="ASA",
        elastic_modulus_psi=380_000,
        allowable_stress_psi=3_600,
        weight_density_lbf_per_in3=0.043,
        orientation_factor=0.65,
        infill_factor=0.85,
    ),
    "PETG": Material(
        name="PETG",
        elastic_modulus_psi=290_000,
        allowable_stress_psi=3_500,
        weight_density_lbf_per_in3=0.046,
        orientation_factor=0.72,
        infill_factor=0.85,
    ),
    # TPU is very flexible (E ~10x lower than PLA) and is listed for completeness;
    # it is a poor structural choice for a stiffness-governed beam.
    "TPU": Material(
        name="TPU",
        elastic_modulus_psi=10_000,
        allowable_stress_psi=2_500,
        weight_density_lbf_per_in3=0.043,
        orientation_factor=0.75,
        infill_factor=0.90,
    ),
}


@dataclass(frozen=True)
class LoadCase:
    name: str
    load_lbf: float
    location_in: float
    orientation: str = UPRIGHT_ORIENTATION


# Engineering judgment lower bounds applied in validate(), independent of optimizer search bounds.
# An idealized stress analysis would permit arbitrarily thin walls and even zero cross-section at
# supports (moment = 0 there), but those geometries are physically unrealizable on an FDM printer.
_MIN_PRINTABLE_WALL_IN: float = 0.040   # ~1 mm; fewer than 2 perimeters at 0.4 mm nozzle is unreliable
_MIN_CROSS_SECTION_DIM_IN: float = 0.150  # ~3.8 mm; beam must retain finite section at every station


@dataclass(frozen=True)
class TaperedRectangularTube:
    span_in: float
    total_length_in: float
    left_width_in: float
    mid_width_in: float
    right_width_in: float
    left_height_in: float
    mid_height_in: float
    right_height_in: float
    wall_thickness_in: float
    left_web_opening_ratio: float = 0.0
    mid_web_opening_ratio: float = 0.0
    right_web_opening_ratio: float = 0.0

    def validate(self) -> None:
        if self.total_length_in < self.span_in:
            raise ValueError("Total length must be at least as large as the support span.")

        if min(
            self.left_width_in,
            self.mid_width_in,
            self.right_width_in,
            self.left_height_in,
            self.mid_height_in,
            self.right_height_in,
            self.wall_thickness_in,
        ) <= 0.0:
            raise ValueError("All geometry dimensions must be positive.")

        # Engineering judgment: even though idealized bending theory allows the section
        # to vanish at simply-supported ends (moment = 0 there), a real printed beam
        # must have a finite, printable cross-section at every station, including at the
        # supports where shear must still be transferred.
        if min(
            self.left_width_in, self.mid_width_in, self.right_width_in,
            self.left_height_in, self.mid_height_in, self.right_height_in,
        ) < _MIN_CROSS_SECTION_DIM_IN:
            raise ValueError(
                f"Cross-section dimension is below the engineering minimum of "
                f"{_MIN_CROSS_SECTION_DIM_IN:.3f} in. "
                "The beam must have a printable cross-section at every station."
            )

        # Engineering judgment: wall thickness must be printable on a 0.4 mm nozzle.
        # A purely stress-based analysis would permit paper-thin walls wherever stress
        # is low, but those walls are physically unrealizable.
        if self.wall_thickness_in < _MIN_PRINTABLE_WALL_IN:
            raise ValueError(
                f"Wall thickness {self.wall_thickness_in:.4f} in is below the FDM printability "
                f"minimum of {_MIN_PRINTABLE_WALL_IN:.4f} in (approx. 1 mm / 2 nozzle widths)."
            )

        if not all(
            0.0 <= ratio < 0.95
            for ratio in (
                self.left_web_opening_ratio,
                self.mid_web_opening_ratio,
                self.right_web_opening_ratio,
            )
        ):
            raise ValueError("Web opening ratios must stay between 0.0 and 0.95.")

        if min(self.left_width_in, self.mid_width_in, self.right_width_in) <= 2.0 * self.wall_thickness_in:
            raise ValueError("Wall thickness is too large for at least one tube width.")

        if min(self.left_height_in, self.mid_height_in, self.right_height_in) <= 2.0 * self.wall_thickness_in:
            raise ValueError("Wall thickness is too large for at least one tube height.")

        minimum_remaining_ligament = np.min(
            0.5
            * (1.0 - np.array(
                [
                    self.left_web_opening_ratio,
                    self.mid_web_opening_ratio,
                    self.right_web_opening_ratio,
                ]
            ))
            * np.array(
                [
                    self.left_height_in,
                    self.mid_height_in,
                    self.right_height_in,
                ]
            )
        )
        if minimum_remaining_ligament <= self.wall_thickness_in:
            raise ValueError(
                "Web openings are too large; keep a remaining ligament larger than the wall thickness."
            )

    def _interpolate_profile(
        self,
        x: np.ndarray,
        left_value: float,
        mid_value: float,
        right_value: float,
    ) -> np.ndarray:
        return np.interp(
            np.asarray(x, dtype=float),
            [0.0, self.span_in / 2.0, self.span_in],
            [left_value, mid_value, right_value],
        )

    def height_profile(self, x: np.ndarray) -> np.ndarray:
        return self._interpolate_profile(
            x,
            self.left_height_in,
            self.mid_height_in,
            self.right_height_in,
        )

    def width_profile(self, x: np.ndarray) -> np.ndarray:
        return self._interpolate_profile(
            x,
            self.left_width_in,
            self.mid_width_in,
            self.right_width_in,
        )

    def web_opening_ratio_profile(self, x: np.ndarray) -> np.ndarray:
        return self._interpolate_profile(
            x,
            self.left_web_opening_ratio,
            self.mid_web_opening_ratio,
            self.right_web_opening_ratio,
        )

    def _validate_orientation(self, orientation: str) -> None:
        if orientation not in {UPRIGHT_ORIENTATION, SIDE_ORIENTATION}:
            raise ValueError(f"Unsupported orientation '{orientation}'.")

    def outer_vertical_dimension(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        self._validate_orientation(orientation)
        if orientation == UPRIGHT_ORIENTATION:
            return self.height_profile(x)
        return self.width_profile(x)

    def outer_lateral_dimension(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        self._validate_orientation(orientation)
        if orientation == UPRIGHT_ORIENTATION:
            return self.width_profile(x)
        return self.height_profile(x)

    def inner_height_profile(self, x: np.ndarray) -> np.ndarray:
        return self.height_profile(x) - 2.0 * self.wall_thickness_in

    def inner_width_profile(self, x: np.ndarray) -> np.ndarray:
        return self.width_profile(x) - 2.0 * self.wall_thickness_in

    def inner_vertical_dimension(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        if orientation == UPRIGHT_ORIENTATION:
            return self.inner_height_profile(x)
        if orientation == SIDE_ORIENTATION:
            return self.inner_width_profile(x)
        self._validate_orientation(orientation)
        return np.asarray(x, dtype=float)

    def inner_lateral_dimension(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        if orientation == UPRIGHT_ORIENTATION:
            return self.inner_width_profile(x)
        if orientation == SIDE_ORIENTATION:
            return self.inner_height_profile(x)
        self._validate_orientation(orientation)
        return np.asarray(x, dtype=float)

    def area(self, x: np.ndarray) -> np.ndarray:
        b = self.width_profile(x)
        h = self.height_profile(x)
        hi = self.inner_height_profile(x)
        flange_area = 2.0 * b * self.wall_thickness_in
        web_area = 2.0 * self.wall_thickness_in * hi
        remaining_web_fraction = 1.0 - self.web_opening_ratio_profile(x)
        return flange_area + remaining_web_fraction * web_area

    def second_moment_bending(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        lateral = self.outer_lateral_dimension(x, orientation)
        vertical = self.outer_vertical_dimension(x, orientation)
        inner_lateral = self.inner_lateral_dimension(x, orientation)
        inner_vertical = self.inner_vertical_dimension(x, orientation)
        intact_tube_second_moment = (lateral * vertical**3 - inner_lateral * inner_vertical**3) / 12.0
        opening_height = self.web_opening_ratio_profile(x) * inner_vertical
        web_opening_second_moment = 2.0 * self.wall_thickness_in * opening_height**3 / 12.0
        return intact_tube_second_moment - web_opening_second_moment

    def section_modulus(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        vertical = self.outer_vertical_dimension(x, orientation)
        return self.second_moment_bending(x, orientation) / (vertical / 2.0)

    def web_shear_area(self, x: np.ndarray, orientation: str = UPRIGHT_ORIENTATION) -> np.ndarray:
        clear_vertical = self.inner_vertical_dimension(x, orientation)
        remaining_web_fraction = 1.0 - self.web_opening_ratio_profile(x)
        return 2.0 * self.wall_thickness_in * clear_vertical * remaining_web_fraction


@dataclass
class AnalysisResult:
    x_in: np.ndarray
    orientation: str
    reaction_a_lbf: float
    reaction_b_lbf: float
    shear_lbf: np.ndarray
    moment_lbf_in: np.ndarray
    area_in2: np.ndarray
    second_moment_bending_in4: np.ndarray
    section_modulus_in3: np.ndarray
    bending_stress_psi: np.ndarray
    shear_stress_psi: np.ndarray
    von_mises_psi: np.ndarray
    factor_of_safety: np.ndarray
    slope_rad: np.ndarray
    deflection_in: np.ndarray
    weight_lbf: float
    min_factor_of_safety: float
    min_factor_of_safety_x_in: float
    max_von_mises_psi: float
    max_von_mises_x_in: float
    max_deflection_in: float
    max_deflection_x_in: float


def build_x_grid(span_in: float, stations: int = 801) -> np.ndarray:
    return np.linspace(0.0, span_in, stations)


def solve_reactions(span_in: float, load_lbf: float, location_in: float) -> tuple[float, float]:
    reaction_a = load_lbf * (span_in - location_in) / span_in
    reaction_b = load_lbf * location_in / span_in
    return reaction_a, reaction_b


def shear_and_moment(
    x_in: np.ndarray,
    span_in: float,
    load_lbf: float,
    location_in: float,
) -> tuple[float, float, np.ndarray, np.ndarray]:
    reaction_a, reaction_b = solve_reactions(span_in, load_lbf, location_in)
    shear = np.where(x_in < location_in, reaction_a, reaction_a - load_lbf)
    moment = np.where(
        x_in < location_in,
        reaction_a * x_in,
        reaction_a * x_in - load_lbf * (x_in - location_in),
    )
    return reaction_a, reaction_b, shear, moment


def integrate_deflection(
    x_in: np.ndarray,
    moment_lbf_in: np.ndarray,
    elastic_modulus_psi: float,
    second_moment_bending_in4: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    dx = x_in[1] - x_in[0]
    curvature = moment_lbf_in / (elastic_modulus_psi * second_moment_bending_in4)

    theta_raw = np.zeros_like(curvature)
    theta_raw[1:] = np.cumsum(0.5 * (curvature[:-1] + curvature[1:]) * dx)

    deflection_raw = np.zeros_like(curvature)
    deflection_raw[1:] = np.cumsum(0.5 * (theta_raw[:-1] + theta_raw[1:]) * dx)

    correction = deflection_raw[-1] / x_in[-1]
    deflection = deflection_raw - correction * x_in
    slope = np.gradient(deflection, dx)
    return slope, deflection


def analyze_load_case(
    geometry: TaperedRectangularTube,
    material: Material,
    load_case: LoadCase,
    stations: int = 801,
) -> AnalysisResult:
    geometry.validate()
    if not 0.0 < load_case.location_in < geometry.span_in:
        raise ValueError("Load location must lie strictly between the supports.")

    x_in = build_x_grid(geometry.span_in, stations=stations)
    reaction_a, reaction_b, shear_lbf, moment_lbf_in = shear_and_moment(
        x_in=x_in,
        span_in=geometry.span_in,
        load_lbf=load_case.load_lbf,
        location_in=load_case.location_in,
    )

    area_in2 = geometry.area(x_in)
    second_moment_bending_in4 = geometry.second_moment_bending(x_in, load_case.orientation)
    section_modulus_in3 = geometry.section_modulus(x_in, load_case.orientation)

    bending_stress_psi = np.abs(moment_lbf_in) / section_modulus_in3

    shear_area_in2 = np.maximum(geometry.web_shear_area(x_in, load_case.orientation), 1.0e-9)
    shear_stress_psi = np.abs(shear_lbf) / shear_area_in2

    von_mises_psi = np.sqrt(bending_stress_psi**2 + 3.0 * shear_stress_psi**2)
    factor_of_safety = np.divide(
        material.effective_allowable_stress_psi,
        von_mises_psi,
        out=np.full_like(von_mises_psi, np.inf),
        where=von_mises_psi > 1.0e-12,
    )

    slope_rad, deflection_in = integrate_deflection(
        x_in=x_in,
        moment_lbf_in=moment_lbf_in,
        elastic_modulus_psi=material.effective_modulus_psi,
        second_moment_bending_in4=second_moment_bending_in4,
    )

    # Beam weight is computed for reporting purposes only.
    # Self-weight is NEGLECTED in the shear, moment, stress, and deflection calculations above.
    # Justification: the optimized beam weighs ~0.026 lbf while the applied loads total 8 lbf
    # (5 lbf LC1 + 3 lbf LC2).  Self-weight is < 0.4 % of applied load — well below the 5 %
    # threshold commonly accepted for simply-supported beams.  Including it as a distributed
    # load would increase midspan stress by less than 0.4 %, which is negligible relative to
    # the FoS = 1.5 safety margin already built into the design.
    volume_in3 = np.trapezoid(area_in2, x_in)
    weight_lbf = volume_in3 * material.weight_density_lbf_per_in3

    min_fos_index = int(np.argmin(factor_of_safety))
    max_vm_index = int(np.argmax(von_mises_psi))
    max_deflection_index = int(np.argmax(np.abs(deflection_in)))

    return AnalysisResult(
        x_in=x_in,
        orientation=load_case.orientation,
        reaction_a_lbf=reaction_a,
        reaction_b_lbf=reaction_b,
        shear_lbf=shear_lbf,
        moment_lbf_in=moment_lbf_in,
        area_in2=area_in2,
        second_moment_bending_in4=second_moment_bending_in4,
        section_modulus_in3=section_modulus_in3,
        bending_stress_psi=bending_stress_psi,
        shear_stress_psi=shear_stress_psi,
        von_mises_psi=von_mises_psi,
        factor_of_safety=factor_of_safety,
        slope_rad=slope_rad,
        deflection_in=deflection_in,
        weight_lbf=weight_lbf,
        min_factor_of_safety=float(factor_of_safety[min_fos_index]),
        min_factor_of_safety_x_in=float(x_in[min_fos_index]),
        max_von_mises_psi=float(von_mises_psi[max_vm_index]),
        max_von_mises_x_in=float(x_in[max_vm_index]),
        max_deflection_in=float(np.abs(deflection_in[max_deflection_index])),
        max_deflection_x_in=float(x_in[max_deflection_index]),
    )


def orientation_label(orientation: str) -> str:
    if orientation == UPRIGHT_ORIENTATION:
        return "upright"
    if orientation == SIDE_ORIENTATION:
        return "rotated 90 deg"
    return orientation


def add_profile_annotations(ax: plt.Axes, x_positions: list[float], dimensions_in: list[float]) -> None:
    offset = 0.05 * max(dimensions_in)
    labels = ["left", "mid", "right"]
    for x_position, dimension_in, label in zip(x_positions, dimensions_in, labels, strict=True):
        ax.axvline(x_position, color="0.75", linestyle=":", linewidth=1.0)
        ax.text(
            x_position,
            dimension_in / 2.0 + offset,
            f"{label}: {dimension_in:.3f} in",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def plot_outer_dimension_views(
    geometry: TaperedRectangularTube,
    output_dir: Path,
    x_in: np.ndarray,
) -> None:
    outer_height = geometry.height_profile(x_in)
    outer_width = geometry.width_profile(x_in)
    opening_ratio = geometry.web_opening_ratio_profile(x_in)
    x_positions = [0.0, geometry.span_in / 2.0, geometry.span_in]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    axes[0].fill_between(x_in, -outer_height / 2.0, outer_height / 2.0, color="#c9d8eb", alpha=0.8)
    axes[0].plot(x_in, outer_height / 2.0, color="tab:blue", linewidth=2.0)
    axes[0].plot(x_in, -outer_height / 2.0, color="tab:blue", linewidth=2.0)
    add_profile_annotations(
        axes[0],
        x_positions,
        [geometry.left_height_in, geometry.mid_height_in, geometry.right_height_in],
    )
    axes[0].set_title("Front View Outer Dimensions (x-y)")
    axes[0].set_xlabel("x [in]")
    axes[0].set_ylabel("y [in]")
    axes[0].grid(True, alpha=0.3)

    axes[1].fill_between(x_in, -outer_width / 2.0, outer_width / 2.0, color="#f5d8b8", alpha=0.8)
    axes[1].plot(x_in, outer_width / 2.0, color="tab:orange", linewidth=2.0)
    axes[1].plot(x_in, -outer_width / 2.0, color="tab:orange", linewidth=2.0)
    add_profile_annotations(
        axes[1],
        x_positions,
        [geometry.left_width_in, geometry.mid_width_in, geometry.right_width_in],
    )
    axes[1].set_title("Top View Outer Dimensions (x-z)")
    axes[1].set_xlabel("x [in]")
    axes[1].set_ylabel("z [in]")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(x_in, opening_ratio, color="tab:green", linewidth=2.0)
    add_profile_annotations(
        axes[2],
        x_positions,
        [
            geometry.left_web_opening_ratio,
            geometry.mid_web_opening_ratio,
            geometry.right_web_opening_ratio,
        ],
    )
    axes[2].set_title("Lightening Opening Ratio")
    axes[2].set_xlabel("x [in]")
    axes[2].set_ylabel("opening ratio [-]")
    axes[2].set_ylim(-0.02, 1.02)
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_dir / "outer_dimension_views.png", dpi=200)
    plt.close(fig)


def plot_section_properties(
    geometry: TaperedRectangularTube,
    output_dir: Path,
    x_in: np.ndarray,
) -> None:
    second_moment_upright = geometry.second_moment_bending(x_in, UPRIGHT_ORIENTATION)
    second_moment_side = geometry.second_moment_bending(x_in, SIDE_ORIENTATION)
    section_modulus_upright = geometry.section_modulus(x_in, UPRIGHT_ORIENTATION)
    section_modulus_side = geometry.section_modulus(x_in, SIDE_ORIENTATION)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    axes[0].plot(x_in, second_moment_upright, label="upright")
    axes[0].plot(x_in, second_moment_side, label="rotated 90 deg")
    axes[0].set_title("Active Second Moment of Area")
    axes[0].set_xlabel("x [in]")
    axes[0].set_ylabel("I [in^4]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(x_in, section_modulus_upright, label="upright")
    axes[1].plot(x_in, section_modulus_side, label="rotated 90 deg")
    axes[1].set_title("Active Section Modulus")
    axes[1].set_xlabel("x [in]")
    axes[1].set_ylabel("S [in^3]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(output_dir / "geometry_properties.png", dpi=200)
    plt.close(fig)


def plot_geometry(
    geometry: TaperedRectangularTube,
    output_dir: Path,
    x_in: np.ndarray,
) -> None:
    plot_outer_dimension_views(geometry, output_dir, x_in)
    plot_section_properties(geometry, output_dir, x_in)


def plot_load_case(result: AnalysisResult, load_case: LoadCase, output_dir: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(12, 12))
    prefix = f"{load_case.name} ({orientation_label(load_case.orientation)})"

    axes[0, 0].plot(result.x_in, result.shear_lbf)
    axes[0, 0].set_title(f"{prefix}: Shear")
    axes[0, 0].set_xlabel("x [in]")
    axes[0, 0].set_ylabel("V [lbf]")
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(result.x_in, result.moment_lbf_in)
    axes[0, 1].set_title(f"{prefix}: Moment")
    axes[0, 1].set_xlabel("x [in]")
    axes[0, 1].set_ylabel("M [lbf-in]")
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(result.x_in, result.von_mises_psi)
    axes[1, 0].set_title(f"{prefix}: von Mises Stress")
    axes[1, 0].set_xlabel("x [in]")
    axes[1, 0].set_ylabel("sigma_vm [psi]")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(result.x_in, result.factor_of_safety)
    axes[1, 1].axhline(1.5, color="tab:red", linestyle="--", linewidth=1.0)
    axes[1, 1].set_title(f"{prefix}: Factor of Safety")
    axes[1, 1].set_xlabel("x [in]")
    axes[1, 1].set_ylabel("FoS [-]")
    axes[1, 1].grid(True, alpha=0.3)

    axes[2, 0].plot(result.x_in, result.slope_rad)
    axes[2, 0].set_title(f"{prefix}: Slope")
    axes[2, 0].set_xlabel("x [in]")
    axes[2, 0].set_ylabel("theta [rad]")
    axes[2, 0].grid(True, alpha=0.3)

    axes[2, 1].plot(result.x_in, result.deflection_in)
    axes[2, 1].set_title(f"{prefix}: Deflection")
    axes[2, 1].set_xlabel("x [in]")
    axes[2, 1].set_ylabel("v [in]")
    axes[2, 1].grid(True, alpha=0.3)

    fig.tight_layout()
    file_name = load_case.name.lower().replace(" ", "_") + "_results.png"
    fig.savefig(output_dir / file_name, dpi=200)
    plt.close(fig)


def print_summary(result: AnalysisResult, load_case: LoadCase) -> None:
    print(f"\n{load_case.name} ({orientation_label(load_case.orientation)})")
    print(f"  Applied load: {load_case.load_lbf:.3f} lbf at x = {load_case.location_in:.3f} in")
    print(f"  Reaction A: {result.reaction_a_lbf:.3f} lbf")
    print(f"  Reaction B: {result.reaction_b_lbf:.3f} lbf")
    print(
        "  Max von Mises: "
        f"{result.max_von_mises_psi:.1f} psi at x = {result.max_von_mises_x_in:.3f} in"
    )
    print(
        "  Min FoS: "
        f"{result.min_factor_of_safety:.3f} at x = {result.min_factor_of_safety_x_in:.3f} in"
    )
    print(
        "  Max deflection: "
        f"{result.max_deflection_in:.5f} in at x = {result.max_deflection_x_in:.3f} in"
    )
    print(f"  Beam weight: {result.weight_lbf:.4f} lbf")


def default_material() -> Material:
    return KNOWN_MATERIALS["PLA"]


def default_geometry() -> TaperedRectangularTube:
    return TaperedRectangularTube(
        span_in=8.0,
        total_length_in=9.0,
        left_width_in=1.10,
        mid_width_in=1.10,
        right_width_in=1.10,
        left_height_in=0.85,
        mid_height_in=1.80,
        right_height_in=0.85,
        wall_thickness_in=0.12,
        left_web_opening_ratio=0.0,
        mid_web_opening_ratio=0.20,
        right_web_opening_ratio=0.0,
    )


def build_geometry_from_args(args: argparse.Namespace) -> tuple[TaperedRectangularTube, str]:
    sample_geometry = default_geometry()
    if args.geometry_mode == "sample":
        return sample_geometry, "sample"

    uniform_width_in = args.outer_width_in
    left_width_in = (
        args.left_width_in
        if args.left_width_in is not None
        else uniform_width_in
        if uniform_width_in is not None
        else sample_geometry.left_width_in
    )
    mid_width_in = (
        args.mid_width_in
        if args.mid_width_in is not None
        else uniform_width_in
        if uniform_width_in is not None
        else sample_geometry.mid_width_in
    )
    right_width_in = (
        args.right_width_in
        if args.right_width_in is not None
        else uniform_width_in
        if uniform_width_in is not None
        else sample_geometry.right_width_in
    )

    return (
        TaperedRectangularTube(
            span_in=args.span_in,
            total_length_in=args.total_length_in,
            left_width_in=left_width_in,
            mid_width_in=mid_width_in,
            right_width_in=right_width_in,
            left_height_in=(
                args.left_height_in
                if args.left_height_in is not None
                else sample_geometry.left_height_in
            ),
            mid_height_in=(
                args.mid_height_in
                if args.mid_height_in is not None
                else sample_geometry.mid_height_in
            ),
            right_height_in=(
                args.right_height_in
                if args.right_height_in is not None
                else sample_geometry.right_height_in
            ),
            wall_thickness_in=(
                args.wall_thickness_in
                if args.wall_thickness_in is not None
                else sample_geometry.wall_thickness_in
            ),
            left_web_opening_ratio=(
                args.left_web_opening_ratio
                if args.left_web_opening_ratio is not None
                else sample_geometry.left_web_opening_ratio
            ),
            mid_web_opening_ratio=(
                args.mid_web_opening_ratio
                if args.mid_web_opening_ratio is not None
                else sample_geometry.mid_web_opening_ratio
            ),
            right_web_opening_ratio=(
                args.right_web_opening_ratio
                if args.right_web_opening_ratio is not None
                else sample_geometry.right_web_opening_ratio
            ),
        ),
        "custom",
    )


def build_load_cases(
    team_number: int,
    load1_lbf: float,
    load1_location_in: float,
    load2_lbf: float | None,
    load2_location_in: float | None,
) -> list[LoadCase]:
    project_load2_lbf = 2.0 + float(team_number)
    project_load2_location_in = 2.0 + float(team_number) / 2.0
    return [
        LoadCase(
            name="Load Case 1",
            load_lbf=load1_lbf,
            location_in=load1_location_in,
            orientation=UPRIGHT_ORIENTATION,
        ),
        LoadCase(
            name="Load Case 2",
            load_lbf=project_load2_lbf if load2_lbf is None else load2_lbf,
            location_in=project_load2_location_in if load2_location_in is None else load2_location_in,
            orientation=SIDE_ORIENTATION,
        ),
    ]


def main() -> None:
    sample_geometry = default_geometry()
    sample_material = default_material()

    parser = argparse.ArgumentParser(
        description="Analyze a tapered rectangular tube beam for the MEEN 305 project."
    )
    parser.add_argument("--team-number", type=int, default=1)
    parser.add_argument("--stations", type=int, default=801)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--geometry-mode", choices=["sample", "custom"], default="sample")
    parser.add_argument("--span-in", type=float, default=sample_geometry.span_in)
    parser.add_argument("--total-length-in", type=float, default=sample_geometry.total_length_in)
    parser.add_argument(
        "--outer-width-in",
        type=float,
        default=None,
        help="Use one width value for the left, mid, and right stations in custom mode.",
    )
    parser.add_argument("--left-width-in", type=float, default=None)
    parser.add_argument("--mid-width-in", type=float, default=None)
    parser.add_argument("--right-width-in", type=float, default=None)
    parser.add_argument("--left-height-in", type=float, default=None)
    parser.add_argument("--mid-height-in", type=float, default=None)
    parser.add_argument("--right-height-in", type=float, default=None)
    parser.add_argument("--wall-thickness-in", type=float, default=None)
    parser.add_argument("--left-web-opening-ratio", type=float, default=None)
    parser.add_argument("--mid-web-opening-ratio", type=float, default=None)
    parser.add_argument("--right-web-opening-ratio", type=float, default=None)
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
    args = parser.parse_args()

    geometry, geometry_mode = build_geometry_from_args(args)
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

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    x_in = build_x_grid(geometry.span_in, stations=args.stations)
    plot_geometry(geometry, output_dir, x_in)

    print(f"Beam geometry mode: {geometry_mode}")
    print("Beam geometry: tapered rectangular tube")
    print(
        "  Outer widths [left, mid, right]: "
        f"[{geometry.left_width_in:.3f}, {geometry.mid_width_in:.3f}, {geometry.right_width_in:.3f}] in"
    )
    print(
        "  Outer heights [left, mid, right]: "
        f"[{geometry.left_height_in:.3f}, {geometry.mid_height_in:.3f}, {geometry.right_height_in:.3f}] in"
    )
    print(f"  Wall thickness: {geometry.wall_thickness_in:.3f} in")
    print(
        "  Web opening ratios [left, mid, right]: "
        f"[{geometry.left_web_opening_ratio:.3f}, {geometry.mid_web_opening_ratio:.3f}, {geometry.right_web_opening_ratio:.3f}]"
    )
    print(f"  Material: {material.name}")
    print(f"  Effective modulus: {material.effective_modulus_psi:.0f} psi")
    print(f"  Effective allowable stress: {material.effective_allowable_stress_psi:.0f} psi")
    print("  Assumption: beam self-weight is neglected in stress and deflection calculations.")

    for load_case in load_cases:
        result = analyze_load_case(
            geometry=geometry,
            material=material,
            load_case=load_case,
            stations=args.stations,
        )
        plot_load_case(result, load_case, output_dir)
        print_summary(result, load_case)

    print(f"\nPlots written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
