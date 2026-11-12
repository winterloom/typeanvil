---
title: Homebrew tap and formula, bumped per release
type: spec
status: draft
owner: maintainers
created: 2026-10-16
updated: 2026-11-11
slug: /specifications/homebrew-tap
sidebar_position: 47
tags: [release, homebrew, distribution]
spec_id: homebrew-tap
issue_id: CORE-137
applies_to:
  - scripts/homebrew_formula.py
  - .github/workflows/release.yml
dependencies:
  - release-ci
---

# Homebrew tap and formula

## Overview

The tap repo `winterloom/homebrew-tap` holds `Formula/typeanvil.rb`.
The release workflow generates the formula from the release `SHA256SUMS` and
opens a pull request on the tap.

## Decision

DECIDED 2026-10-16 (agent): the bump opens a reviewable PR on the tap. It does
not push directly. Direct push needs an owner decision after several clean
releases.

## Behavior

1. The formula shall have per-platform `url` and `sha256` for four targets:
   `aarch64-apple-darwin`, `x86_64-apple-darwin`,
   `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-gnu`.
2. `scripts/homebrew_formula.py` shall read the `SHA256SUMS` file of the release
   and fail with exit 1 if any of the four artifacts is missing or the version
   is not CalVer.
3. The formula `test do` block shall check `typeanvil --version` and render a
   minimal HTML file to a non-empty PDF.
4. The `homebrew-bump` job in `release.yml` shall generate the formula and open
   a PR on the tap. It shall skip with a notice, and stay green, when the
   `HOMEBREW_TAP_TOKEN` secret is absent.
5. `winterloom/typeanvil` is public, so the formula downloads release archives
   without authentication. `brew install winterloom/tap/typeanvil` works once
   the tap repo exists.

## Acceptance Criteria

- Given a SHA256SUMS with all four artifacts, when the generator runs, then the
  formula holds each URL and SHA256
  (`tests/test_homebrew_formula.py::test_formula_selects_per_platform_artifact_and_sha`).
- Given a missing artifact, then the generator fails
  (`test_missing_target_fails`).
- Given a non-CalVer version, then the generator fails
  (`test_non_calver_rejected`).

## Verification

2026-11-11: the generator built `typeanvil.rb` from the `v2026.11.0`
`SHA256SUMS`. A local tap install of that formula on Apple Silicon printed
`typeanvil 2026.11.0`, `brew test` passed, and a smoke render wrote a 1-page
PDF.

## Open items (need owner)

- Create the tap repo `winterloom/homebrew-tap` and the `HOMEBREW_TAP_TOKEN`
  secret (contents and pull-requests write on the tap).
- Run the bump on the next release and merge its PR.
