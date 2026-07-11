Place client reference documents here to enable `test_client_reference_subset_if_present`:

| Filename | Document type |
|----------|---------------|
| `MOA Glycine IP.docx` | MOA |
| `Spec Glycine IP.docx` | Specification |
| `GLYCINE IP.docx` | Analysis Protocol (standing) / filled AWS reference |
| `Glycine IP 010326.docx` | COA / Analytical Report |

These files are **optional local artifacts** (large client documents). They may be kept out of git if preferred.

When present, tests compare a subset of the current renderer output against the reference:

- Section margins (`w:pgMar`)
- Page borders (`w:pgBorders`)
- Repeating header table grids (`header2.xml`)

Results are recorded in [`MATCH_STATE.md`](MATCH_STATE.md) (auto-generated on pytest run).  
**PASS** = subset matches; **DIVERGE** = documented delta (does not fail the golden regression gate).

If files are absent, reference tests skip gracefully.
