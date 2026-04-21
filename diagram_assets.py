from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle


OUTPUT_DIR = Path("outputs")


def add_double_arrow(ax, start, end, text, text_offset=(0.0, 0.0), color="black", fontsize=11):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="<->",
        mutation_scale=12,
        linewidth=1.6,
        color=color,
    )
    ax.add_patch(arrow)
    text_x = 0.5 * (start[0] + end[0]) + text_offset[0]
    text_y = 0.5 * (start[1] + end[1]) + text_offset[1]
    ax.text(text_x, text_y, text, ha="center", va="center", fontsize=fontsize, color=color)


def add_axis_arrow(ax, start, end, label):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={"arrowstyle": "->", "linewidth": 1.8, "color": "black"},
    )
    ax.text(end[0], end[1], label, fontsize=11, ha="left", va="bottom")


def make_fbd_diagram(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.8))

    beam_x0 = 0.5
    beam_y0 = 1.8
    beam_length = 9.0
    beam_height = 0.45
    support_a_x = 1.0
    support_b_x = 9.0
    load_x = 5.0

    beam = Rectangle(
        (beam_x0, beam_y0),
        beam_length,
        beam_height,
        facecolor="#d9d9d9",
        edgecolor="black",
        linewidth=1.8,
    )
    ax.add_patch(beam)

    tri_a = Polygon(
        [[support_a_x - 0.28, 1.3], [support_a_x + 0.28, 1.3], [support_a_x, 1.8]],
        closed=True,
        facecolor="#b7d7f0",
        edgecolor="black",
        linewidth=1.4,
    )
    tri_b = Polygon(
        [[support_b_x - 0.28, 1.3], [support_b_x + 0.28, 1.3], [support_b_x, 1.8]],
        closed=True,
        facecolor="#b7d7f0",
        edgecolor="black",
        linewidth=1.4,
    )
    ax.add_patch(tri_a)
    ax.add_patch(tri_b)
    ax.plot([support_a_x - 0.45, support_a_x + 0.45], [1.2, 1.2], color="black", linewidth=1.2)
    ax.plot([support_b_x - 0.45, support_b_x + 0.45], [1.2, 1.2], color="black", linewidth=1.2)

    ax.annotate(
        "",
        xy=(support_a_x, 3.2),
        xytext=(support_a_x, 2.25),
        arrowprops={"arrowstyle": "->", "linewidth": 2.0, "color": "tab:blue"},
    )
    ax.text(support_a_x - 0.18, 3.28, r"$R_A$", color="tab:blue", fontsize=12)

    ax.annotate(
        "",
        xy=(support_b_x, 3.2),
        xytext=(support_b_x, 2.25),
        arrowprops={"arrowstyle": "->", "linewidth": 2.0, "color": "tab:blue"},
    )
    ax.text(support_b_x - 0.18, 3.28, r"$R_B$", color="tab:blue", fontsize=12)

    ax.annotate(
        "",
        xy=(load_x, 2.25),
        xytext=(load_x, 3.6),
        arrowprops={"arrowstyle": "->", "linewidth": 2.2, "color": "tab:red"},
    )
    ax.text(load_x + 0.12, 3.62, r"$P$", color="tab:red", fontsize=12)

    add_double_arrow(ax, (support_a_x, 0.72), (support_b_x, 0.72), r"$L=8\ \mathrm{in}$", text_offset=(0.0, -0.14))
    add_double_arrow(ax, (beam_x0, 0.25), (beam_x0 + beam_length, 0.25), r"$L_\mathrm{total}=9\ \mathrm{in}$", text_offset=(0.0, -0.14))
    add_double_arrow(ax, (support_a_x, 4.1), (load_x, 4.1), r"$a$", text_offset=(0.0, 0.16))

    add_axis_arrow(ax, (-0.05, 0.85), (0.75, 0.85), r"$x$")
    add_axis_arrow(ax, (-0.05, 0.85), (-0.05, 1.70), r"$y$")

    ax.text(beam_x0 + beam_length / 2.0, 2.03, "Rectangular beam idealization", fontsize=11, ha="center")
    ax.text(support_a_x, 1.02, "Support A", fontsize=10, ha="center")
    ax.text(support_b_x, 1.02, "Support B", fontsize=10, ha="center")

    ax.set_xlim(-0.1, 10.2)
    ax.set_ylim(-0.1, 4.5)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_dir / "fbd_rectangular_beam.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def make_front_view_diagram(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    x0 = 0.6
    y0 = 1.4
    length = 8.0
    left_h = 1.0
    mid_h = 2.2
    right_h = 1.0

    top_pts = [
        (x0, y0 + left_h / 2.0),
        (x0 + length / 2.0, y0 + mid_h / 2.0),
        (x0 + length, y0 + right_h / 2.0),
    ]
    bottom_pts = [
        (x0 + length, y0 - right_h / 2.0),
        (x0 + length / 2.0, y0 - mid_h / 2.0),
        (x0, y0 - left_h / 2.0),
    ]
    body = Polygon(
        top_pts + bottom_pts,
        closed=True,
        facecolor="#d9d9d9",
        edgecolor="black",
        linewidth=1.8,
    )
    ax.add_patch(body)

    ax.plot([x0 + length / 2.0, x0 + length / 2.0], [y0 - 1.45, y0 + 1.72], linestyle="--", color="gray", linewidth=1.2)
    ax.plot([x0, x0], [y0 - 0.95, y0 + 1.12], linestyle="--", color="gray", linewidth=1.2)
    ax.plot([x0 + length, x0 + length], [y0 - 0.95, y0 + 1.12], linestyle="--", color="gray", linewidth=1.2)

    add_double_arrow(ax, (x0 + 0.05, y0 + 1.12), (x0 + length / 2.0 - 0.06, y0 + 1.12), r"$x$")
    add_double_arrow(ax, (x0 + length / 2.0 + 0.06, y0 + 1.12), (x0 + length - 0.05, y0 + 1.12), r"$L-x$")
    add_double_arrow(ax, (x0 - 0.75, y0 - left_h / 2.0), (x0 - 0.75, y0 + left_h / 2.0), r"$h(0)$", text_offset=(-0.25, 0.0))
    add_double_arrow(
        ax,
        (x0 + length / 2.0 + 1.00, y0 - mid_h / 2.0),
        (x0 + length / 2.0 + 1.00, y0 + mid_h / 2.0),
        r"$h(x)$",
        text_offset=(0.34, 0.0),
    )

    add_axis_arrow(ax, (0.15, 0.15), (1.05, 0.15), r"$x$")
    add_axis_arrow(ax, (0.15, 0.15), (0.15, 1.05), r"$y$")

    ax.text(x0 + length / 2.0, y0 + 2.02, "Front view: tapered height profile", fontsize=11, ha="center")
    ax.set_xlim(-0.55, 9.95)
    ax.set_ylim(-0.2, 3.7)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_dir / "front_view_dimensions.png", dpi=240, bbox_inches="tight")
    plt.close(fig)

