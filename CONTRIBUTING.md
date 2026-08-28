# Contributing

The contents of `skills/tidymac/` make up TidyMac. Keep that directory self-contained and free of runtime dependencies.

Treat changes to the operating contract in `skills/tidymac/SKILL.md` as product changes. Update affected references and public documentation in the same change.

Run the repository check before landing a change:

```bash
mise run check
```

## Publishing a release

1. Choose the semantic version described in the README.
2. Update the pinned tag in the README installation command.
3. Land the change on `main`.
4. Tag that commit and create the matching GitHub release.
5. Run the README installation command with `--list` and confirm that it resolves the new tag and finds `tidymac`.
