# Cosmic Binding Basins / TEC-2

Short exploratory preprint and pilot validation for the TEC-2 framework:

> Dark energy is treated here as a large-scale boundary-setting term for gravitational membership, rather than as an internal dynamical disruption mechanism within already bound systems.

## DOI

Archived v0.1.0 DOI: [10.5281/zenodo.20310154](https://doi.org/10.5281/zenodo.20310154)

Current working version in this repository: `v0.2.0`.

## Core idea

TEC-2 proposes a dimensionless boundary index for gravitational-basin membership in ΛCDM:

```text
T_Lambda(R,M) = Omega_Lambda H0^2 R^3 / (G M)
```

The index compares the effective acceleration associated with the cosmological constant to the mean gravitational acceleration of an enclosed mass.

- `T_Lambda < 1`: gravitational basin / bound regime
- `T_Lambda ~ 1`: exterior boundary / turnaround-like regime
- `T_Lambda > 1`: outside the ideal basin; expansion-dominated scale

This is not claimed as a new physical law. It is a compact diagnostic derived from the ΛCDM turnaround scale.

## Geometric extension

The current manuscript also introduces TEC-3 as a proposed extension, not as a validated result. TEC-3 reframes basin membership through local Weyl/tidal curvature versus the cosmological dark-energy curvature scale:

```text
B_Lambda(x) = sqrt(C_abgd C^abgd / 48) / (Lambda/3)
```

For the ideal Schwarzschild-de Sitter case, this reduces to:

```text
B_Lambda(R) = 1 / T_Lambda(R,M)
```

This is the stronger research direction for future simulation tests.

## Files

- `paper/Cosmic_Binding_Basins_preprint_v0.2.docx`: editable revised short preprint draft.
- `paper/Cosmic_Binding_Basins_preprint_v0.2.pdf`: shareable revised PDF generated from the same manuscript content.
- `data/cosmic_binding_basins_literature_validation.csv`: clean English pilot validation sample for publication.
- `data/tec_literature_validation.csv`: internal raw validation sample used by the scripts.
- `code/tec_literature_validation.py`: script used to compute `T_Lambda` for the literature sample.
- `figures/tec_literature_validation.png`: validation plot with error bars.
- `figures/tec_diagrama_fase_Tlambda.png`: TEC phase diagram, now labelled in English.
- `figures/tec_resumo_por_classe.png`: synthetic class summary, now labelled in English.
- `figures/tec_turnaround_fit.png`: synthetic turnaround-scaling test, now labelled in English.
- `figures/tec_energia_escura_dinamica.png`: dynamical dark-energy extension, now labelled in English.
- `data/tec_resumo_estatistico.json`: synthetic sample summary.
- `code/tec_numerical_study.py`: synthetic proof-of-concept script.
- `references.bib`: BibTeX references.

## Publication status

Exploratory preprint draft. Not peer reviewed.

## v0.2.0 changes

- Revised the dark-energy wording to avoid rhetorical "destruction" language.
- Converted figure labels and captions to English.
- Corrected the validation boundary label to `T_Lambda = 1 boundary`.
- Expanded the manuscript figure set and retained TEC-3 as a proposed geometric extension, not a validated result.

## Recommended claim

The pilot validation shows that published structures interpreted as bound, in turnaround, or collapsing remain below `T_Lambda = 1` in central estimates, consistent with TEC-2 as an exterior-boundary criterion for gravitational membership. This does not demonstrate universality, but provides preliminary independent consistency.

## Next validation step

Run the same index on a homogeneous simulated or survey sample, compare against existing classifiers, and test whether `T_Lambda` improves boundary prediction relative to mass, density, virial radius, turnaround radius, or cosmic-web classification alone.
