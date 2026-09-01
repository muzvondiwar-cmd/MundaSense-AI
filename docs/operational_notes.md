# Operations and recovery

## Readiness

`python scripts/verify_release.py` verifies required files, bundle schema/checksum/metrics, rules,
locales, directories, database write access, and all three service-level scenarios. The evaluation
page displays the same readiness categories.

## Backup and restore

Stop the app before copying the local SQLite database and its WAL/SHM companions. Backups must be
protected like the source device and include the model/rule versions needed to interpret records.
Test restore on a separate path. Do not commit backups to Git or upload them to an unapproved service.

## Model or rules failure

Do not auto-retrain at startup. Restore the last trusted model and checksum, or run the documented
training command for the demonstration path. A rule failure requires restoration of the matching
reviewed YAML release. Historical snapshots are never silently recomputed.

## Upgrade and rollback

Package model, checksum, metrics, figures, model card, rule catalogue, locale report, tests, and
change log as one release. Run quality and readiness gates, retain the previous known-good package,
and record user-visible changes and rollback target. A pilot adds signature verification and a named
release owner.

