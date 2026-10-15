# Operating Mode — the presentation of the standard

`index.html` is the **source** of the ASF™ Operating Mode document, the one that becomes a deck
or a PDF for clients and new teams. It lives here, in the standard repository, for one reason:
until v8.0 it did not, and it drifted.

## Why it is versioned here

The circulating version was **v5.0, April 2026**, exported to
`ASF_OperatingMode_Presentation_v1.pptx` and sitting in a shared drive. The standard had
meanwhile reached v7.6 and then v8.0. Nine substantive disagreements had accumulated, and none
of them announced itself:

| # | The document said | The standard said |
|---|---|---|
| 1 | `state.json` was never mentioned | It is the **single source of truth** of the whole methodology |
| 2 | Prompt Stack **L0→L3** | L0 → L1 → L1.5 → L2 → L3 → L4 |
| 3 | `requisites.md` as the L1 functional source, named five times | No such file. It is `product.md` |
| 4 | `architecture.md` as L1 | Removed in v8.0; `architecture.json` is the artifact |
| 5 | 6 agents | 9 in v7.6, 13 in v8.0 |
| 6 | **CronStudio** as the interface layer | Renamed kStudio |
| 7 | Quality Gate L1 mentioned, not specified | Five certification points, all mandatory |
| 8 | Decision Records absent | A mandatory procedure with a schema and a status lifecycle |
| 9 | "Claude Code" as the coding engine, `CLAUDE.md` as L0 | v8.0 made L0 vendor-neutral: `AGENTS.md` |

Points 1 to 3 are not cosmetic. A document that never names the source of truth, and names an
L1 file that does not exist, describes a method that nobody can follow.

**A document that lives outside the repository drifts silently**, because nothing fails when it
falls behind: it keeps opening, keeps looking finished, and keeps being sent to clients. Kept
here, it changes in the same commit as the thing it describes — or the diff shows that it did not.

## Regenerating the deck

`index.html` is self-contained: no external CSS, no fonts to fetch, no JavaScript. Open it in a
browser and print to PDF, or import it into the presentation tool of the day.

## The rule that keeps it honest

The last panel of the document states it, and it is the point of keeping the source here:

> Where this document disagrees with the standard files, **the files are right** — and the
> disagreement is a defect to be reported.

Update `index.html` in the same change as the standard it describes. A presentation that is
allowed to lag becomes, within two versions, a second and competing description of the method.
