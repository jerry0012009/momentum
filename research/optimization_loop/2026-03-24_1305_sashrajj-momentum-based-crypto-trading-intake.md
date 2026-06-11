# bot3 自动优化日志：SashRajj/Momentum-Based-Crypto-Trading fresh intake

- 时间：2026-03-24 13:05 UTC
- 路径判断：Scout
- 主点：fresh intake
- 紧邻子点：repo README / 公开结构诚实性快检
- 认领动作：`cycle_plan` 第 2 项

## 本轮执行
1. 读取 `BOT2_BOT3_POLICY.md` 与 `BOT2_BOT3_STATE.md`，确认当前前排无 `Active P2` 与 `Surviving candidate`，本轮合法主线为 fresh intake。
2. 认领未在当前 runtime / 既有研究记录中出现过的公开 repo：`SashRajj/Momentum-Based-Crypto-Trading`。
3. 读取 GitHub repo 页面与原始 `README.md`，核对其是否给出足够支持 `keep_P1` 的 clean-room 复现入口、样本边界、诚实性钩子与最小执行口径。
4. 只做 first verdict，不扩展为深度复现或 admission 工程。

## 本轮观察
- repo 对外给出的核心内容主要是 `README.md` + 单个 notebook；公开材料里能看到的是“volume-adjusted momentum + dynamic portfolio weighting + stop-loss + backtesting”。
- README 给出了一组非常强的汇总绩效数字（Gross Return `1137.37%`、Net Return `769.64%`、Net Sharpe `1.69`），但没有同时给出样本起止、训练/验证切分、再训练规则、持仓/换手约束、成本口径细节、滑点建模、是否存在参数搜索后回看挑选。
- README 虽然声称“includes transaction costs”，但公开入口没有把 cost model、trade frequency、rebalance 规则和 leakage guard 讲清楚；当前更像展示型项目，而不是可直接进入最小诚实 follow-up 的研究骨架。
- 需要配置 Binance API credentials 这一点本身不是问题，但在当前公开入口下，它并没有把“如何用同一规则重建结果”讲到足以支持 `keep_P1` 的程度。

## 本轮结论
- verdict：`park`
- 一句话结果：`SashRajj/Momentum-Based-Crypto-Trading` fresh intake 完成后直接 park：当前公开材料只有高层 README 指标与 notebook 壳，缺少能支撑 keep_P1 的 clean-room 样本边界、成本/换手口径与抗泄漏说明，不值得占用唯一 follow-up 预算。

## 为什么不是 keep_P1
- 还没有一个足够清楚的“下一步只补一刀就能改变层级”的 blocker；缺口是成套的，不是单点的。
- 若继续推进，下一步会被迫变成大范围源码/实验重建，而不是 policy 允许的便宜、决定性 follow-up。
- 因此最诚实的 first verdict 是直接 `park`，把证据留档，不给前排制造伪希望。

## 落档
- 外部来源：
  - `https://github.com/SashRajj/Momentum-Based-Crypto-Trading`
  - `https://raw.githubusercontent.com/SashRajj/Momentum-Based-Crypto-Trading/main/README.md`
- 本轮未分配 Rank；原因：结论未达到 `keep_P1`。
