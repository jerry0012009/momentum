# 2026-03-17 07:24 UTC · Rank 26 ETH+SOL 最小诚实检查后压回 park

## 为什么这轮选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - `Paper Seat / EMA` 在 `07:04 UTC` 的 A 股 due-follow-up 已如实消化，当前全 desk 没有新的 `due-now / overdue` lane，因此 `EMA` 继续按 `waiting_not_due` 处理。
  - `Scout Seat` 当前 active 候选里，`Rank 17 / Rank 2` 都是 `P3 narrow paper pilot`，本轮未出现新的真实 `append/review need`。
  - 因此这轮最该做的，不是 fresh intake，也不是继续磨 P3 文档，而是把 `Rank 26 regime triplet state gate` 那 **1 次 genuinely verdict-changing 最小检查** 做完，直接回答：`升 P3 / 压回 park`。

## 本轮主点 + 紧邻子点
- 主点：对 `Rank 26` 做最小 narrow-scope recheck——不改规则、不追新 bar，只把 `BTC` 弱腿剥离，测试 `ETH+SOL-only` 是否足以升到 `narrow paper pilot`。
- 紧邻子点：把这次 hard verdict 写回 `docs/TODO.md` 顶部指挥板，并产出 reader-facing 网页落点。

## 先过诚实边界
1. **trade on / trade off 不变**
   - `trade on = baseline multi-tf momentum 同向，且 long 端满足 up_regime、short 端满足 down_regime（strict_up_down）`
   - `trade off = 基线方向缺失或状态门未过`
2. **不引入 lookahead / repaint / leakage**
   - 只复用既有 `BTC/ETH/SOL 120d 15m` 历史样本与现成回测链路；
   - 不追新 bar、不改参数、不换执行口径。

## 做了什么
### 1) 新增脚本
- `scripts/build_regime_triplet_narrow_scope_recheck.py`

### 2) 生成新增 artifact
- `reports/artifacts/scout_regime_triplet_15m/ethsol_scope_recheck.csv`
- `reports/artifacts/scout_regime_triplet_15m/ethsol_scope_time_recheck_15bps.csv`
- `reports/artifacts/scout_regime_triplet_15m/narrow_paper_pilot_ethsol_monitoring_board.csv`
- `reports/artifacts/scout_regime_triplet_15m/narrow_paper_pilot_ethsol_review_queue.csv`
- `reports/artifacts/scout_regime_triplet_15m/ethsol_scope_recheck_meta.csv`

### 3) 生成 reader-facing 网页落点
- `reports/site/factors/scout_regime_triplet_15m/ethsol_scope_recheck.html`

### 4) 写回指挥板
- 更新 `docs/TODO.md`：
  - 将 `Rank 26` 从 `paper candidate（P2）` 改写为 **`park / evidence pool`**；
  - 更新 `Next 3 bot3 runs` 顶部 authoritative override：`Rank 26` 这刀已做完，后续若 `Rank 17 / Rank 2` 仍无真实 `P3` need，则默认切到新的 fresh intake，而不是继续让 `Rank 26` 卡在研究态；
  - 更新 `Run 2 / 2s` 的条目口径，同步写清 ETH+SOL-only recheck 的结论。

## 关键结果（hard verdict）
### 原始 P2 证据仍成立
- `strict_up_down` 在 full scope（BTC/ETH/SOL）下：
  - `6bps/side ≈ +14.65%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 141`
  - `10bps/side ≈ +2.44%`
- 所以它此前进入 `paper candidate pool` 并不离谱。

### 这次 genuinely verdict-changing 最小检查
把 `BTC` 诚实剥离，只看 `ETH+SOL-only` 后：
- `6bps/side ≈ +31.90%`，`2/2` 资产为正
- `10bps/side ≈ +17.80%`，`2/2` 资产为正
- `15bps/side ≈ +2.29%`，但只剩 `1/2` 资产为正：
  - `ETH ≈ +9.89%`
  - `SOL ≈ -5.31%`
- `20bps/side ≈ -11.17%`

### 15bps 时间稳定性（ETH+SOL-only）
- `bucket_1 ≈ -8.44%`
- `bucket_2 ≈ +1.56%`
- `bucket_3 ≈ +2.45%`
- 即：`time positive buckets = 2/3`，但前段 bucket 仍明显转负，不是足够干净的 `P3 narrow paper pilot` 读法。

## 一句话结论
**Rank 26 的 narrow-scope 检查没有“爆雷到全盘归零”，但它也没有把这条线修成足够干净的 P3：ETH+SOL-only 到 15bps 只剩一条腿为正、而且时间前段仍有明显破口。按当前 desk 规则，这条线最诚实的去处是 `park / evidence pool`，而不是继续挂在 P2 等下一页说明。**

## 为什么这次选择 park，而不是继续留在 P2
- 用户当前要的是更快的 `promote / park`，不是让候选长期停在研究态；
- 这次检查已经直接打在最真实的 blocker 上：`BTC` 弱腿 + friction survivability；
- 检查后虽然 average 变好，但并没有形成足够干净的 narrow pilot：
  - `15bps` 只剩 `1/2` 资产为正；
  - 时间 bucket 仍然保留明显破口；
  - 因此继续把它挂在 `P2` 只会拖慢 Scout 吞吐，而不会改变当前 desk judgment。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_regime_triplet_narrow_scope_recheck.py`
2. `python3 scripts/build_regime_triplet_narrow_scope_recheck.py`
3. `sed -n '1,20p' reports/artifacts/scout_regime_triplet_15m/ethsol_scope_recheck.csv`
4. `sed -n '1,20p' reports/artifacts/scout_regime_triplet_15m/ethsol_scope_time_recheck_15bps.csv`

## reader-facing 落点
- 网页：`reports/site/factors/scout_regime_triplet_15m/ethsol_scope_recheck.html`
- Desk 指挥板镜像：`docs/TODO.md` 顶部 `TRADING DESK BOARD`（后续由 Control Tower 页面镜像）

## 风险 / 边界
- 本轮没有追最新 bar；
- 没有改 `Rank 26` 规则或参数；
- 没有同时打开第二个 fresh candidate；
- 这次 `park` 不是说这条线完全没信息量，而是说：**它已经用完当前默认 Scout 预算，不该继续占默认主资源**。

## 下一步建议
1. 继续维持 `Paper Seat / EMA = waiting_not_due` 的默认节奏，直到下一次真实 due window。
2. `Scout Seat` 先检查 `Rank 17 / Rank 2` 是否出现新的真实 `P3 append/review need`。
3. 如果仍然没有，就默认切到新的 `paper / repo based 5m / 15m crypto` fresh intake，不再围着 `Rank 26` 补近义说明。

## Git
- 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮不做 commit，避免混提。
