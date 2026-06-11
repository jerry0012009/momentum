# EMA / PSAR 页升级成更像策略决策页

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不再补新数字，而是把页面最后一块还不够“可决策”的地方补完：**如果今天就要排研发优先级，EMA 和 PSAR 到底该怎么投资源。**

之所以选这个点：
1. `docs/TODO.md` 里这条任务还没勾掉；
2. 页面虽然已经有角色判断和成本段，但还缺一段更像 `go / no-go gate` 的明确决策语言；
3. 这是一个足够小、又能直接落到网页可见产物的收口动作，符合当前 13 分钟节奏。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 在原有 `Q9 成本段` 之后新增：`Q10. 如果今天就要排研发优先级，EMA 和 PSAR 应该怎么投资源？`
   - 这一段现在明确回答四件事：
     - 第一优先级继续投给 `EMA`，但目标应收窄为 `rolling / OOS honesty`；
     - `PSAR` 不应单独扩成第二条主 alpha 线；
     - 更合理的是先做最小 `EMA + PSAR` 组合验证，看它是否更像快退出 / protective layer；
     - 真正的 `go / no-go gate` 是：EMA 下一轮 rolling / OOS 若还能保住大部分日/周频优势，才有资格正式升为项目的 `raw alpha baseline`。
   - 原 `Q10 边界` 顺延为 `Q11`。
2. 重建 `reports/site/factors/ema_psar_raw_alpha/report.html`
   - 新的决策段已正式进页，可直接在网站上看到。
3. 更新 `docs/TODO.md`
   - 将 `把 EMA / PSAR Raw Alpha Focus Report 升级成更接近策略决策页，而不只是阶段性研究页` 这条标记为完成；
   - 并补一句固定口径，避免后续又回到“只是阶段性研究摘要”的状态。

## 验证 / 证据

### 1) 网页已出现新的决策段

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q10. 如果今天就要排研发优先级，EMA 和 PSAR 应该怎么投资源？`
- 原边界段已顺延成 `Q11. 这页的边界是什么？`

这说明本轮结果已经真的落到网页，而不是只停留在日志或 TODO。

### 2) 当前决策口径被写得更死了

这轮之后，EMA / PSAR 线的项目级读法更明确：
- `EMA` 继续保留为 **主 raw alpha baseline 候选**；
- 但下一步不是继续堆“它为什么强”的论述，而是优先补 **rolling / OOS honesty**；
- `PSAR` 当前不单独扩成第二条主 alpha，而是优先作为 **fast reaction / protective layer 候选** 放进最小 `EMA + PSAR` 组合验证。

### 3) 最小技术验证通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`

结果：
- 成功重建报告；
- 期间只有 matplotlib 中文字体 warning；
- 无阻塞性报错。

## 风险 / 边界

1. 这轮是 **决策表达收口**，不是新回测；
2. 因此没有新增 rolling / OOS 数据，只是把“下一步该怎么投资源”写成了更可执行的页面语言；
3. 真正决定 EMA 能否正式升成 baseline 的，仍然是下一轮 rolling / OOS honesty，而不是这轮文案本身。

## 下一步建议

下一步最值得接的仍是：
1. `EMA` 的 rolling / OOS honesty；
2. `EMA + PSAR` 最小组合验证，回答 `PSAR` 当快退出 / protective layer 时，是否比单跑 EMA 更诚实。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html` 这些路径本身在本轮开始前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮变更。