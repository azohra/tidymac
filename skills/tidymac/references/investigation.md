# Investigation

Filesystem measurement locates allocated blocks. Finish only after those blocks have machine-specific meaning.

## Establish context

Run context commands separately so every result is observable:

```bash
df -h /
df -h "$HOME"
diskutil info /
diskutil info /System/Volumes/Data
tmutil listlocalsnapshots /
pwd -P
```

Use only commands available on the Mac. Record missing evidence instead of guessing or escalating.

Modern macOS normally separates a sealed System volume from the writable Data volume. Do not compare System-volume `Used` with user-directory measurements or call either whole-machine physical use. Use the filesystem containing `$HOME` plus APFS container context.

Treat `du -sk` as an allocated-size estimate. APFS clones, hard links, sparse files, compression, snapshots, File Provider placeholders, and purgeable space can separate apparent size from physical recovery. Claim a mechanism only with direct evidence.

## Measure incrementally

Measure one existing, quoted root per invocation, for example:

```bash
du -x -sk "$HOME/Library/Application Support"
du -x -sk "$HOME/Library/Caches"
du -x -sk "$HOME/Library/Containers"
du -x -sk "$HOME/Library/Group Containers"
du -x -sk "$HOME/.Trash"
```

Never combine these examples into one command. Do not scan `$HOME`, glob all home children, loop over them, or run `find "$HOME"`. Allow a slow measurement to finish or report it blocked; do not overlap deep scans.

Rank non-overlapping roots. Inspect one selected parent at a time with `du -d 1` when supported or a quoted immediate-child loop:

```bash
target_path="/exact/path/from-the-census"
for item in "$target_path"/* "$target_path"/.[!.]* "$target_path"/..?*; do
  [ -e "$item" ] || continue
  du -sk "$item"
done | sort -nr
```

This is read-only evidence for one resolved directory, never a cleanup-target pattern.

After the first ranking, share the strongest explanation and next investigation area. Continue with relevant hidden roots, detected ecosystems, smaller aggregates, and a finer pass. Keep personal, project, archive, backup, dataset, and database content opaque unless the user grants content-level review.

## Build dossiers

For each material finding, answer:

| Question | Useful evidence |
|---|---|
| What owns it? | Native inventory, bundle ID, app metadata, receipt, process, manifest |
| What is it? | Safe top-level structure, allocated size, selected metadata |
| Is it active? | Native state, process/open-file ownership, project history, timestamps |
| What action is supported? | Native preview/help, documented UI, exact guarded path |
| What does the user pay? | Regeneration, network, rebuild, reset, state loss, permanence |
| What comes back physically? | Native estimate, local allocation, overlap/sparse risk, before/after free space |

Use `stat`, `du`, `mdfind`, `mdls`, `plutil`, `pkgutil`, `launchctl`, `pgrep`, and `lsof` narrowly. A process absence or old timestamp is a clue, not proof of abandonment.

Read only manifest fields needed to establish ownership, activity, or regeneration. Do not dump content, secrets, process lists, archive members, or personal filenames. Interactive reports may show the minimum useful owner identifier; shareable reports use generic labels and IDs.

## Track coverage and reconciliation

Coverage is `contextualized non-overlapping bytes / measured in-scope non-overlapping bytes`. A raw candidate or unresolved finding is not contextualized. Call it in-scope coverage, not whole-machine coverage, when protected or inaccessible roots remain.

Keep a separate reconciliation ledger for:

- Data-volume use
- explained path allocation
- native-owned allocation outside or overlapping the census
- other users and mounted volumes
- inaccessible scope
- documented OS-managed or purgeable context
- residual unexplained storage

Preserve each figure’s source and basis. Do not force `du`, `df`, APFS, and native-tool numbers into a false equality.

## Development context

For generated project artifacts, establish the project root, rebuild manifest, recent Git/worktree activity, repeated copies, and network or native-build cost. Exclude the current project tree. Do not count suspected duplicates or APFS clones as unique savings without evidence.

## Research

Research only a dossier question. Prefer Apple or vendor documentation, source repositories, and native manuals. Separate documented behavior from inference about this Mac. Local evidence wins over generic cleanup advice.
