# Database implementation boundary

The approved 21-entity PostgreSQL model remains authoritative in `docs/05-*` and `docs/06-*`.
DDL/migrations are intentionally not copied or executed. Phase 13 Part 1 uses only a process-local
development repository for the approved account/profile/wellness/consent slice. Provider, region,
retention, legal-hold and RTO/RPO decisions remain unresolved.
