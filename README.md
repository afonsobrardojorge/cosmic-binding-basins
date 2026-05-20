# Cosmic Binding Basins / TEC-2

Short exploratory preprint and pilot validation for the TEC-2 framework:

> Dark energy does not destroy gravitationally bound structures; it defines the outer limit of gravitational membership.

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

## Files

- `TEC2_preprint_curto_v2_formula_extensoes.docx`: short preprint draft.
- `tec_literature_validation.csv`: pilot literature validation sample.
- `tec_literature_validation.py`: script used to compute `T_Lambda` for the literature sample.
- `tec_literature_validation.png`: validation plot with error bars.
- `tec_resumo_estatistico.json`: synthetic sample summary.
- `tec_numerical_study.py`: synthetic proof-of-concept script.
- `references.bib`: BibTeX references.

## Publication status

Exploratory preprint draft. Not peer reviewed.

## Recommended claim

The pilot validation shows that published structures interpreted as bound, in turnaround, or collapsing remain below `T_Lambda = 1` in central estimates, consistent with TEC-2 as an exterior-boundary criterion for gravitational membership. This does not demonstrate universality, but provides preliminary independent consistency.

## Next validation step

Run the same index on a homogeneous simulated or survey sample, compare against existing classifiers, and test whether `T_Lambda` improves boundary prediction relative to mass, density, virial radius, turnaround radius, or cosmic-web classification alone.
