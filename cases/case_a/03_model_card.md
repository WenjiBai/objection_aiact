# CV-Sage Suitability Model — Model Card v3.2

**Owner:** CV-Sage ML team
**Released:** 2026-01

## Intended use

Producing a per-applicant **suitability score** (0–100) and rationale used to
generate a top-N shortlist for an open requisition. The model is intended to
support — not replace — a human recruiter's first-pass triage.

## Inputs

- Parsed CV text (skills, experience entries, education).
- Job description (requirements, seniority, location, must-haves).
- Optional: transcripts from recorded screening interviews (≤ 15 min each).

## Outputs

- Suitability score (float, 0–100).
- Four sub-scores: skills match, experience match, communication signals,
  diversity signals.
- A short rationale (≤ 60 words) generated from the structured score breakdown.

## Model architecture

- Skills + experience matching: fine-tuned encoder (sentence-transformer
  derivative).
- Rationale generation: third-party general-purpose language model accessed
  via API. See "Foundation model dependency" below.

## Foundation model dependency

The rationale generator is built on top of a general-purpose language model
licensed from a foundation-model provider. We do not train or fine-tune the
underlying model. The provider's terms of service include a data-retention
opt-out which we have enabled for our enterprise tier.

## Training data

- ~480,000 anonymised job postings from public sources (2018–2024).
- ~2.1M anonymised applications from CV-Sage customers, with usage permission.
- No demographic labels are included in training inputs.

## Bias testing

We perform aggregate parity checks across self-reported gender (where opt-in
data is available) on a held-out evaluation set, quarterly. Results are
provided to enterprise customers on request. Parity for protected attributes
beyond gender has not been systematically tested.

## Known limitations

- Performance degrades for highly technical specialisms not well-represented
  in training data (e.g. niche embedded-systems roles).
- Multilingual support is limited to English, German, French, Finnish, Swedish.
- The diversity booster is **opt-in per customer** and disabled by default.

## Versioning

v3.2 is the production version (since 2026-01). v3.0 is deprecated.
