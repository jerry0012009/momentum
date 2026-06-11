# EMA first rolling slice 的 go / yellow / fail gate 写回决策页

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不去仓促开新回测，而是把一个真正会影响后续资源判断的关键问题先写死：**如果下一步先做 `EMA 60m gross vs 20bps` 的 rolling falsification slice，什么结果算继续推进，什么结果该降级？**

之所以选这个点：
1. `EMA / PSAR Raw Alpha Focus Report` 已经写明下一步默认先做 `EMA 60m` 的 rolling / walk-forward falsification；
2. 但在此之前，页面里还没有把“做完之后怎么判 go / no-go”说得足够硬；
3. 在 13 分钟节奏下，先把判定门槛写清，比匆忙补一版不诚实的 rolling 页更有价值，也更方便 Jerry 判断后面到底该不该继续往策略/实盘推进。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 在 `EMA / PSAR Raw Alpha Focus Report` 中新增一段：
     - **Q13. 如果先做完 EMA 60m 的最小 rolling falsification slice，什么结果算继续、什么结果算降级？**
   - 把 `EMA 60m` first slice 的判定写成三档：
     - `pass`：多数窗口仍为正，且 `gross -> 20bps` 后没有整排塌陷；
     - `yellow`：gross 还能看，但 `20bps` 后只剩少数窗口 / 少数资产在撑；
     - `fail`：rolling 后大部分窗口在 `20bps` 下都转负，或主要只靠少数大牛段 / 单一资产撑住。
   - 同时把原边界段顺延为 `Q14`。
2. 更新 `docs/TODO.md`
   - 在 `优先补 EMA 的成本 / rolling / OOS / 跨市场稳定性` 这条下补上同样的 `go / yellow / fail gate` 最新说明；
   - 并同步进 `reports/site/plans/momentum_todo.html`。
3. 重建可见产物
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 当前新增的关键结论

这轮没有新增回测数字，但把一个很重要的决策口径写死了：

- **继续推进（pass）**：`EMA 60m` rolling 后多数窗口仍为正，而且从 gross 扣到 `20bps` 没有整排窗口一起塌掉；
- **谨慎保留（yellow）**：gross 还能看，但 `20bps` 后只剩少数窗口 / 少数资产在撑；
- **直接降级（fail）**：rolling 后大部分窗口在 `20bps` 下都转负，或主要只靠少数大牛段 / 单一资产撑住，此时应把 EMA 从 `baseline candidate` 降回 `research branch`。

为什么先看 `EMA 60m`：
- 因为这块当前最薄、最适合先做 falsification；
- first-pass 成本里，`EMA 60m` 的 positive-only median breakeven cost 约 `27.5bps`；
- 扣 `20bps` 后只剩约 `4/9` 组合存活；
- 所以如果这里都明显站不住，就没必要急着把 EMA 往更高定位推。

## 验证 / 证据

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现：
  - `Q13. 如果先做完 EMA 60m 的最小 rolling falsification slice，什么结果算继续、什么结果算降级？`
  - `research branch`
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 也已同步出现：
  - `go / yellow / fail gate`

## 风险 / 边界

1. 这轮仍是 **决策门槛补强**，不是新 rolling 回测；
2. 没有新增窗口统计或净值曲线；
3. 但它确实把“下一轮 rolling slice 做完之后该怎样判继续 / 降级”写成了网页可见协议，减少后续边做边改口径的风险。

## 下一步建议

下一步最值得接的就是：
1. 真做一版 `EMA 60m gross vs 20bps` rolling / walk-forward falsification slice；
2. 如果这一步没有明显 fail，再接 `EMA + PSAR exit overlay` 的最小组合验证。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
