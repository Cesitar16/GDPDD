from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def save_count_plot(data: pd.Series, title: str, xlabel: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(data.index.astype(str), data.values, color="#1f4e79")
    ax.set_title(title, fontweight="bold", pad=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Cantidad de registros")
    ax.bar_label(bars, padding=3)
    fig.tight_layout(pad=1.5)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def save_target_group_plot(crosstab: pd.DataFrame, title: str, xlabel: str, path: Path) -> None:
    ax = crosstab.plot(kind="bar", stacked=True, figsize=(7, 4.5), color=["#9dc3e6", "#1f4e79"])
    ax.set_title(title, fontweight="bold", pad=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Cantidad de registros")
    ax.legend(title="target")
    plt.tight_layout(pad=1.5)
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()


def save_original_unique_comparison(comparison: pd.DataFrame, title: str, xlabel: str, path: Path) -> None:
    """Grafica porcentajes comparables para original y deduplicado."""
    pivot = comparison.pivot(index="categoria", columns="version", values="porcentaje").fillna(0)
    ax = pivot.plot(kind="bar", figsize=(7.5, 4.8), color=["#9dc3e6", "#1f4e79"])
    ax.set_title(title, fontweight="bold", pad=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Porcentaje del dataset")
    ax.legend(title="Versión")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=2, fontsize=8, rotation=90)
    plt.tight_layout(pad=1.5)
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()


def save_subgroup_heatmap(subgroups: pd.DataFrame, title: str, path: Path) -> None:
    """Muestra el N deduplicado por sex y rango etario, sin usar porcentajes aislados."""
    pivot = subgroups.pivot(index="sex", columns="age_group", values="n_unicos").reindex(columns=["<40", "40-49", "50-59", "60-69", "70+"])
    fig, ax = plt.subplots(figsize=(8, 3.5))
    image = ax.imshow(pivot.values, cmap="Blues")
    ax.set_title(title, fontweight="bold", pad=16)
    ax.set_xlabel("Rango etario")
    ax.set_ylabel("sex (código)")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), [str(value) for value in pivot.index])
    for row in range(pivot.shape[0]):
        for column in range(pivot.shape[1]):
            ax.text(column, row, int(pivot.iloc[row, column]), ha="center", va="center")
    fig.colorbar(image, ax=ax, label="N deduplicado")
    fig.tight_layout(pad=1.5)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
