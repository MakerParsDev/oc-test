# Portable OpenCode Worker — MakerParsDev

This public repository provides **one stateless worker runtime** for the trusted
dispatcher in [oaslananka-dev/oc-test](https://github.com/oaslananka-dev/oc-test).

- GitHub-hosted Ubuntu runners are temporary; work is dispatched with a validated
  task manifest and an immutable target repository commit.
- OpenCode models use the approved free-model allowlist.
- Workers do not publish changes, open PRs, merge or deploy. Their output is
  scoped evidence for a separate trusted controller.
- Main must contain the reviewed `oc-fleet-worker.yml` workflow and three
  `oc_fleet_*.py` helpers. There are no account credentials in this repository.
- Repository Actions variable: `FLEET_WORKER_REPOSITORY=MakerParsDev/oc-test`.
- Repository Actions bootstrap secret: `DOPPLER_TOKEN`, read-only to the
  central `oc-test/main` configuration.

For implementation and provenance checks, consult the controller repository's
`docs/oc-fleet-configuration.md`.
