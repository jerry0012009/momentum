# Phase 7L-R — PM Review

> Date: 2026-06-15
>
> Status: NEEDS FIX

---

## A. Review Conclusion

Phase 7L-R improved reproducibility by adding `scripts/build_crypto_native_caches.py`, a manifest, and validation tests.

However, Phase 7L-R is not yet fully approved. Phase 7M factor implementation remains blocked.

---

## B. What Passed

- A dedicated cache construction script was added.
- The script exposes the intended modes: `all`, `taker`, `funding`, `validate`.
- A manifest was generated for 5 cache artifacts.
- Summary CSVs were regenerated.
- Tests were added.
- No factor implementation, factor_values build, evaluation, backtest, alpha promotion, or status upgrade was reported.

---

## C. Blocking Issues

### 1. CLI arguments are not fully wired into the builder

The script exposes:

```text
--funding-source
--output-root
```

but `build_funding_events()`, `build_funding_aligned()`, and `build_manifest()` still rely on module-level constants such as `FUNDING_SOURCE` and `OUTPUT_ROOT`.

This means the script is less reproducible than advertised because important CLI parameters do not actually control all construction paths.

### 2. `committed_to_git` in manifest is misleading

The manifest currently marks some data/cache parquet artifacts as `YES` simply because they are below the GitHub 100MB size limit.

This is incorrect. The latest GitHub commit did not include any data/cache parquet files. Therefore these parquet artifacts should be marked as local artifacts, unless the script explicitly verifies they are tracked by Git.

Correct behavior:

```text
committed_to_git = NO_LOCAL_ARTIFACT
```

for all generated parquet caches that are not actually tracked in Git.

If the project wants to distinguish small local files from large local files, add a separate field such as:

```text
large_file_policy
```

or:

```text
size_policy
```

Do not overload `committed_to_git`.

### 3. Validation does not catch the two issues above

The test suite passes, but it does not verify that:

- CLI arguments change construction paths;
- manifest `committed_to_git` matches actual Git-tracked state;
- generated parquet artifacts are intentionally local-only.

---

## D. Required Fix

Do not start Phase 7M.

First run:

```text
Phase 7L-R2 — Cache Reproducibility Fixes
```

Required fixes:

1. Refactor `build_crypto_native_caches.py` so CLI config is passed into all build functions.
2. Fix manifest semantics for `committed_to_git`.
3. Add tests for CLI path wiring.
4. Add tests or explicit manifest logic for local-only parquet artifacts.
5. Update closeout and docs.

---

## E. Phase 7M Readiness

Phase 7M implementation is blocked until Phase 7L-R2 passes PM review.
