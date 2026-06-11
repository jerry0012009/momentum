# EMA non60m survivor frontier：把 family-level honesty 的前线排出来

## 本轮认领

- 主点：`EMA / PSAR raw alpha focus`
- 具体任务：把 `baseline family survivors` 从“non60m 还活着”的存在性切片，再往前推进半步，直接回答：**如果后面只做一刀 `EMA non60m` 的 family-level honesty / rolling / OOS，最该先看哪几个口袋？**

## 为什么选这个

这轮优先选 EMA 线，而且刻意不再补 protocol / gate / closure wording，原因是：
1. `docs/TODO.md` 顶部当前最明确还没做完的，就是 `EMA：把 baseline family survivors 推到更诚实的 family-level honesty`；
2. 前一轮已经证明 `EMA 60m crypto` 是 fail pocket，而 `EMA non60m` 整体仍很厚，但“整体很厚”还不足以指导下一步该先做哪一刀 rolling / OOS；
3. 现成 `ema_psar_cost_budget_by_combo.csv` 已经足够回答这个问题，不需要新下载或重跑重型回测。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新增 `build_ema_non60m_honesty_queue(...)`；
   - 把 `EMA non60m`（仅 `1d + 1wk`）按 `breakeven_roundtrip_cost_bps` 从薄到厚排序，生成新的 durable artifact：
     - `reports/artifacts/ema_psar_raw_alpha/ema_non60m_honesty_queue.csv`
2. 更新 `EMA / PSAR Raw Alpha Focus Report`
   - 新增 **Q17：如果不想在 18 个 non60m 组合上平均用力，EMA family-level honesty 应该先看哪几个口袋？**
   - 把“survivor frontier”直接挂回页面，而不是只说 `non60m` 还活着。
3. 更新 `docs/TODO.md`
   - 给顶部 relay baton 里的 EMA 第 2 条补上最新结果；
   - 同步在 EMA 详细收口段补入同样口径；
   - 让 `reports/site/plans/momentum_todo.html` 也同步可见。
4. 重建可见产物
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 核心结果

### 1) `EMA non60m` 不是“18 个组合都一样厚”，前线已经能排出来

来自新的 `ema_non60m_honesty_queue.csv`：

当前最薄的 `EMA non60m` survivor frontier 依次是：
1. `沪深300ETF 1d`：breakeven 约 `39.7bps`，`50bps` 近似下已约 `-5.79%`
2. `沪深300ETF 1wk`：约 `184.0bps`
3. `创业板ETF 1d`：约 `237.7bps`
4. `创业板ETF 1wk`：约 `276.5bps`
5. `SPY 1d`：约 `339.0bps`
6. `QQQ 1d`：约 `383.2bps`

这说明：虽然 `EMA non60m` 整体还是厚的，但如果后面真的要做 family-level honesty，**最有信息量的不是先去看最厚的 crypto 周频，而是先看这些“最薄但还没正式倒下”的 survivor frontier**。

### 2) 当前最薄口袋已经足够接近 falsification frontier

尤其是：
- `沪深300ETF 1d` 虽然仍在 `non60m family` 里，但 breakeven 只有约 `39.7bps`；
- 到 `50bps` 近似时已经转到约 `-5.79%`；
- 这使它更像“family 里最先该被 rolling / OOS 拿来验真伪”的薄边，而不是可以放心归类成厚口袋。

换句话说，当前 `EMA baseline family` 的关键问题，已经不再是“60m 能不能救”，而是：**这些 non60m 薄边口袋在更正式 honesty 下还能不能守住。**

### 3) 当前更有价值的 next step 被进一步收窄了

这轮之后，EMA 线下一棒更明确：
- 不是继续围着 `EMA 60m crypto` 打转；
- 也不是先去看最厚的 `BTC / SOL 1wk` 这类 backstop；
- 而应优先拿 `沪深300ETF / 创业板ETF / SPY / QQQ` 这些 non60m 薄边 survivor 去做第一刀 rolling / OOS honesty。

如果连这批都过不了，`EMA baseline family` 就该继续收窄；
如果它们还能守住，再去看更厚的口袋才有意义。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现：
  - `Q17. 如果不想在 18 个 non60m 组合上平均用力...`
  - `39.7bps`
  - `184.0bps`
  - `276.5bps`
  - `reports/artifacts/ema_psar_raw_alpha/ema_non60m_honesty_queue.csv`
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步新结果口径。

## 当前更诚实的项目级读法

EMA 线现在已经被切成更清楚的三层：
1. `EMA 60m crypto`：已是 fail pocket；
2. `EMA non60m overall`：整体还活着；
3. `EMA non60m survivor frontier`：最该优先做下一刀 honesty 的前线，是 `沪深300ETF / 创业板ETF / SPY / QQQ` 这些更薄的 non60m 口袋。

这比“non60m 还不错”更接近真正可执行的研究排序。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
