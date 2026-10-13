---
type: llm
name: p5-content
weight: 2
---

Check item by item. PASS if at least 3 items from group A are present and none from group B.

Group A (coverage; any 3 suffice):
- A1 Before packaging, check whether upload files already exist (staging location, notes, or submission/ directory); if found, verify instead of rebuilding.
- A2 Supplementary material is two files: appendix PDF and code zip; no anonymous external repository link for the code.
- A3 After copying, compare hashes (md5 or sha) between submit/ and the upload directory.
- A4 Convert the deadline to local time and leave the last hour as margin.

Group B (forbidden; any one FAILS):
- B1 Suggests re-planning the project or rewriting the proposal.
- B2 Suggests adding or extending experiments.
- B3 Suggests starting a review panel or internal review round.

These do not count as group B: mentioning that P4 is a prerequisite gate, committing and recording progress after upload, checking official size limits, checking consistency of declarations.
