# Internal HR process notes — CV-Sage rollout

**Author:** Talent Ops, Aurora Tech Oy
**Last updated:** 2026-03-14

## Why we're deploying CV-Sage

Engineering team is growing from 35 to ~95 over the next 18 months. Last
hiring cycle, our two recruiters spent ~14 hours/week each on first-pass CV
triage. CV-Sage promises to compress that down to ~3 hours/week so the team
can focus on interviewing and sourcing.

## How we use the output

CV-Sage gives us a ranked top-5 list per opening. The rule for the recruiters is:

1. **The top 3 always get an interview** (recruiter screen first, then panel
   if positive).
2. The remaining 2 get a recruiter screen if the pipeline is thin (less than
   10 active interviews that week).
3. Candidates **outside** the top 5 are sent the polite-rejection template.

## Override

In principle a recruiter can pull a candidate from outside the top 5 into an
interview — there's a manual "force include" button in the dashboard. **In
practice this hasn't been exercised in the four months we've been using it.**

We have not written down when a recruiter should override, nor are we tracking
how often it happens. Hiring managers don't see the underlying scores, only the
final shortlist.

## Appeals

We don't have a formal appeals process for applicants who don't make the
shortlist. If a candidate emails us and asks why, the recruiter copy-pastes a
generic "we received an exceptional volume of applications" reply.

## Open questions for legal review

- Does CV-Sage's ranking count as "evaluation of candidates" under the EU AI
  Act? Legal hasn't weighed in yet.
- We have not done a fundamental-rights impact assessment.
- We haven't checked whether CV-Sage uses any GPAI base model under the hood —
  the vendor docs don't say.
