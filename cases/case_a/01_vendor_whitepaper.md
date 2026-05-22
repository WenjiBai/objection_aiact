# CV-Sage — Candidate Screening Platform

**Product brief · CV-Sage Inc. · v3.2**

## 1. What CV-Sage does

CV-Sage is an AI-powered candidate screening platform built for mid-market HR
teams. It ingests applicant CVs in PDF or DOCX format, parses recorded interview
transcripts, and produces a **ranked shortlist of the top 5 candidates per
opening**. The shortlist is surfaced to HR managers through our web dashboard.

Typical deployment context: in-house recruiting teams (10–200 hires per year)
processing 50–500 applications per opening. CV-Sage replaces the "first-pass
résumé pile" — the manual triage step where a recruiter spends 30 seconds on
each CV before deciding to move it forward.

## 2. How the ranking works

For each applicant we compute a **suitability score** (0–100) along four
weighted dimensions:

| Dimension | Weight | Inputs |
|---|---|---|
| Skills match | 40% | NLP match of CV content vs. job description requirements |
| Experience match | 30% | Years/relevance of past roles vs. seniority bar |
| Communication signals | 20% | Sentiment + clarity scores on recorded interview answers |
| Diversity signals | 10% | (Optional, opt-in per customer) demographic balance booster |

The shortlist is the top N candidates by suitability score. Tie-breaks use
earliest application timestamp.

## 3. Human oversight (built-in)

CV-Sage includes human oversight by design. HR managers see the ranked list,
the per-dimension scores, and a one-paragraph rationale per candidate. They
choose whom to invite to interview. **No hiring decision is made by the
system.**

## 4. Data handling

- CVs are stored encrypted at rest in the customer's region (EU-West for EU
  customers).
- Interview audio is transcribed by a third-party speech-to-text provider; raw
  audio is deleted after transcription.
- Suitability scores are retained for the duration of the requisition.
- We do not sell or share applicant data.

## 5. Why customers choose CV-Sage

- **70% reduction in time-to-shortlist** on average.
- **2.3× more diverse shortlists** when the diversity booster is enabled.
- SOC 2 Type II certified.

## 6. Pricing

Three tiers: Starter ($199/mo · 50 openings/yr), Growth ($799/mo · unlimited
openings), Enterprise (custom).
