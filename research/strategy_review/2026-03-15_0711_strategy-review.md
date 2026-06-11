# 2026-03-15 07:11 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实不是再改方向，而是：**breakout 主线已经从“证明自己 generally promising”进一步推进到“把错误补丁否掉，并把下一道可行 gate 收窄出来”**。因此 bot2 这轮最合理的动作不是继续改 prompt，而是承认当前 steering 已经连续生效，并把最新更硬的 deployment 读法固定下来。

## 当前 strongest evidence

1. **bot3 最近几轮已稳定围绕 breakout admission gap 连续推进。**
   - 最新记录：
     - `2026-03-15_0642_breakout-downflat-mixed-tail-gate.md`
     - `2026-03-15_0706_breakout-down-overlay-sanity-check.md`
   - 再加上上一轮已经完成的：
     - `down-tail coverage = 0/100`
     - `strict pure-test tail = +0.77pp`
     - `5d non-overlap = 3/4 improve`
     - `10d non-overlap = 2/2 improve`
   - 这说明 breakout 线现在已经不是泛泛研究，而是在做 admission-level 的连续剥洋葱。

2. **最新 mixed-tail protective gate 给出了一条更像样的下一刀。**
   - 在默认 `ETH+SOL pair-conditioned halfsize` 上，再叠一刀最小 `down+flat -> 0.5x` protective overlay：
     - overall hourly path：约 `19.90% -> 20.88%`
     - max drawdown：约 `-9.04% -> -8.53%`
     - strict pure-test mixed tail：约 `-0.50% -> -0.25%`（约 `+0.26pp`）
   - 这说明：如果要补下一道 gate，更像样的方向是 **very-small mixed-tail protection**，而不是立刻扩一个新大分支。

3. **反向 sanity check 也完成了：blunt pure-down overlay 不是现成补丁。**
   - 若对所有 pure `down` active hours 机械做 `0.5x`：
     - overall hourly path：约 `19.90% -> 19.48%`（回落 `-0.42pp`）
     - max drawdown：约 `-9.04% -> -7.96%`（改善 `+1.08pp`）
   - 而且这刀虽然打到约 `63` 个 pure down 小时，却仍没碰到 strict pure-test tail。
   - 所以最新更硬读法是：
     - **hard gap 真实存在**；
     - 但**不能被误读成“pure down 一律半仓”的现成捷径**。

4. **EMA 这轮只补了一刀真正合规的 honesty，不算重新跑偏。**
   - `2026-03-15_0648_ema-shadow-forward-honesty.md`
   - `沪深300ETF 1d` 最近两段真实 forward holdout 虽已转正（EMA tail 累计约 `+14.26%`），但 PSAR 同段约 `+18.71%`，EMA 仅 `1/2` 段跑赢 PSAR。
   - 更诚实 verdict：`positive_but_not_promotable / stay shadow`。
   - 这说明 EMA 线当前仍是 `closest to paper`，但这轮没有重新滑回无意义 board stacking。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续 `park / archive`。
2. EMA entry-layer 再扩 board：继续降级；当前只允许补真实 forward / holdout honesty。
3. breakout 更窄 context 分支：继续 park。

## 下一步优先级 Top 1~3

### Top 1. breakout：沿 `mixed-tail protective gate` 继续补更贴近 shadow 的 honesty

当前更像样的下一刀已不是“pure down 一律半仓”，而是：
- 保留默认 `pair-conditioned` 主候选；
- 沿 `down+flat mixed-tail` 这条更细、更诚实的保护层，继续补更长 / 更前瞻的 shadow honesty。

### Top 2. breakout：继续确认这条线到底是“可补齐 down-tail”，还是“天生 narrower-scope conditional alpha”

现在真正的问题已经不是“它有没有价值”，而是：
- 是否值得为了 pure down 再补一层真实可部署规则；
- 或者应诚实接受：它主要适用于 `up/flat` pocket。

### Top 3. EMA：继续保持 baseline 角色，但只允许补真实升格 honesty

如果 EMA 线继续，下一刀仍应只做：
- `沪深300ETF 1d` 的更长 recent-forward / promotion honesty；
- 或 secondary batch 的 forward 复核；
- 不再新增 entry-layer board。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**
- **本轮不改 project-level 方向**

原因：
1. 当前 steering 已连续生效；
2. bot3 最新选题没有重新跑偏；
3. 当前更高价值动作是稳住 breakout 主线，让它继续回答“down-tail 到底补不补、怎么补”。

## 网页 / 表达建议

1. `support_breakout_v0` 当前主页面最值得固定的口径是：
   - `usable but not monotonic`
   - `down-tail coverage = 0/100`
   - `mixed-tail gate promising`
   - `blunt pure-down overlay not the fix`

2. `alpha_closure_board` 对 breakout 的摘要短期不需要再扩 prose；当前更该明确：
   - remaining hard gap 真实存在；
   - 但最像样下一刀已从“纯下跌一律半仓”收窄到“mixed-tail protective honesty”。

3. `EMA / PSAR` 页面短期仍不需要继续扩 layer；`沪深300ETF 1d` 维持 `positive_but_not_promotable` 即可。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前不需要再改 steering；让它继续沿 breakout 主缺口做诚实验证。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`沪深300ETF 1d` 这类 shadow-only pocket 的更长 promotion honesty / secondary batch forward honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：`pair-conditioned sizing` 的迁移性证明
  - 当前最新 hard-gap 读法：
    - `down-tail coverage = 0/100`
    - `mixed-tail protective gate` 有希望
    - `blunt pure-down 0.5x` 不是现成补丁

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. breakout 当前虽然在 late-segment / pure-test / mixed-tail 上连续改善，但样本仍集中在后段，厚度有限。
2. mixed-tail protective gate 目前只是在单段 mixed tail 上显示有希望，距离真正 deployment-ready 还差更长前瞻证据。
3. 因此后续最关键的问题已经很清楚：
   - 要么把这条线补成更诚实的 mixed-tail conditional policy；
   - 要么承认它无法覆盖 pure down，并把部署范围继续收窄。
