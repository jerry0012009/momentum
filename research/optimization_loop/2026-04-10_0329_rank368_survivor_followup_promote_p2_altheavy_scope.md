# Rank 368 — survivor follow-up: promote to P2 on 5m alt-heavy scope

- Time: 2026-04-10 03:29 UTC
- Target: `Rank 368 / cross-exchange funding extreme × band-stretch fade shell`
- Action type: survivor follow-up / scope decision
- Verdict: `promote_P2`

## What changed system truth
`Rank 368` 的诚实存活形态不是全市场 `BB/RSI + funding` 模板，而是 **`5m alt-heavy (ETH/ADA/DOGE)` 的 crowding-conditioned mean-reversion pocket**：在单 venue Binance funding 的保守代理下，只要把 scope 收窄到 liquid alts，且 time-stop 不拖太久，after-cost 结果仍为正，因此它应从 survivor 升到 `Active P2`，而不是回到 background。

## Minimal follow-up performed
本轮只补了 survivor 允许的唯一一次最小复检，围绕 `5m alt-heavy` 的三件事：
1. 是否真的只能在 `ETH/ADA/DOGE` 这类 liquid-alt 子集站住；
2. `funding` 阈值不是单点偶然；
3. `exit / time-stop` 是否存在单一 decisive blocker。

复检 artifact：
- `reports/artifacts/literature/rank368_altheavy_5m_threshold_timestop_sensitivity_2026-04-10.csv`

## Key evidence
### 1) Alt-heavy scope 成立，但不是全市场模板
在上一轮 pooled `5m` 六币口径里，成本后正贡献主要来自 `ETH / ADA / DOGE`，而 `BTC / XRP` 明显偏弱、`SOL` 接近打平；因此这条线的诚实读法应是 **alt-heavy crowding fade**，不是“所有大币 perp 都能做”。

### 2) Funding threshold 不是单点偶然
对 `ETH/ADA/DOGE` 的 `5m` lane，用 rolling absolute funding quantile 做 gate：
- `q90 + 12bar time-stop`：`233` 笔，post-cost 约 `+570.4bps`，约 `+2.45bps/笔`
- `q95 + 12bar time-stop`：`217` 笔，post-cost 约 `+256.1bps`，约 `+1.18bps/笔`
- `q97.5 + 12bar time-stop`：`214` 笔，post-cost 约 `+176.1bps`，约 `+0.82bps/笔`

结论：只要 threshold 仍处在“较极端 funding”这一带，edge 会衰减但没有瞬间塌掉；不存在“只有单个阈值能赚钱”的单一 decisive blocker。

### 3) Exit / time-stop 有偏好，但不是致命 honesty flaw
同样在 alt-heavy pooled 口径下：
- `6bar` 普遍接近或低于 break-even（`q90/q95/q97.5` 分别约 `-0.18 / -0.59 / -0.72bps/笔`）
- `12bar` 最稳（分别约 `+2.45 / +1.18 / +0.82bps/笔`）
- `18bar` 开始分化，`q90` 仍可、`q95` 变弱、`q97.5` 接近打平

这说明这条线更像 **短持有的 snapback pocket**：不能过早砍，也不能无限拖长；但这属于可参数化的 execution 现实，而不是推翻 alpha 的 honesty flaw。

### 4) 单币层面仍有后续 admission 空间
- `ETH`：`q90~q97.5` 在 `6/12bar` 都保持小幅正的 after-cost；`18bar` 明显转差
- `DOGE`：`12bar` 最强，`18bar` 仍正
- `ADA`：需要更长 `18bar` 才转正，说明 symbol 异质性真实存在

这正是 `P2 admission` 应继续回答的问题：**是否要做 symbol-tiered exits / thresholds，还是只保留更稳定的 ETH+DOGE 子池。**

## Verdict rationale
按照 policy，survivor 只有这一次 follow-up。现在已经拿到足以改变层级的结论：
- 它不是泛化的 `BB/RSI fade` 旧壳；
- 但它也不该被夸大成全市场模板；
- 诚实收窄到 `5m alt-heavy` 后，after-cost edge 在多个 funding 阈值与合理 time-stop 下仍为正；
- 当前不存在单一 decisive honesty / execution blocker，只存在后续需要 admission 收口的 symbol/parameter 稳定性问题。

因此本轮最合法动作是：**`Rank 368` 从 survivor 直接升到 `Active P2`。**

## Reader-facing takeaway
`Rank 368` 通过了唯一一次 survivor follow-up，但通过方式很具体：**这不是“funding 极端 everywhere 都能 fade”，而是 `5m` liquid-alt 上、资金费率极端给出 crowding 背书后，短持有 snapback 更容易活过成本。** 下一步不该再争论它是不是活着，而该在 `P2` 里回答它到底该保留哪些币、哪些 exit、哪些阈值。
