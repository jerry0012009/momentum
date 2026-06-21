# PM-14A Bilingual Factor Cards

**Date:** 2026-06-21
**Follows:** PM-13B (period-level quantile diagnostics)

---

## Summary Verdict

**`BILINGUAL_CARDS_PASS_WITH_REVIEW_FLAGS`**

All 71 factors have bilingual (EN/ZH) factor cards with complete metadata. All cards are `AUTO_GENERATED_REVIEW_REQUIRED` because the metadata is template-generated and should be reviewed by a domain expert before being treated as authoritative.

---

## 1. Files Generated

| File | Rows | Format |
|------|------|--------|
| factor_bilingual_cards.csv | 71 | CSV |
| factor_bilingual_cards.json | 71 | JSON |
| manifest.json | — | JSON |

Directory: `research/factor_runs/crypto_top50_factor_library/factor_metadata/`

---

## 2. Factor Count Coverage

- Expected: 71
- Generated: 71
- Missing: 0
- Duplicate IDs: 0

---

## 3. Required Field Validation

All 71 cards have non-empty values for:
- factor_id, name_en, name_zh, formula_en, formula_zh
- intuition_en, intuition_zh, metadata_quality
- All other required fields from spec

---

## 4. Metadata Quality Distribution

| Quality | Count | Description |
|---------|-------|-------------|
| AUTO_GENERATED_REVIEW_REQUIRED | 71 | Template-generated, needs domain expert review |

All cards are marked `AUTO_GENERATED_REVIEW_REQUIRED` because:
1. Bilingual text is template-based, not hand-crafted by domain experts.
2. Direction explanations are generic by family, not per-factor validated.
3. Known limitations are a mix of generic and per-factor overrides.

---

## 5. Data Source Type Distribution

| Type | Count |
|------|-------|
| MOMENTUM_REVERSAL | 12 |
| VOLATILITY | 8 |
| TECHNICAL | 12 |
| HYBRID | 10 |
| PRICE_POSITION | 7 |
| RANGE_CANDLE | 3 |
| CROSS_SECTIONAL | 2 |
| VOLUME | 8 |
| TAKER_FLOW | 3 |
| FUNDING_RATE | 3 |

---

## 6. Example Cards

**mom_20h:**
- EN: "20h Momentum" — Measures price continuation over 20h.
- ZH: "20小时动量" — 衡量20小时内的价格延续性。
- Formula: `close / close_lag(20) - 1`
- Direction: positive (higher = continued upward drift)
- Quality: AUTO_GENERATED_REVIEW_REQUIRED

**volatility_20h:**
- EN: "20h Volatility" — Measures return dispersion over 20h.
- ZH: "20小时波动率" — 衡量20小时内的收益离散度。
- Formula: `std(ret_1h, 20)`
- Direction: negative (high vol historically underperforms)
- Quality: AUTO_GENERATED_REVIEW_REQUIRED

**taker_buy_ratio_20h:**
- EN: "20h Taker Buy Ratio" — Measures taker buy vs sell pressure.
- ZH: "20小时主动买入比率" — 衡量主动买卖压力。
- Formula: `mean(taker_buy_qvol / qvol, 20)`
- Direction: positive
- Quality: AUTO_GENERATED_REVIEW_REQUIRED

---

## 7. Known Limitations

1. All metadata is template-generated — human review recommended.
2. Chinese translations are functional, not polished.
3. Per-factor limitations are generic for most factors; only 12 have specific overrides.
4. No connection to diagnostics metrics in the cards themselves (designed for PM-15 integration).
5. `source_fields` is inferred from `required_columns`, not from actual data pipeline audit.

---

## 8. Non-Change Statement

- No factor formulas modified.
- No signal panel modified.
- No public HTML pages modified.
- No new factors added.

---

## 9. Recommended Next PM

**PM-14B: Factor Card Chinese Review and Polish**

Have a Chinese-speaking domain expert review and polish the Chinese translations, intuition descriptions, and direction explanations. Upgrade cards from `AUTO_GENERATED_REVIEW_REQUIRED` to `COMPLETE` or `NEEDS_REVIEW` after review.
