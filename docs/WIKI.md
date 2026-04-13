# Wiki (GitHub Wiki)

This project uses **GitHub Wiki** for documentation pages.

## Where the wiki lives

The wiki content is in a separate git repository (GitHub stores wikis as `<repo>.wiki.git`).

In this workspace, the wiki repo is checked out at:

- `indicators-cli.wiki/`

## Editing workflow

1. Edit markdown files under `indicators-cli.wiki/`
2. Commit and push changes from within that directory (it has its own git history)

## Keeping docs accurate

When you change behavior, update the corresponding wiki pages:

- CLI flags/options → `CLI Reference`
- Config keys/defaults → `Configuration & Templates` and `Config Resolution`
- Data fetch / MultiIndex behavior → `Source Data Deep Dive`
- Output paths / writers → `Write Output Deep Dive`
- Indicator columns → `Indicators (Overview)` and the relevant indicator page
- Tests/profiling flows → `Developer Guide` and `Profiling`
