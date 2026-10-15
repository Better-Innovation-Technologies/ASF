## Localization

The user interface is in **{{ui_language}}** only. That is a product decision, not a reason to
scatter strings in the code:

- User-facing text lives in **one catalog** under `{{messages_path}}`, addressed by stable keys, so
  that adding a locale later is a translation job and not a refactoring.
- Never build a sentence by concatenating fragments; keep one message per sentence, with named
  variables.
- Dates, numbers and currencies are formatted with the locale-aware APIs, never by hand.
