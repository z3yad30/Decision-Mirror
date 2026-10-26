# Extraction prompt changelog

- **v1.0 — legacy:** Initial extraction prompt. Archived for provenance; it is
  not used for official evaluation.
- **v1.1 — legacy:** Tightened evidence, confidence, status, and null handling
  after review. Archived because it was only a partial summary.
- **v1.2 — legacy:** Expanded the contract and added a calibration exception.
  Archived because the source export is incomplete and block-reversed, and
  contained a gold-specific rule.
- **v1.3 — legacy:** Consolidated a stricter extraction prompt. Archived after
  review identified the gold-specific rule, missing quiz handling, field drift,
  and evidence gates that contradicted the ontology.
- **v2.0 — draft:** Rebuilt as a system prompt aligned with the ontology and
  Task 4 contracts. Adds injection resistance, four-way context handling,
  distinct quiz guidance, evidence-tier confidence, null rules, exact output
  shape, self-authored illustrations, a registry, and leakage tests.
- **v2.1 — draft:** **Failure category:** `context_confusion` →
  **Evidence:** 5 unique dev items, 5/14 organic items →
  **Change:** require evidence for a factor's causal role and clarify that a
  circumstance or constraint alone is not trait evidence →
  **Expected effect:** reduce unsupported family/social/financial factor tags
  and trait scores derived from constraints while preserving evidence-based
  preference scores. Requires a separate dev run and paired comparison before
  it can be kept.
