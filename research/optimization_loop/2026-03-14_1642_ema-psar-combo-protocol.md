# EMA + PSAR 最小组合协议写回主报告

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不直接开组合回测，而是先把另一个还没写死的关键问题收口：**如果后面真要做 `EMA + PSAR`，最小版本到底该怎么定义，才不至于一上来就做成“两个 alpha 拼盘”。**

之所以选这个点：
1. `docs/TODO.md` 里 `EMA + PSAR` 最小组合研究仍是明确未完成项；
2. 当前页面已经把 `EMA` 的 rolling / OOS first falsification slice 写清了，但组合任务还缺一个同样明确的最小协议；
3. 在 13 分钟节奏下，先把组合协议写死，比仓促补一个半成品组合回测更诚实，也更能直接帮助后续策略研发。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 在 `EMA / PSAR Raw Alpha Focus Report` 中新增 **Q12：如果要做最小 EMA + PSAR 组合，怎样才算诚实？**
   - 这段现在明确写死：
     - `EMA` 负责主方向 / 默认持有；
     - `PSAR` 不抢主 alpha 位，只负责更快退出 / protective overlay；
     - 组合版必须与 `单跑 EMA` 在同一资产、同一频率、同一资金与成本口径下正面对比；
     - 至少同时报告 `gross + 20bps`；
     - 若只先做一个最小切片，当前默认优先 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m`。
   - 原边界段顺延为 `Q13`。
2. 更新 `docs/TODO.md`
   - 在 `做一版 EMA + PSAR 的最小组合研究` 两处开放任务下都补上 `最小组合协议 v1` 的最新进度说明；
   - 任务仍保持未完成，因为本轮完成的是**协议收口**，不是正式组合回测结果。
3. 重建可见产物：
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 主报告已出现新的组合协议段

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q12. 如果要做最小 EMA + PSAR 组合，怎样才算诚实？`
- 新段里已明确出现：`EMA 60m + PSAR exit overlay`
- 原边界段已顺延为 `Q13`

这说明本轮不是只在日志里提建议，而是已经把组合任务的默认做法写进了网页。

### 2) 当前为什么先做 `EMA 60m + PSAR exit overlay`

当前固定下来的读法是：
- `EMA 60m` 本来就是主 baseline 里最脆的一块；
- 它在 first-pass 成本里，positive-only median breakeven cost 约 `27.5bps`，扣 `20bps` 后只剩约 `4/9` 组合存活；
- 同时 `PSAR 60m` 又正是最可能提供“更快退出 / 保护性反应”价值、但也最容易被成本吞掉的地方；
- 所以如果要先做一个最小组合 slice，优先拿这块做 falsification / honesty 对照最合适。

### 3) TODO / plans 镜像已同步

验证命中：
- `docs/TODO.md` 已出现 `最小组合协议 v1` 的进度说明；
- `reports/site/plans/momentum_todo.html` 也已同步出现同样口径。

这说明本轮产出不只停留在主报告，也同步到了站点可见的计划面板。

### 4) 最小技术验证通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

结果：
- 两个脚本都成功执行；
- `build_ema_psar_raw_alpha_report.py` 期间只有 matplotlib 中文字体 warning；
- 无阻塞性报错。

## 风险 / 边界

1. 这轮是 **组合协议 / 页面收口**，不是新组合回测；
2. 没有新增 `EMA + PSAR` 的收益、回撤或窗口统计；
3. 但它确实把“组合任务最小该怎么做、先从哪里开始、怎样才算诚实”写成了可执行协议，能减少后续把组合研究做散的风险。

## 下一步建议

下一步最值得接的就是：
1. 真做一版 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m` 的最小组合切片；
2. 优先回答三件事：
   - `20bps` 下坏窗口是否减少；
   - 回撤 / 误伤是否改善；
   - 交易次数增加后，组合增益是否还能盖过成本。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
