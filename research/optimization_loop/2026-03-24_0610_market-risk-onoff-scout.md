# bot3 optimization loop — 2026-03-24 06:10 UTC — market risk-on/off scout

## 路径判断
- 顶板读取结果：`Paper launch queue = none`、`Fresh intake = open`、`Surviving candidate = none`、`Active P2 = none`
- 本轮路径：`Scout / fresh intake`
- 认领动作：按 `Next 3 bot3 runs` 执行 `fresh intake`

## 本轮主点
- 新认领并落地一条 fresh intake：`market risk-on/off regime gate`（15m crypto clean-room spec）
- 执行动作：运行 `python3 scripts/build_market_risk_onoff_scout_spec.py`
- 产物：
  - artifact: `reports/artifacts/scout_market_risk_onoff_15m/clean_room_spec_v1.csv`
  - meta: `reports/artifacts/scout_market_risk_onoff_15m/spec_meta.csv`
  - 网页: `reports/site/factors/scout_market_risk_onoff_15m/report.html`

## 紧邻子点
- 同步刷新首页入口并发布站点：`bash scripts/publish_homepage_index.sh`
- 发布结果：
  - 本地首页：`reports/site/index.html`
  - 外网入口：`https://jp.jerrypsy.top/momentum/`

## 为什么这步最有杠杆
- 当前 desk board 明确要求优先 `fresh intake`，而不是回头重磨 background pool/旧 compare。
- 这条 intake 直接把 `Svogun & Bazán-Palomino (2022)` 的“成本生存性依赖 market regime”压成可实现的 `1h gate + 15m execution` 规格，能最短路径接到下一轮 clean replication。
- 相比继续补旧 wiring/旧 wording，这一步留下了可验证、可交付、可继续推进的明确输入件。

## 简短 scorecard
- seat legality: `PASS`（fresh intake，符合当前 policy/state）
- leverage: `PASS`（直接形成 implementation-ready spec，而非重复解释）
- verifiability: `PASS`（artifact + site page + homepage publish 均已落地）
- reader-facing output: `PASS`（新网页已可见）
- overreach control: `PASS`（只做 source intake + spec；未伪装成 clean replication / paper candidate）

## 当前 hard verdict
- `guard-passed / implementation-ready clean-room spec`
- 还不是 paper candidate；下一轮最自然动作应是复用现有 `market_risk_on_off_filter.py` 与 Binance 15m cache，补四档最小 clean replication：
  - `baseline_mtf`
  - `trend_only_gate`
  - `market_risk_2of3`
  - `market_risk_3of3`

## 备注
- 本轮未触碰 `Paper launch` / `P2 admission`，因为顶板对应槽位均为 `none`。
- 本轮也未去 reopen background pool 旧对象，符合 `do_not_auto_reopen`。
