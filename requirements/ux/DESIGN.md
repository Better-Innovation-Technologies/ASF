# DESIGN.md — [Project Name]

> **UX guidelines · Owner: PM / UX** — signed with the look & feel of `docs/product.md`.
> Every interface task loads this file. The design tokens are the code form of what is written
> here: when they disagree, one of the two is a defect, and the review says which.

*(to be completed with the PM / UX during Startup, before Quality Gate Layer 1. A section that is
not decided yet says so and moves its open points to **To be decided** — an empty heading is not a
decision.)*

---

## Guiding principle

[One or two sentences: what the interface must make obvious at first glance, and the trade-off the
team accepts for it — e.g. "the best price is the first thing the eye lands on, at the cost of
density".]

## Theme

[Light only / dark only / both. If both: which is the reference, and whether the user or the system
chooses.]

## Colour — by role

Colours are named by **what they do**, never by how they look: a component asks for `primary` or
`danger`, not for a hex value.

| Role | Used for | Value (in the tokens) |
|---|---|---|
| [brand / primary] | [main actions, active state] | [token name] |
| [accent] | [the one thing to notice] | [token name] |
| [text] | [body and headings] | [token name] |
| [surface] | [backgrounds, cards] | [token name] |
| [feedback: success / warning / error] | [only if the product needs them] | [token name] |

[Rules on combinations and contrast, and the colours the product deliberately does not use.]

## Type

[Typefaces for headings, body and figures; the scale (sizes and line heights); the minimum size.]

## Icons

[Set and style (outline / filled), sizes, when an icon needs a text label.]

## Spacing and radii

[The spacing scale (e.g. a 4 px base), corner radii by element, borders and shadows.]

## Mobile patterns

[Priority device; navigation pattern; touch target size; how lists, filters and forms behave on a
small screen.]

## Components and their states

For each component the product uses: what it is for, and how it looks in every state.

| Component | Default | Hover / focus | Active / selected | Disabled | Loading | Error | Empty |
|---|---|---|---|---|---|---|---|
| [button] | | | | | | | |
| [card] | | | | | | | |

## Microcopy

[Tone of voice, person and register; how numbers, prices, dates and units are written; error
messages say what happened and what to do; words the product never uses.]

## Accessibility

[Target WCAG level; contrast; keyboard and screen-reader rules; motion that can be turned off.]

## Tokens as code

[Where the design tokens live in the code (file or package), their naming convention, and how a new
token is added. Components take colour, type, spacing and radius from the tokens only — never a
literal value.]

## To be decided

- [Open point — who decides, by when.]
