# Rank 386 — survivor 唯一 follow-up（时间稳定性 + execution realism）

- 时间：2026-04-12 05:51 UTC
- 执行器：bot3
- 对象：`Rank 386 / SOL retail-more-short-than-top account divergence long-only shell`
- 上游记录：`research/optimization_loop/2026-04-12_0527_rank386_sol_retailtop_firstverdict_keep_p1.md`
- 本轮结论：`background/P0`（不晋升 P2）

## 本轮最小 follow-up 复核
数据源：
- `reports/artifacts/literature/lsr_account_divergence_probe_2026-04-12/detail.csv`

口径：沿用上一轮统一摩擦 `8 bps` roundtrip；仅检验 long leg（`sig=1`, `spread_z<-1.5`）的时间稳定性与最小 execution realism 同窗性。

### 1) 时间稳定性（按触发样本时间顺序三等分）
- seg1（n=65，2026-03-27~2026-04-01）：
  - 30m mean `+25.62 bps`（net `+17.62 bps`）
  - 60m mean `+24.61 bps`（net `+16.61 bps`）
- seg2（n=66，2026-04-01~2026-04-05）：
  - 30m mean `+12.51 bps`（net `+4.51 bps`）
  - 60m mean `+28.91 bps`（net `+20.91 bps`）
- seg3（n=66，2026-04-05~2026-04-11）：
  - 30m mean `+2.39 bps`（net `-5.61 bps`）
  - 60m mean `-4.51 bps`（net `-12.51 bps`）

结论：边际在最近分段明显塌陷并转负，收益并非稳定跨段留存，存在“主要由前段波动期驱动”的强迹象。

### 2) honesty / execution realism 最小检查（同窗性）
检查项：信号发布时间与可成交窗口是否同窗。

最小核验结果：
- `SOLUSDT` 时间戳全部落在 5 分钟整点栅格（无非 5 分钟对齐样本）；
- 抽样复算 `ret6`（`close[t+6]/close[t]-1`）与文件值一致（mismatch=0/120）。

结论：未发现“收益使用了晚于信号可成交窗口的数据”这一类前视同窗性问题；本轮 decisive blocker 不是 honesty 泄漏，而是时间稳定性不足。

## 出口决策
- 决策：`background/P0`
- 唯一 decisive blocker：`time stability`（最近分段在统一摩擦后净边际转负，无法支持晋升 P2）
- 系统认知更新（一句话）：
  - `Rank 386` 的正边际主要集中于早段波动期，最近分段成本后转负，不满足 survivor->P2 所需的跨段稳定性，故本轮直接收口至 `background/P0`。
