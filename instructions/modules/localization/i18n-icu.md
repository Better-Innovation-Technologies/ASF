## Localization (i18n)

The user interface ships in **{{supported_locales}}**; the default locale is **{{default_locale}}**.

- **No user-facing string in the source.** Every label, message, placeholder, tooltip, e-mail and
  error shown to a user lives in the message catalogs under `{{messages_path}}`, one file per
  locale, addressed by a stable key (`orders.empty.title`), never by the English text.
- Messages use **ICU MessageFormat** for plurals, gender and variables. Never build a sentence by
  concatenating fragments, and never split one sentence across keys: translators need the whole
  sentence.
- Dates, numbers, currencies and units are formatted with the locale-aware APIs (`Intl.*`,
  Babel/ICU), never by hand.
- A new key is added to **every** locale in the same merge request; a missing translation fails CI
  instead of falling back silently.
- Logs and operator-facing errors are not localized: they follow the language rules of this file.
- Layouts tolerate text 40% longer than the default locale; do not truncate translated text in code.
