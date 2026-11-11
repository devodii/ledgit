# Evals

`receipts eval --event <slug>` measures how well the claim pipeline did and writes:

- `<slug>/report.md` a readable report
- `<slug>/report.json` the same numbers as data
- `<slug>/review-sample.yaml` 20 claims for a person to label

## What is measured

- **Funnel.** Videos, transcripts, candidate claims, judge accepted, ranked, public.
- **Quote integrity.** Every public quote is re-checked against the stored transcript, independently of the extraction stage. This must be 100%.
- **Judge.** A second, skeptical Claude pass reviews each extracted claim against the transcript. The report shows how many it accepted, why it rejected the rest, and how its confidence is distributed.
- **Coverage.** How many public claims have a named speaker, a resolved domain, a country, an SCF award, and at least one linked evidence item, and which sources supplied each fact.
- **Verification.** Verdict distribution and check outcomes.
- **Human review.** Open `review-sample.yaml`, listen to each clip, and set `human_label` to `correct`, `partial` or `incorrect`. Rerun the eval to get a precision estimate.

## Run it

```bash
cd api
DATABASE_URL=... uv run python -m receipts.cli eval --event meridian-2025
```
