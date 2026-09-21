<!-- harness:region:start id=doc -->
# Region ownership — how updates never clobber your edits

The v1 updater compared checksums and, when a project-owned file had been
customized (which after `/seed` is *always*), wrote a `.harness-update` sidecar
and left you to merge prose by hand. Every update of the highest-value files
became a conflict. v2 replaces that with **region ownership**: no text merge, no
sidecars, works offline, and no provenance marker that has to live inside JSON.

## The mechanism

A seeded file is a sequence of **harness-owned regions** and exactly one
**project-owned region**, delimited by fenced markers:

```
<!-- harness:region:start id=intro -->
...harness content — the updater OWNS this; it is replaced wholesale on update...
<!-- harness:region:end id=intro -->

<!-- harness:region:start id=project keep -->
...your content — the updater NEVER touches a region marked `keep`...
<!-- harness:region:end id=project -->
```

- `keep` marks a region the updater must preserve verbatim. Every seeded file has
  exactly one, with a fixed heading from the schema (e.g. `## Lessons`,
  `## Project attack surfaces`, `## Project non-negotiables`).
- Region markers are comments in the file's own syntax: `<!-- -->` for markdown,
  `#` for shell/toml, `//` for JS, and for JSON — which has no comments — the
  file is generated whole and carries no project region (config, not prose).

## The update algorithm

For each managed file, given the new template from the source:

1. Parse the local file into regions by id.
2. For each non-`keep` region: replace local content with the template's.
3. For each `keep` region: retain local content unchanged.
4. New template regions are inserted in template order; regions the template
   dropped are removed (unless `keep`).
5. If a local file has no region markers (pre-v2, or user stripped them): fall
   back to the v1 sidecar, and report it — this is the only degraded path.

Because ownership is structural, the updater needs no stored checksums and no
network fetch of the old version. `.harness/manifest.lock` records which files
are managed and their category; `harness.toml` records the version. Drift within
a `keep` region is *expected and yours*; drift within a harness region is
overwritten. That is the whole contract.

## Why not in-file provenance markers

They can't live in JSON, they need per-filetype comment syntax, and they sit
inside merged content where a "clean up this file" pass deletes them first. The
region markers do the same provenance job structurally and survive because they
are load-bearing (removing one visibly breaks the file's ownership).
<!-- harness:region:end id=doc -->
