# App ownership and leftover evidence

Treat leftover detection as an ownership investigation, not a naming exercise.

## Build local ownership evidence

Use built-in application metadata and Spotlight where available:

- Search application bundles in `/Applications`, `~/Applications`, `/System/Applications`, and Spotlight results.
- Read bundle identifiers and display names from `Contents/Info.plist` with `plutil` or `mdls`.
- Relate sandbox container names, app-group identifiers, and leading team identifiers to installed bundle IDs.
- Check nested login items, LaunchAgents, package receipts, Homebrew casks, browser extensions, plugins, and version-manager installations when relevant.
- Check vendor uninstallers, application groups, team identifiers, nested bundles, system extensions, background items, and package-manager ownership before treating related files as abandoned.
- Check a narrowly identified process or open-file owner before touching mutable data.

Do not assume `group.com.apple.*` or team-prefixed group containers are leftovers simply because their names do not exactly match an app bundle.

## Investigate unknown entries

For each meaningful unknown entry:

1. Measure immediate children and timestamps without opening file contents.
2. Look for safe metadata: bundle identifiers, database filenames, manifests, vendor names, update frameworks, and executable names.
3. Check installed applications, casks, receipts, login items, launch items, plugins, extensions, and CLIs as relevant.
4. Check whether a related process is running.
5. Research the exact path or identifier from primary sources when available.
6. Ask whether the user recognizes the product or wants retained settings only when local evidence cannot establish intent.

## Confidence labels

- **Verified owner:** Direct bundle, manifest, receipt, entitlement, process, or native-tool evidence identifies an installed owner.
- **Likely owner:** Several weaker signals point to an installed owner. Keep or research further.
- **Likely leftover:** The product is identified, no installed component or integration remains, timestamps align with removal, and contents are product-specific.
- **Unknown:** Ownership or data value remains ambiguous. Do not propose deletion.

Use “verified leftover” only when authoritative uninstall evidence or the user's direct knowledge closes the remaining uncertainty.

## Data-value checks

Even verified leftovers can contain valuable state. Confirm individually when top-level structure suggests databases, projects, exports, recordings, downloads, models, media, licenses, certificates, keys, authentication, recovery data, backups, archives, simulators, VM disks, container volumes, or shared vendor libraries.

Cloud-provider state, shared AI-model blobs, creative libraries, game saves, plugins, and app-group containers can outlive one application while remaining owned by another installed component. Establish the remaining consumer before calling them leftovers.

When uninstalling an installed application, prefer its bundled or vendor-supported uninstaller. Record what it removes and preserves, then investigate residual paths separately. Deleting an `.app` bundle does not prove related data is disposable or that a subscription, login item, extension, or shared component is gone.

Prefer Trash for approved direct-path removal. Space is not reclaimed until Trash is reviewed and emptied.
