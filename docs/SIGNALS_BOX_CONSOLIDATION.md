# SIGNALS_BOX_CONSOLIDATION（横盘/箱体建仓信号）

## 1. 目标
把主观交易语言转换为可回测的量化信号，覆盖 **指数 + 个股**：

1) **窄幅震荡建仓**（narrow accumulation）  
2) **箱体震荡突破建仓**（box breakout accumulation）

输出在 `src/momentum/signals/box_consolidation.py`：
- `narrow_accum_ready`
- `box_breakout_ready`
- `accumulation_ready`（两者并集）

---

## 2. 主观概念 -> 量化定义

| 主观概念 | 量化代理定义（默认） | 对应主流概念 |
|---|---|---|
| 进入箱体前一波下跌 | `drawdown_from_peak <= -12%`（`decline_lookback=60`），且近 `20` 日出现过该下跌 | 先验下行趋势（prior downtrend） |
| 收盘不创新低（阴线最低点） | 计算 `bearish_floor = rolling_min(low where close<open)`；要求 close 连续 `5` 日 > `bearish_floor` | 支撑位守住（support holding） |
| 窄幅震荡 | `narrow_box_width <= 8%` 且 `ATR/Close <= 2.5%` | 波动收缩（Volatility Contraction / Squeeze） |
| 上涨浪信号确立 | `upwave` 在近 `20` 日至少出现一次 | 趋势恢复确认 |
| 箱体震荡（振幅更大） | `box_width` 在 `[8%,30%]`，且近窗口内 up/down wave 均出现 | Donchian 式区间交易框架 |
| 下跌浪不破前低 | 最近 downwave 收盘 >= 前一次 downwave 收盘 | 更高低点（Higher Low） |
| 上涨浪不破前高 | 最近 upwave 收盘 <= 前一次 upwave 收盘 | 不创新高、区间上沿压制 |
| 阳线突破箱体上沿 | `close>open` 且 `close > box_high_prev*(1+buffer)` | 区间突破（breakout close） |
| 底部筹码顶格 | 可选 chip 过滤：`chip_bottom_locked` 或 `winner_ratio` 在区间内 | 筹码集中（需外部 chip 数据） |

---

## 3. 信号逻辑（默认）

### 3.1 窄幅震荡建仓 `narrow_accum_ready`
同时满足：

- 有近期下跌：`prior_decline_recent == 1`
- 连续 5 日收盘站上历史阴线低点：`floor_hold_ok == 1`
- 波动收缩：`narrow_box_ok == 1`
- 近期出现上涨浪：`upwave_recent == 1`
- （可选）筹码过滤通过：`chip_ok == 1`

### 3.2 箱体突破建仓 `box_breakout_ready`
同时满足：

- 有近期下跌：`prior_decline_recent == 1`
- 箱体窗口内同时出现 upwave/downwave
- 下跌浪不破前低：`down_non_break == 1`
- 上涨浪不破前高：`up_non_break == 1`
- 箱体振幅在定义区间：`box_width_ok == 1`
- 阳线向上突破箱体上沿：`box_breakout == 1`
- （可选）筹码过滤通过：`chip_ok == 1`

### 3.3 总信号
`accumulation_ready = narrow_accum_ready OR box_breakout_ready`

---

## 4. 参数建议（第一版）

- `min_decline_pct`: 8%~15%（指数偏低，个股偏高）
- `narrow_range_max`: 5%~10%
- `narrow_atr_ratio_max`: 2.0%~3.0%
- `box_range_min/max`: 8%~30%
- `floor_hold_days`: 5~8

建议先在 `long_only` 下做事件回测，优先看：
- 成本后收益
- 回撤
- 参数邻域稳定性（不是单点最优）

---

## 5. 使用方式

```bash
cd jerry/momentum
source .venv/bin/activate

python scripts/build_box_consolidation_signals.py
```

配置文件：`config/signals/box_consolidation.yaml`

---

## 6. 参考文献（用于概念映射）

> 说明：这里用于“概念对齐”，不是逐字复刻某一本书的交易规则。

1. John Bollinger, *Bollinger on Bollinger Bands*（波动收缩与带宽概念）  
2. Richard Donchian / Donchian Channel（区间上沿突破框架）  
3. Wyckoff Method（吸筹-整理-突破的市场结构思想）  
4. Lo, Mamaysky, Wang (2000), *Foundations of Technical Analysis*（图形/技术规则可量化化）  
5. Minervini VCP（Volatility Contraction Pattern，窄幅收敛后突破）
