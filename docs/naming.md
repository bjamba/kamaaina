# Naming in Kamaʻāina

## Why Hawaiian names

The author of this project was born and raised in Hawaiʻi (though not ethnically Hawaiian). The names in this project celebrate those roots and that upbringing. They are chosen with care, used with respect, and are open to correction — if you are a speaker of ʻōlelo Hawaiʻi or a cultural practitioner and see a name used incorrectly or inappropriately here, please open an issue. Getting this right matters more than keeping a name.

## The orthography rule

Hawaiian orthography uses two marks that ASCII-centric tooling handles poorly:

- The **ʻokina** (ʻ) — a consonant, written as a single open quote, marking a glottal stop.
- The **kahakō** (ā, ē, ī, ō, ū) — a macron marking a long vowel.

The rule for this repository:

| Context | Form | Example |
|---|---|---|
| Documentation prose, titles, headings | Proper orthography | Kamaʻāina, Loea |
| Directory names, filenames, slugs, code identifiers | ASCII, no diacritics | `kamaaina`, `loea` |
| Manifest `name` field | ASCII slug | `name: loea` |
| Manifest `title` field | Proper orthography | `title: Loea` |

The ASCII forms exist purely for tooling compatibility (shells, URLs, cross-platform filesystems). They are not the preferred spellings — the documentation is where the names live properly, and documentation should always use the correct marks. Not knowing the marks yet is a reason to look them up, not a reason to leave them out.

## Glossary of names used

- **Kamaʻāina** — literally "child of the land"; a person of a place, a longtime local. This project is named for the idea of building AI tooling that belongs to the machine it runs on — local-first, of the land it lives on — rather than renting capability from somewhere far away.

- **Loea** — the skill-creator tool in this ADK. *Loea*: skill, ingenuity, cleverness; a master of a craft (one speaks of a loea of lauhala weaving or of navigation). Chosen because the tool's essence is exactly that kind of mastery — expert, inventive design within hard constraints. *(Naming history: this tool was briefly named Kū at the project's founding. It was renamed both because loea is the tighter fit for a tool about skill itself, and out of respect for the weight Kū carries as one of the four great akua of Hawaiian tradition — a weight a software tool has no business borrowing. The record stays here on purpose: naming is design review, and reviews sometimes reverse.)*

- **Waihona** *(proposed, pending review)* — the context-base format and its scaffold tool. *Waihona*: depository, archive, a place where valuables are kept (as in *hale waihona puke*, library). Chosen because the context-base is exactly that — the place a local stack keeps its accumulated knowledge. Spec: `design/context-base/context-base.md`.

## For contributors

- When you introduce a new named artifact, add it to the glossary above with its meaning and why it was chosen.
- Use proper orthography in all prose from the start; ASCII only in paths and identifiers.
- If a proposed name draws on Hawaiian language or culture, treat the naming as part of the design review, not decoration.
