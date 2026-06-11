# 2026-03-18 02:36 UTC — Rank 32b scope promotion honesty：升到 P3 narrow paper pilot（full scope）

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行。
- `Run 1 / EMA` 仍处于 `running paper / waiting_not_due`：最新 authoritative board 继续指向 A 股 `07:00 UTC`、美股 `20:00 UTC`、Crypto `2026-03-19 00:00 UTC` 的下一次 due 窗口，因此这轮不能把 paper refresh 硬做成主点。
- 当前 active Scout 只有 `Rank 32b`，而它上一轮刚从 `P1` 升到 `P2 paper candidate`。按 desk 规则，这轮只允许再做 **1 个 truly verdict-changing 的最小检查**，优先回答：
  - 它到底需要缩成更窄 scope 才能升到 `P3`；
  - 还是 full scope 本身就已经足以进入 `narrow paper pilot`；
  - 若两者都不行，则应直接压回 `park`。

## 本轮主点
- **主点**：`Rank 32b` 的 `asset-leg / narrow-paper promotion honesty`。
- **紧邻子点**：补 1 份最小 `narrow_paper_monitoring_board.csv`，作为后续 `paper ledger / monitoring / review` 的起点。

## 做了什么
1. 新增脚本：
   - `scripts/build_rank32b_scope_promotion_check.py`
2. 固定复用现有 `BTC/ETH/SOL 120d 15m` cache 与既有冻结规则：
   - `remove spread-mid reclaim requirement`
   - 保留 `EMA cross + aligned slope floor`
   - 不追新 bar，不改参数，不改持有期
3. 只做 promotion honesty 所需的最小比较：
   - `full_scope = BTC + ETH + SOL`
   - `ethsol_only = ETH + SOL`（作为“去掉最弱腿 BTC 后会不会改变结论”的诚实对照）
4. 产出新 artifact：
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/scope_promotion_check.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/scope_promotion_asset_summary.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/scope_promotion_meta.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/narrow_paper_monitoring_board.csv`
5. 产出 reader-facing 页面：
   - `reports/site/factors/scout_rank32b_slope_floor_continuation_15m/scope_promotion_check.html`
6. 同步更新：
   - `reports/site/factors/scout_rank32b_slope_floor_continuation_15m/report.html`
   - `docs/TODO.md`

## 关键证据
### 1) full scope 在 promotion friction 下仍站得住
`scope_promotion_check.csv` 显示：
- `full_scope @ 15bps/side`：
  - `mean_total_return≈30.94%`
  - `positive_asset_ratio=3/3`
  - `mean_trades≈75.7`
- `full_scope @ 20bps/side`：
  - `mean_total_return≈21.11%`
  - `positive_asset_ratio=3/3`
  - `mean_trades≈75.7`

这很关键，因为它直接说明：**Rank 32b 不是必须先缩 scope 才能讲得通**。

### 2) weakest leg（BTC）仍偏薄，但没薄到该被剥离
`scope_promotion_asset_summary.csv` / 页面里的 `15/20bps per-asset honesty snapshot`：
- `BTC-USD`：
  - `15bps≈8.46%`
  - `20bps≈2.75%`
- `ETH-USD`：
  - `15bps≈14.88%`
  - `20bps≈5.72%`
- `SOL-USD`：
  - `15bps≈69.47%`
  - `20bps≈54.86%`

BTC 的确是三条腿里 friction buffer 最薄的一条，但它 **没有转负**，所以当前更诚实的读法是：
- `BTC = watch leg / friction-buffer watch`
- 而不是 `BTC = scope blocker`

### 3) 缩 scope 只会让 headline 更漂亮，不会改变升格判断
对照 `ETH+SOL-only`：
- `15bps≈42.18%`
- `20bps≈30.29%`
- 两档仍是 `positive_asset_ratio=2/2`

这说明若缩 scope，数字当然会更好看；但 **promotion verdict 并不依赖这次缩 scope**。因此当前不该把它写成 “只有 ETH+SOL-only 才配升 P3”。

## 硬结论
- **一句话结论**：`Rank 32b` 这轮通过了唯一那刀真正会改变 desk judgment 的 promotion honesty 检查，当前更诚实的定位应从 `P2 paper candidate` 升到 **`promote to narrow paper pilot approved（P3, full scope）`**。
- **为什么不是继续留在 P2**：因为继续停在 P2 已经不再减少真实不确定性；full scope 在 `15/20bps` 下都还保留 `3/3` 资产为正，足够回答“该不该进 paper-only narrow pilot”。
- **为什么不是缩成 ETH+SOL-only 再升**：因为缩 scope 只会让 headline 更漂亮，但不是当前升格所必需的条件。
- **为什么不是 park**：因为 decisive fail 并没有出现；相反，friction 下 full scope 仍然存活。

## 后续边界
- 这次升格只是 **paper-only narrow pilot**，不是 tiny-live 许可。
- 后续若继续认领 `Rank 32b`，默认只允许：
  - `paper ledger`
  - `monitoring`
  - `refresh`
  - `review`
  的最小接线，或一个真正会改变 paper verdict 的最小检查。
- 默认不应再继续给它追加 `source-intake / admission wording / promotion 近义文案`。

## 最小接线产物
- `narrow_paper_monitoring_board.csv` 已补齐，当前建议读法：
  - `BTC-USD`：`watch_btc_friction_buffer`
  - `ETH-USD`：`green_keep_in_scope`
  - `SOL-USD`：`green_keep_in_scope`

## 验证
- 运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank32b_scope_promotion_check.py`
- 脚本成功退出，并生成新的 CSV / HTML 落点。

## 提交情况
- 未提交。
- 原因：repo 里存在大量与本轮无关的脏文件；本轮只做了与 `Rank 32b` 直接相关的 selective 产物 / 页面 / TODO 局部写回，不适合混提。
