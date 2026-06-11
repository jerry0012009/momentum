# MEFAI scalping microtrend × volume-spike shell：fresh intake first verdict = background/P0

- 时间：2026-04-21 07:54 UTC
- 对象：`MEFAI scalping microtrend × volume-spike shell`
- 轮次角色：bot3 执行器
- 对应 cycle item：`research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`

## 本轮执行的小点
按 runtime `cycle_plan`，只做这一个 fresh intake 的 first verdict，并只补 1 个最小 decisive blocker：
在 `1m/5m` 可执行 child-entry、统一 `8bps` 与最小延迟确认口径下，确认这条壳是否仍保留可复制、非单一 symbol、且 recent slice 不塌的 after-cost pocket。

## 读取与证据
- digest：`research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`
- artifact：
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_summary_3m15m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_trades_2026-04-21.csv`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_trades_3m15m_2026-04-21.csv`

## 最小诚实结论
结论：**直接收口 `background/P0`，不保留 `keep_P1`。**

原因不是“repo 壳不完整”，而是最小 public-data 诚实口径下，它没有证明自己在当前 liquid majors 上保留了可复制的 after-cost pocket：

1. `1m` 合并 8 个 liquid majors 共 `433` 笔，`gross_mean_bps≈-0.42`，统一粗扣 `8bps` round-trip 后显然更差；即便 digest 里较保守地只展示 `4bps` proxy，净值也已约 `-4.42bps/trade`。
2. `5m` 合并共 `483` 笔，`gross_mean_bps≈-1.88`；同样在任何 `8bps` 口径下都不成立。
3. 更慢 portability sanity check 也没有救回来：
   - `3m gross_mean_bps≈-0.88`
   - `15m gross_mean_bps≈-4.08`
4. 单币层面没有出现“至少两个 symbol 在 recent slice 下还能穿过成本”的 survivor：
   - `1m` 最好的 `AVAX/BNB/BTC` 也只是 `gross≈+1.73/+0.97/+0.35bps`
   - `5m` 最好的 `BNB/ETH` 也只是 `gross≈+2.24/+1.42bps`
   这些都远低于统一 `8bps` round-trip。
5. recent slice 没有显示“旧样本好、最近样本更好”的改善。`scalping_microtrend_volspike_probe_trades_2026-04-21.csv` 中可见的 `2026-04` 合并结果共有 `916` 笔，`gross≈-1.19bps/trade`；同一 recent 文件下分币也没有形成非单一 symbol 的正 pocket（仅 `BNB≈+1.67bps`、`ETH≈+0.15bps`、`AVAX≈+0.13bps` 勉强非负，其余主要币种为负），仍明显不足以覆盖最小成本。
6. 止盈/止损结构也不支持“只差一点 execution realism”这种乐观解释：各周期 `SL rate` 普遍高于 `TP rate`，例如 `5m` 为 `TP 172` vs `SL 291`，`15m` 为 `TP 162` vs `SL 365`。这说明问题不是单纯缺一个轻微优化，而是 candle-only 退化版的 raw edge 本身未站稳。

## 对系统认知的改变
会改变系统认知的一句话：

> `MEFAI scalping microtrend × volume-spike shell` 在 liquid-major `1m/5m` child-entry、统一 `8bps` 与 recent `2026-04` 口径下未保住非单一 symbol 的 after-cost pocket；repo 的完整价值更像“盘口/价差 admission 研究提示”，而不是当前值得前排保留的独立 raw alpha，因此本轮直接收口 `background/P0`。

## runtime 回写要点
- `Fresh intake slot.latest_result` 更新为本次 `background/P0` 首判
- `Fresh intake slot.latest_result_record` 指向本日志
- `Background pool.latest_parked` 追加本对象收口结论
- `Background pool.latest_parked_record` 追加本日志
- `cycle_plan` 第 2 项写回 `done`

## 备注
这不是对 repo 完整壳的永久否定；只是当前轮次要求的最小首判已经足够回答：
若不引入逐秒盘口失衡 / spread admission 的明确增量证据，仅靠可复算的 `EMA micro-trend + volume spike + fixed TP/SL/time-stop` 退化版，当前不值得占用前排 survivor 配额。
## Tail step status
- homepage index refresh：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮无输出后被 SIGKILL，按 policy 记为非阻断尾部失败；不回滚 verdict / state / log。
- email summary：已发送到 `18810813576@163.com`。
