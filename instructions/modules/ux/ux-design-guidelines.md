## UX — design guidelines and tokens

Every piece of interface work follows **`docs/requirements/ux/DESIGN.md`**: theme, colour roles,
type, icons, spacing and radii, mobile patterns, component states, microcopy, accessibility. Load it
with the task, as you load the requirement: an interface built without it is built against nothing.

### Tokens, never literal values

- Colour, type, spacing, radius, shadow and motion come from the design tokens in
  `{{tokens_path}}`, by **role** (`primary`, `surface`, `danger`), never by value. A hex code, a
  pixel size or a font name written in a component is a review defect, like a hard-coded business
  value.
- A value the tokens do not have is a question for `DESIGN.md` first: the guideline is extended,
  the token follows in the same merge request, and only then the component uses it.
- `DESIGN.md` and the tokens say the same thing. When they disagree, stop and report it: one of
  the two is a defect, and choosing silently hides it.

### Components

- Every component the product uses has all the states `DESIGN.md` lists for it — default, focus,
  disabled, loading, error, empty — before it is called done. A missing state is a missing
  acceptance criterion, not a polish item.
- Reuse before creating: a new component that duplicates an existing one under another name is
  rejected in review.
- Text the user reads follows the microcopy of `DESIGN.md` and the localization rules of this file.

### Accessibility

The target in `DESIGN.md` is part of the Definition of Done of every interface task: contrast,
keyboard use, focus visibility, labels for icons without text, touch targets on mobile.
