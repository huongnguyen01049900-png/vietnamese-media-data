# Vietnamese–Korean corpus evidence index

This reusable index covers the site's 266 terminology records. It deliberately contains **no article body or quoted sentence text**. Full contextual excerpts remain in the owner's authenticated private research site and original uploaded corpus.

- `articles.json`: article IDs, language, title, original newspaper URL and date.
- `sentences-*.json`: sentence IDs, article IDs, original spreadsheet locators, SHA-256 text hashes, and Vietnamese field/character offsets.
- `terms-*.json`: term IDs/labels, actual observed forms, sentence references, and specifically reviewed pair references.
- `manifest.json`: counts, status definitions and limitations. Each compact file states its positional row fields.

A Korean occurrence is not automatically a Vietnamese–Korean translation pair. `paired_verified` applies only to the listed local paired context, not every occurrence or the term's etymological/definition status. Other pairs may be conditional or unknown. Matching is conservative lexical boundary plus a Korean-particle list; Vietnamese segmentation is automatic. Neither is exhaustive linguistic analysis.

Original newspaper URLs lead to the source articles, not guaranteed sentence anchors. Private site anchors use `corpus-` followed by the literal sentence ID. Preserve source IDs and offsets when rebuilding from the original user-owned corpora; never invent missing translations.
