#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pie_charts_divertissement.py
Génère des camemberts à partir du CSV exporté depuis index.html.
Pour générer le CSV : ouvrir index.html dans le navigateur et taper
exportCSV() dans la console, puis placer le fichier ici.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ─────────────────────────────────────────────
# PALETTE DE COULEURS (identique au site)
# ─────────────────────────────────────────────

COLOR_MAP = {
    'Bar / Café':              '#c4954a',
    'Restaurant':              '#6daa45',
    'Hôtel / Pension':         '#5591c7',
    'Spectacle / Sociabilité': '#a86fdf',
    'Club / Société':          '#d19900',
    'Club / Discothèque':      '#dd6974',
    'Autre':                   '#7a7974',
}

# ─────────────────────────────────────────────
# CHARGER LE CSV
# ─────────────────────────────────────────────

csv_path = Path('lieux_divertissement.csv')
if not csv_path.exists():
    print("❌ Fichier 'lieux_divertissement.csv' introuvable.")
    print("   → Ouvre index.html dans le navigateur, puis tape dans la console :")
    print("     exportCSV()")
    exit(1)

df = pd.read_csv(csv_path)
print(f"✅ {len(df)} lignes chargées")

years_data = {}
for year, group in df.groupby('annee'):
    years_data[year] = group
    print(f"   {year}: {len(group):4d} lieux")

# ─────────────────────────────────────────────
# GÉNÉRER LES CAMEMBERTS
# ─────────────────────────────────────────────

n_years = len(years_data)
fig = plt.figure(figsize=(7 * min(n_years, 3), 6.5 * (1 + n_years // 4)))
axes = [fig.add_subplot(2 if n_years > 3 else 1, 3 if n_years > 3 else n_years, i + 1)
        for i in range(n_years)]

fig.suptitle('Distribution des types de lieux de divertissement à Lausanne\n(1832 – 2026)',
             fontsize=16, fontweight='bold', y=0.995)

for idx, (year, group) in enumerate(sorted(years_data.items())):
    ax = axes[idx]

    type_counts = group['categorie'].value_counts().sort_index()
    colors = [COLOR_MAP.get(cat, '#CCCCCC') for cat in type_counts.index]

    wedges, texts, autotexts = ax.pie(
        type_counts.values,
        labels=None,
        startangle=90,
        colors=colors,
        autopct='%1.0f%%',
        textprops={'fontsize': 8},
        pctdistance=0.88,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(7)

    ax.legend(
        type_counts.index,
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        fontsize=8,
        frameon=True,
        fancybox=False,
        shadow=False,
        borderpad=0.5,
        labelspacing=0.8
    )

    ax.set_title(f'{year}\n({len(group)} lieux)', fontsize=12, fontweight='bold', pad=10)

for idx in range(n_years, len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout(rect=[0, 0, 0.95, 0.97])
output_file = 'divertissement_comparaison_normalized.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0.2)
print(f"\n✅ Image sauvegardée: {output_file}")

# ─────────────────────────────────────────────
# TABLEAU RÉCAPITULATIF
# ─────────────────────────────────────────────

print("\n" + "═" * 110)
print("TABLEAU COMPARATIF - Distribution des types de lieux")
print("═" * 110)

all_categories = sorted(df['categorie'].unique())

print(f"\n{'Catégorie':<30} | ", end="")
for year in sorted(years_data.keys()):
    print(f"{year:>12} | ", end="")
print()
print("-" * (30 + len(years_data) * 16))

for cat in all_categories:
    print(f"{cat:<30} | ", end="")
    for year in sorted(years_data.keys()):
        group = years_data[year]
        count = len(group[group['categorie'] == cat])
        total = len(group)
        pct = 100 * count / total if total > 0 else 0
        print(f"{count:3d} ({pct:5.1f}%) | " if count > 0 else f"  0 (  0.0%) | ", end="")
    print()

print("-" * (30 + len(years_data) * 16))
print(f"{'TOTAL':<30} | ", end="")
for year in sorted(years_data.keys()):
    print(f"{len(years_data[year]):>12} | ", end="")
print()
print("\n" + "═" * 110)

plt.show()
