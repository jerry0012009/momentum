# closure board 补入 breakout v0 的成本与脆弱点口径

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，但不再新开回测，而是把上一轮刚得到的 `breakout v0 first-pass 成本` 结论补回总入口页 `alpha_closure_board`。

原因很直接：
1. `support_breakout_v0_h24` 页已经有了新成本段，但 `closure board` 里关于 breakout 线的总览证据还是旧口径；
2. Jerry 现在更常从总入口页判断“先继续哪条线、该警惕什么”，所以最新证据应该先同步到最上位的决策页；
3. 这是一个很小、但能直接提升网页最终表达质量的收口动作。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 将 breakout 线的 `当前最强证据` 改成同时包含最新成本结论：
     - `20bps` 下 overall 平均单笔仍约 `+1.24%`
     - 累计仍约 `+75.03%`
   - 将 `当前不能过度解读什么` 改成更诚实的脆弱点表达：
     - `test split @ 20bps` 累计约 `-3.08%`
     - `up regime @ 20bps` 累计约 `-2.98%`
   - 将 `下一步最值得做什么` 收得更准：优先补 `split / regime honesty`，再看 rolling OOS / non-overlap / capital allocation。
2. 重建 `reports/site/factors/alpha_closure_board/report.html`
   - breakout 这张卡现在已经反映最新成本页结论，而不是停留在更早的 v0 口径。

## 验证 / 证据

### 1) 总入口页已显示最新 breakout 成本读法

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `20bps` 下 overall 平均单笔仍约 `+1.24%`、累计仍约 `+75.03%`
  - `test split` 在 `20bps` 下累计约 `-3.08%`
  - `up regime` 在 `20bps` 下累计约 `-2.98%`
  - `先补 split / regime honesty`

### 2) breakout 线在 closure board 里的读法更准确了

这轮之后，closure board 对 breakout 线的项目级口径变成：
- 不是“轻微成本一扣就塌”的弱原型；
- 但也不是可以忽略后段与环境依赖、直接往 production short 包装的对象；
- 当前更诚实的下一步是：`split / regime honesty`，不是继续扩 breakout 变体。

## 风险 / 边界

1. 这轮是 **总入口页证据同步**，不是新回测；
2. 没有新增交易数据，只是把上一轮已得到的关键数值提升到更上位的决策页；
3. 但这能避免 Jerry 从总入口页看到过时的 breakout 证据口径。

## 下一步建议

下一步最值得接的仍是：
1. `support_breakout_raw @ h24` 的 `split / regime honesty` 小页；
2. 或把 `avoid_fluctuating` 与 `trade_all` 放到同一成本口径下做最小对照。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `scripts/build_alpha_closure_board_report.py` 与 `reports/site/factors/alpha_closure_board/report.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
