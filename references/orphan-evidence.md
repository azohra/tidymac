# Orphan evidence

Treat orphan detection as an evidence-gathering problem, not a naming exercise.

## Initial pass

Run:

```bash
python3 <skill-dir>/scripts/scan_orphans.py \
  --min-size-mb 50 \
  --use-spotlight \
  --output /tmp/tidymac-orphans.json
```

The scanner inventories normal application roots, bundle identifiers, app names, login-item helpers, Spotlight results, and obvious CLI matches. It returns `matched` or `unmatched`. Never rewrite `unmatched` as `orphaned` without further evidence.

## Investigate unmatched entries

For each material unmatched entry:

1. Inspect top-level names, types, allocated sizes, and modification dates without opening user documents unnecessarily.
2. Look for bundle identifiers in plists, database names, package manifests, vendor names, update frameworks, and executable paths.
3. Check `~/Applications`, `/Applications`, `/System/Applications`, Homebrew casks, package receipts, login items, LaunchAgents, LaunchDaemons, browser extensions, plugins, and version-manager installations as relevant.
4. Check whether a related process is running before touching mutable data.
5. Search current primary sources for the exact path or bundle identifier when local evidence is insufficient.
6. Ask the user whether they recognize the app or want its settings retained.

## Confidence labels

- **Verified owner:** Bundle identifier, manifest, receipt, or running process directly identifies an installed owner. Keep unless the user is intentionally resetting it.
- **Likely owner:** Several weaker signals point to an installed owner. Keep or research further.
- **Likely orphan:** The owning product is identified, no installed component or dependent integration remains, timestamps align with uninstallation, and contents are product-specific.
- **Unknown:** The owner or data value remains ambiguous. Do not recommend deletion.

Only use “verified orphan” when authoritative uninstall evidence or the user's direct knowledge closes the remaining uncertainty.

## Data-value checks

Even verified leftovers can contain valuable state. Confirm individually when contents include:

- Databases, projects, exports, recordings, downloads, models, or media
- Licenses, certificates, keys, authentication tokens, or recovery data
- Device backups, archives, simulator state, virtual-machine disks, or container volumes
- Shared vendor libraries used by more than one application

Prefer Trash for approved path removal. Explain that the space is not reclaimed until Trash is emptied, and inspect Trash separately before proposing that irreversible step.
