# Phase 7L-R2 — Cache Reproducibility Fixes Closeout

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7L-R2: cache reproducibility hardening fixes
- Fix CLI wiring, manifest semantics, validate mode, tests
- No factor implementation, no factor_values build, no evaluation/backtest

---

## B. CLI Wiring Fix

**Before:** `--funding-source`, `--output-root` exposed but not wired to `build_funding_events()`, `build_funding_aligned()`, `build_manifest()`. Functions used module-level globals.

**After:** `CacheBuildConfig` dataclass carries all paths. Every builder function receives `cfg: CacheBuildConfig` explicitly. No module-level path globals.

```python
@dataclass
class CacheBuildConfig:
    static_dataset_id: str
    dynamic_dataset_id: str
    funding_source: Path
    output_root: Path
    report_dir: Path
    klines_dir: Path
```

New CLI args: `--report-dir`, `--klines-dir` also wired through.

---

## C. Manifest `committed_to_git` Fix

**Before:** Used file size (>100MB → NO_LOCAL_ARTIFACT, else YES). WRONG.

**After:** All 5 generated parquet artifacts → `NO_LOCAL_ARTIFACT`. Uses `git ls-files --error-unmatch` to verify tracking. No generated parquet is in GitHub.

| Artifact | committed_to_git | size_policy |
|----------|-----------------|-------------|
| taker_enriched_static | NO_LOCAL_ARTIFACT | SMALL_LOCAL_FILE |
| taker_enriched_dynamic | NO_LOCAL_ARTIFACT | LARGE_LOCAL_FILE |
| funding_events | NO_LOCAL_ARTIFACT | SMALL_LOCAL_FILE |
| funding_aligned_static | NO_LOCAL_ARTIFACT | SMALL_LOCAL_FILE |
| funding_aligned_dynamic | NO_LOCAL_ARTIFACT | SMALL_LOCAL_FILE |

New `size_policy` field: `SMALL_LOCAL_FILE` (<100MB) or `LARGE_LOCAL_FILE` (>=100MB).

---

## D. Validate Mode Fix

Now checks:
1. Artifact existence
2. Checksum re-verification for small files
3. `committed_to_git` consistency (YES only if actually git-tracked)
4. `size_policy` consistency with actual file size

---

## E. Test Results

| Test Class | Tests | Result |
|-----------|-------|--------|
| TestScriptExists | 3 | ✅ |
| TestCLIWiring | 2 | ✅ |
| TestManifestSemantics | 6 | ✅ |
| TestTakerSummary | 2 | ✅ |
| TestFundingAlignment | 2 | ✅ |
| TestValidateMode | 2 | ✅ |
| TestNoForbiddenChanges | 2 | ✅ |
| **Total** | **20** | **20/20 PASS** |

---

## F. Phase 7M Readiness

**Phase 7M limited crypto-native factor implementation is allowed pending PM review.**

Script, manifest, and validation tests all pass. Cache is reproducible from raw data via `python scripts/build_crypto_native_caches.py --mode all`.

---

## G. Negative Declarations

No new factors were implemented.
No factor registry was modified.
No factor_ops were modified.
No factor_values were built.
No static evaluation was run.
No dynamic evaluation was run.
No static-vs-dynamic comparison was run.
No diagnostic classification was run.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
