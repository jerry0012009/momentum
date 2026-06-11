# bot3 执行日志 — Rank 397 fresh intake first verdict（ETH downside outlier fade）

- 时间：2026-04-13 07:04 UTC
- 执行动作：`cycle_plan` 第 2 项（fresh intake first-verdict）
- 目标对象：`research/quant_digests/2026-04-13_0639_eth-downside-outlier-fade-alpha.md`

## 结论（会改变系统认知）
- 为该 fresh intake 分配正式 `Rank 397`。
- `ETH downside outlier fade × Europe-hours veto` 判定为 `keep_P1`（不进 `P2`）。
- 唯一 survivor blocker 锁定为：**缺少同口径 `5m` 执行层（next-5m 进场/微结构等待进场）在滚动时段切片下的费后稳健性证据**；当前仅有 `15m` 触发 + next-bar 执行近似，尚未完成执行层 realism 封口。

## 本轮最小证据
### 1) intake 主证据复核（来自现有 probe）
- ETH, z=3, hold=60m, 全样本：`170` 次，`gross_mean_bps=+10.08`
- ETH, z=3, hold=60m, `asia_us`：`96` 次，`gross_mean_bps=+36.66`
- ETH, z=3, hold=60m, `eu_08_16`：`74` 次，`gross_mean_bps=-24.40`
- 说明：Europe-hours veto 对该 alpha 为必要条件，不是可选修饰。

### 2) honesty / execution realism 子检查（本轮新增）
按“事件在 bar close 才可见，下一根 bar open 执行”的更诚实口径重算 ETH z=3：
- `ret60`（入场 next-open，持有 4 根后 close 退出）
  - all: `170` 次，`gross_mean_bps=+7.24`，`net@8bps=-0.76`
  - asia_us: `96` 次，`gross_mean_bps=+30.63`，`net@8bps=+22.63`
  - eu_08_16: `74` 次，`gross_mean_bps=-23.11`，`net@8bps=-31.11`
- `ret120`（入场 next-open，持有 8 根后 close 退出）
  - all: `170` 次，`gross_mean_bps=+14.75`，`net@8bps=+6.75`
  - asia_us: `96` 次，`gross_mean_bps=+33.16`，`net@8bps=+25.16`
  - eu_08_16: `74` 次，`gross_mean_bps=-9.13`，`net@8bps=-17.13`

解释：在去除事件同 bar 的潜在对齐偏差后，alpha 并未失真；但 edge 明显依赖 session 过滤，且是否可交易仍取决于 `5m` 执行层摩擦与成交路径。

## 本轮判定
- `fresh intake first verdict = keep_P1`
- 不升 `P2`：因为尚未形成“5m 执行层 + 滚动切片 + 统一摩擦口径”的单一 decisive 通过证据。
- survivor follow-up（唯一一次）应只做一件事：
  - 在 `ETHUSDT`、`z in {2.5,3.0,3.5}` 与 Europe-hours veto 下，比较 `next-5m immediate` vs `micro lower-low fail` 两种执行；
  - 统一 round-trip 成本（至少 8bps）+ 滚动切片（time stability）；
  - 产出是否可 `promote_P2` 的封口答案。

## 尾部执行
- 首页刷新（best-effort）：已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，该进程未在预期窗口内返回并已终止；按规则记为非阻断尾部失败，不回滚本轮结论。
- 邮件通知：`send_text_email.py` 执行成功（sent）。