def make_cross_section_diagram(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    rect = Rectangle((1.9, 0.9), 3.5, 2.0, facecolor="#d9d9d9", edgecolor="black", linewidth=1.8)
    ax.add_patch(rect)
    ax.plot([3.65, 3.65], [0.35, 3.45], linestyle="--", color="gray", linewidth=1.2)
    ax.plot([1.2, 6.35], [1.9, 1.9], linestyle="--", color="gray", linewidth=1.2)

    add_double_arrow(ax, (1.9, 0.45), (5.4, 0.45), r"$b(x)$", text_offset=(0.0, -0.16))
    add_double_arrow(ax, (6.95, 0.9), (6.95, 2.9), r"$h(x)$", text_offset=(0.34, 0.0))
    ax.text(3.92, 2.24, "centroid", fontsize=10, ha="left")
    ax.text(6.05, 2.42, r"$c(x)=h(x)/2$", fontsize=10, ha="left")

    add_axis_arrow(ax, (0.5, 0.5), (1.35, 0.5), r"$z$")
    add_axis_arrow(ax, (0.5, 0.5), (0.5, 1.35), r"$y$")

    ax.text(3.65, 3.55, "Cross-section dimensions", fontsize=11, ha="center")
    ax.set_xlim(0.0, 7.6)
    ax.set_ylim(0.0, 3.8)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_dir / "cross_section_dimensions.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    make_fbd_diagram(OUTPUT_DIR)
    make_front_view_diagram(OUTPUT_DIR)
    make_cross_section_diagram(OUTPUT_DIR)
    print(f"Saved diagrams to {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
