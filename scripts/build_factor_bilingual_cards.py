#!/usr/bin/env python3
"""Build bilingual factor cards for all canonical factors.

PM-14A: Generates machine-readable bilingual metadata layer.
Deterministic, template-based, no hand-written JSON.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from factor_formula_registry import REGISTRY
from factor_specs import FactorSpec

# ---------------------------------------------------------------------------
# Family-level bilingual templates
# ---------------------------------------------------------------------------

FAMILY_META: dict[str, dict] = {
    "momentum": {
        "family_en": "Momentum",
        "family_zh": "动量",
        "data_source_type": "MOMENTUM_REVERSAL",
        "intuition_template_en": "Measures price continuation over {lookback}h. Higher values indicate stronger recent upward drift.",
        "intuition_template_zh": "衡量{lookback}小时内的价格延续性。值越高表示近期向上漂移越强。",
        "direction_explanation": {
            "positive": ("Higher momentum suggests continued upward drift.", "更高的动量值暗示持续的向上漂移。"),
            "negative": ("Higher momentum suggests mean-reversion expected.", "更高的动量值暗示预期均值回归。"),
        },
    },
    "reversal": {
        "family_en": "Reversal",
        "family_zh": "反转",
        "data_source_type": "MOMENTUM_REVERSAL",
        "intuition_template_en": "Captures short-term mean-reversion after {lookback}h price moves. Formula is sign-inverted so higher = stronger prior loser.",
        "intuition_template_zh": "捕捉{lookback}小时价格变动后的短期均值回归。公式已取反，值越高=前期跌幅越大。",
        "direction_explanation": {
            "positive": ("Higher reversal value = stronger prior loser, expected to bounce.", "更高的反转值=前期跌幅越大，预期反弹。"),
        },
    },
    "volatility": {
        "family_en": "Volatility",
        "family_zh": "波动率",
        "data_source_type": "VOLATILITY",
        "intuition_template_en": "Measures return dispersion over {lookback}h. Higher volatility = larger typical price swings.",
        "intuition_template_zh": "衡量{lookback}小时内的收益离散度。波动率越高=典型价格波动越大。",
        "direction_explanation": {
            "negative": ("High volatility historically underperforms in crypto cross-section.", "高波动率在加密货币截面中历史上表现较差。"),
            "conditional": ("Direction depends on volatility regime.", "方向取决于波动率状态。"),
        },
    },
    "technical": {
        "family_en": "Technical",
        "family_zh": "技术指标",
        "data_source_type": "TECHNICAL",
        "intuition_template_en": "Classic technical indicator applied to {lookback}h bars.",
        "intuition_template_zh": "应用于{lookback}小时K线的经典技术指标。",
        "direction_explanation": {
            "positive": ("Higher reading suggests bullish conditions.", "较高读数暗示看涨条件。"),
            "negative": ("Higher reading suggests overbought, expect pullback.", "较高读数暗示超买，预期回调。"),
            "conditional": ("Direction depends on market regime.", "方向取决于市场状态。"),
        },
    },
    "technical_indicators": {
        "family_en": "Technical Indicators",
        "family_zh": "技术指标",
        "data_source_type": "TECHNICAL",
        "intuition_template_en": "Standard technical indicator with {lookback}h lookback.",
        "intuition_template_zh": "{lookback}小时回溯的标准技术指标。",
        "direction_explanation": {
            "positive": ("Higher reading suggests bullish momentum.", "较高读数暗示看涨动量。"),
            "negative": ("Higher reading suggests overbought conditions.", "较高读数暗示超买状态。"),
            "conditional": ("Direction depends on market regime.", "方向取决于市场状态。"),
        },
    },
    "wq101": {
        "family_en": "WorldQuant 101",
        "family_zh": "WorldQuant 101",
        "data_source_type": "HYBRID",
        "intuition_template_en": "Alpha formula from WQ101 paper, adapted for {lookback}h bars.",
        "intuition_template_zh": "源自WQ101论文的Alpha公式，适配{lookback}小时K线。",
        "direction_explanation": {
            "conditional": ("Direction intentionally left conditional to avoid post-hoc fitting. Empirical diagnostics required.", "方向故意设为条件式以避免事后拟合。需实证诊断。"),
        },
    },
    "alpha158": {
        "family_en": "Alpha158",
        "family_zh": "Alpha158",
        "data_source_type": "HYBRID",
        "intuition_template_en": "Alpha158-inspired formula adapted for perpetual futures.",
        "intuition_template_zh": "受Alpha158启发的公式，适配永续合约。",
        "direction_explanation": {
            "conditional": ("Direction set to conditional. Requires empirical diagnostics.", "方向设为条件式。需实证诊断。"),
        },
    },
    "alpha158_ohlcv": {
        "family_en": "Alpha158-OHLCV",
        "family_zh": "Alpha158-OHLCV",
        "data_source_type": "HYBRID",
        "intuition_template_en": "Alpha158-derived factor using OHLCV data.",
        "intuition_template_zh": "使用OHLCV数据的Alpha158衍生因子。",
        "direction_explanation": {
            "positive": ("Higher value suggests bullish signal.", "较高值暗示看涨信号。"),
            "negative": ("Higher value suggests bearish signal.", "较高值暗示看跌信号。"),
            "conditional": ("Direction set to conditional. Requires empirical diagnostics.", "方向设为条件式。需实证诊断。"),
        },
    },
    "alpha158_price": {
        "family_en": "Alpha158 Price",
        "family_zh": "Alpha158 价格标准化",
        "data_source_type": "HYBRID",
        "intuition_template_en": "Alpha158 normalized price-location feature over a {lookback}-bar lag window. It compares lagged OHLC levels with current close.",
        "intuition_template_zh": "Alpha158价格标准化特征，使用{lookback}根K线滞后窗口，将滞后的OHLC价位与当前收盘价比较。",
        "direction_explanation": {
            "conditional": ("Direction is conditional: normalized price-location can reflect continuation, reversal pressure, or redundant price level context.", "方向为条件式：标准化价格位置可能反映延续、反转压力，或仅提供冗余价格位置背景。"),
        },
    },
    "alpha158_volume": {
        "family_en": "Alpha158 Volume",
        "family_zh": "Alpha158 成交量标准化",
        "data_source_type": "HYBRID",
        "intuition_template_en": "Alpha158 lagged volume ratio over a {lookback}-bar window. It compares prior volume with current volume to diagnose short-horizon volume expansion or fade.",
        "intuition_template_zh": "Alpha158滞后成交量比率，使用{lookback}根K线窗口，将前期成交量与当前成交量比较，用于诊断短周期成交量扩张或衰退。",
        "direction_explanation": {
            "conditional": ("Direction is conditional: lagged/current volume can mark fading attention, fresh participation, stress selling, or redundant liquidity context.", "方向为条件式：滞后/当前成交量可能表示关注度衰退、新资金参与、压力抛售，或仅提供冗余流动性背景。"),
        },
    },
    "range_position": {
        "family_en": "Range Position",
        "family_zh": "区间位置",
        "data_source_type": "PRICE_POSITION",
        "intuition_template_en": "Measures where price sits within its {lookback}h range.",
        "intuition_template_zh": "衡量价格在{lookback}小时区间内的位置。",
        "direction_explanation": {
            "conditional": ("Near range top vs bottom depends on trend/momentum regime.", "接近区间顶部还是底部取决于趋势/动量状态。"),
        },
    },
    "price_position": {
        "family_en": "Price Position",
        "family_zh": "价格位置",
        "data_source_type": "PRICE_POSITION",
        "intuition_template_en": "Measures where current price sits relative to {lookback}h high-low range.",
        "intuition_template_zh": "衡量当前价格相对于{lookback}小时高低区间的位置。",
        "direction_explanation": {
            "conditional": ("Position near highs can mean breakout or overbought; context-dependent.", "接近高点可能意味着突破或超买；取决于上下文。"),
        },
    },
    "volume_liquidity": {
        "family_en": "Volume Z-Score",
        "family_zh": "成交量Z分数",
        "data_source_type": "VOLUME",
        "intuition_template_en": "Z-score of current volume vs {lookback}h rolling mean/std. Detects unusual volume spikes.",
        "intuition_template_zh": "当前成交量相对于{lookback}小时滚动均值/标准差的Z分数。检测异常成交量放大。",
        "direction_explanation": {
            "positive": ("High volume z-score suggests increased attention, may precede moves.", "高成交量Z分数暗示关注度增加，可能预示后续波动。"),
        },
    },
    "quote_volume_liquidity": {
        "family_en": "Quote Volume Z-Score",
        "family_zh": "成交额Z分数",
        "data_source_type": "VOLUME",
        "intuition_template_en": "Z-score of quote volume (USD notional) vs {lookback}h baseline.",
        "intuition_template_zh": "成交额（美元名义值）相对于{lookback}小时基线的Z分数。",
        "direction_explanation": {
            "positive": ("Elevated quote volume suggests institutional interest.", "成交额放大暗示机构关注。"),
            "conditional": ("Direction depends on volume-price relationship.", "方向取决于量价关系。"),
        },
    },
    "trend_ma": {
        "family_en": "Trend MA Gap",
        "family_zh": "均线差",
        "data_source_type": "TECHNICAL",
        "intuition_template_en": "Gap between short and long moving averages. Positive = short MA above long MA (uptrend).",
        "intuition_template_zh": "短期和长期均线之间的差距。正值=短期均线在长期均线上方（上升趋势）。",
        "direction_explanation": {
            "positive": ("Positive gap suggests uptrend continuation.", "正差距暗示上升趋势延续。"),
        },
    },
    "breakout": {
        "family_en": "Breakout Distance",
        "family_zh": "突破距离",
        "data_source_type": "PRICE_POSITION",
        "intuition_template_en": "How far price has moved beyond its {lookback}h high. Positive = new high.",
        "intuition_template_zh": "价格超越{lookback}小时高点的距离。正值=创新高。",
        "direction_explanation": {
            "positive": ("Positive breakout suggests trend continuation.", "正突破暗示趋势延续。"),
        },
    },
    "intraday_candle": {
        "family_en": "Intraday Candle",
        "family_zh": "日内K线",
        "data_source_type": "RANGE_CANDLE",
        "intuition_template_en": "Intraday candle pattern component (body/wick ratio).",
        "intuition_template_zh": "日内K线形态分量（实体/影线比率）。",
        "direction_explanation": {
            "positive": ("Larger body/longer lower wick suggests buying pressure.", "较大实体/较长下影线暗示买压。"),
            "negative": ("Longer upper wick suggests selling pressure.", "较长上影线暗示卖压。"),
            "conditional": ("Direction depends on candle context.", "方向取决于K线上下文。"),
        },
    },
    "cross_sectional_normalized": {
        "family_en": "Cross-Sectional Rank",
        "family_zh": "截面排名",
        "data_source_type": "CROSS_SECTIONAL",
        "intuition_template_en": "Cross-sectional rank of {lookback}h metric across all symbols.",
        "intuition_template_zh": "{lookback}小时指标在所有标的中的截面排名。",
        "direction_explanation": {
            "conditional": ("Direction depends on which metric is ranked.", "方向取决于被排名的指标。"),
        },
    },
    "realized_skew_kurtosis": {
        "family_en": "Realized Skew/Kurtosis",
        "family_zh": "已实现偏度/峰度",
        "data_source_type": "VOLATILITY",
        "intuition_template_en": "Higher-order return distribution moment over {lookback}h.",
        "intuition_template_zh": "{lookback}小时内的高阶收益分布矩。",
        "direction_explanation": {
            "negative": ("Negative skew / high kurtosis historically penalized.", "负偏度/高峰度在历史上被惩罚。"),
            "conditional": ("Direction depends on distribution shape.", "方向取决于分布形态。"),
        },
    },
    "realized_shape": {
        "family_en": "Realized Shape",
        "family_zh": "已实现形态",
        "data_source_type": "VOLATILITY",
        "intuition_template_en": "Return distribution shape metric over {lookback}h window.",
        "intuition_template_zh": "{lookback}小时窗口的收益分布形态指标。",
        "direction_explanation": {
            "conditional": ("Direction depends on distribution shape vs market regime.", "方向取决于分布形态与市场状态。"),
        },
    },
    "taker_imbalance": {
        "family_en": "Taker Buy Imbalance",
        "family_zh": "主动买入失衡",
        "data_source_type": "TAKER_FLOW",
        "intuition_template_en": "Measures taker buy vs sell pressure over {lookback}h. Requires taker-enriched bars.",
        "intuition_template_zh": "衡量{lookback}小时内的主动买卖压力。需要taker增强数据。",
        "direction_explanation": {
            "positive": ("Higher taker buy ratio = more aggressive buying, may precede upward moves.", "更高的主动买入比率=更激进的买入，可能预示上涨。"),
        },
    },
    "funding_rate": {
        "family_en": "Funding Rate",
        "family_zh": "资金费率",
        "data_source_type": "FUNDING_RATE",
        "intuition_template_en": "Perpetual funding rate metric over {lookback}h. High funding = crowded long.",
        "intuition_template_zh": "{lookback}小时永续资金费率指标。高资金费率=拥挤多头。",
        "direction_explanation": {
            "negative": ("High funding = crowded long, expect mean-reversion / long squeeze.", "高资金费率=拥挤多头，预期均值回归/多头踩踏。"),
        },
    },
    "liquidity": {
        "family_en": "Liquidity",
        "family_zh": "流动性",
        "data_source_type": "VOLUME",
        "intuition_template_en": "Liquidity/illiquidity metric over {lookback}h.",
        "intuition_template_zh": "{lookback}小时流动性/非流动性指标。",
        "direction_explanation": {
            "negative": ("Higher illiquidity penalized in cross-sectional sorting.", "更高的非流动性在截面排序中被惩罚。"),
            "conditional": ("Direction depends on liquidity regime.", "方向取决于流动性状态。"),
        },
    },
    "volume_price": {
        "family_en": "Volume-Price",
        "family_zh": "量价",
        "data_source_type": "HYBRID",
        "intuition_template_en": "Volume-price relationship metric over {lookback}h.",
        "intuition_template_zh": "{lookback}小时量价关系指标。",
        "direction_explanation": {
            "conditional": ("Direction depends on correlation sign and market regime.", "方向取决于相关性符号和市场状态。"),
        },
    },
    "trend_quality": {
        "family_en": "Trend Quality",
        "family_zh": "趋势质量",
        "data_source_type": "TECHNICAL",
        "intuition_template_en": "Measures how efficiently price moves directionally over {lookback}h.",
        "intuition_template_zh": "衡量{lookback}小时内价格定向移动的效率。",
        "direction_explanation": {
            "positive": ("Higher efficiency = cleaner directional move, trend continuation likely.", "更高效率=更干净的定向移动，趋势延续可能性大。"),
        },
    },
}

# ---------------------------------------------------------------------------
# Per-factor name overrides (factor_id -> name)
# ---------------------------------------------------------------------------

FACTOR_NAMES: dict[str, tuple[str, str]] = {
    "mom_20h": ("20h Momentum", "20小时动量"),
    "mom_5h": ("5h Momentum", "5小时动量"),
    "mom_10h": ("10h Momentum", "10小时动量"),
    "mom_40h": ("40h Momentum", "40小时动量"),
    "mom_72h": ("72h Momentum", "72小时动量"),
    "mom_120h": ("120h Momentum", "120小时动量"),
    "mom_accel_20h": ("20h Momentum Acceleration", "20小时动量加速度"),
    "reversal_5h": ("5h Reversal", "5小时反转"),
    "rev_1h": ("1h Reversal", "1小时反转"),
    "rev_3h": ("3h Reversal", "3小时反转"),
    "rev_10h": ("10h Reversal", "10小时反转"),
    "rev_24h": ("24h Reversal", "24小时反转"),
    "rev_72h": ("72h Reversal", "72小时反转"),
    "volatility_20h": ("20h Volatility", "20小时波动率"),
    "vol_5h": ("5h Volatility", "5小时波动率"),
    "vol_40h": ("40h Volatility", "40小时波动率"),
    "vol_ratio_5_20": ("Vol Ratio 5/20", "波动率比 5/20"),
    "vol_ratio_20_80": ("Vol Ratio 20/80", "波动率比 20/80"),
    "rsi_14h": ("14h RSI", "14小时RSI"),
    "rsi_7h": ("7h RSI", "7小时RSI"),
    "rsi_28h": ("28h RSI", "28小时RSI"),
    "bb_zscore_20h": ("20h Bollinger Z-Score", "20小时布林Z分数"),
    "wq101_alpha101": ("WQ101 Alpha101", "WQ101 Alpha101"),
    "wq101_alpha12": ("WQ101 Alpha12", "WQ101 Alpha12"),
    "wq101_alpha53": ("WQ101 Alpha53", "WQ101 Alpha53"),
    "wq101_alpha6": ("WQ101 Alpha6 Open-Volume Corr", "WQ101 Alpha6 开盘量相关"),
    "wq101_alpha9": ("WQ101 Alpha9 Delta State", "WQ101 Alpha9 价格变化状态"),
    "wq101_alpha21": ("WQ101 Alpha21 Mean/Volume State", "WQ101 Alpha21 均值成交量状态"),
    "wq101_alpha41": ("WQ101 Alpha41 Range VWAP Gap", "WQ101 Alpha41 区间VWAP差"),
    "wq101_alpha54": ("WQ101 Alpha54 OHLC Power Ratio", "WQ101 Alpha54 OHLC幂比率"),
    "wq101_alpha23": ("WQ101 Alpha23 High Breakout State", "WQ101 Alpha23 高价突破状态"),
    "wq101_alpha24": ("WQ101 Alpha24 Mean Drift State", "WQ101 Alpha24 均值漂移状态"),
    "wq101_alpha46": ("WQ101 Alpha46 Close Slope State", "WQ101 Alpha46 收盘斜率状态"),
    "wq101_alpha49": ("WQ101 Alpha49 Close Slope State", "WQ101 Alpha49 收盘斜率状态"),
    "wq101_alpha51": ("WQ101 Alpha51 Close Slope State", "WQ101 Alpha51 收盘斜率状态"),
    "wq101_alpha32": ("WQ101 Alpha32 Mean Reversion VWAP Corr", "WQ101 Alpha32 均值回归VWAP相关"),
    "wq101_alpha33": ("WQ101 Alpha33 Intrabar Return Rank", "WQ101 Alpha33 K线内收益排名"),
    "wq101_alpha37": ("WQ101 Alpha37 Open-Close Corr Rank", "WQ101 Alpha37 开收差相关排名"),
    "wq101_alpha38": ("WQ101 Alpha38 TS Rank / Close-Open Rank", "WQ101 Alpha38 时序排名与收开比排名"),
    "wq101_alpha44": ("WQ101 Alpha44 High-Volume Rank Corr", "WQ101 Alpha44 高价成交量排名相关"),
    "wq101_alpha45": ("WQ101 Alpha45 Delayed Close / Volume Corr", "WQ101 Alpha45 滞后收盘量价相关"),
    "wq101_alpha34": ("WQ101 Alpha34 Vol Ratio / Delta Rank", "WQ101 Alpha34 波动比与价格变化排名"),
    "wq101_alpha40": ("WQ101 Alpha40 High Volatility Corr", "WQ101 Alpha40 高价波动相关"),
    "wq101_alpha42": ("WQ101 Alpha42 VWAP-Close Rank Ratio", "WQ101 Alpha42 VWAP收盘排名比"),
    "wq101_alpha50": ("WQ101 Alpha50 Ranked VWAP-Volume Corr", "WQ101 Alpha50 VWAP成交量排名相关"),
    "wq101_alpha55": ("WQ101 Alpha55 Range Position Volume Corr", "WQ101 Alpha55 区间位置成交量相关"),
    "wq101_alpha60": ("WQ101 Alpha60 Close-Location Volume Scale", "WQ101 Alpha60 收盘位置成交量缩放"),
    "q158_high_low_range": ("Alpha158 High-Low Range", "Alpha158高低价差"),
    "vwap_dev_20h": ("20h VWAP Deviation", "20小时VWAP偏离"),
    "wvma_20h": ("20h Volume-Weighted Vol", "20小时量加权波动"),
    "vol_ret_corr_20h": ("20h Vol-Return Correlation", "20小时量价相关"),
    "intraday_ret": ("Intraday Return", "日内收益"),
    "klow_close": ("Lower Wick / Close", "下影线/收盘价"),
    "ksft_5h": ("5h Return Skewness", "5小时收益偏度"),
    "tech_macd": ("MACD Histogram", "MACD柱状图"),
    "tech_atr": ("14h ATR", "14小时ATR"),
    "range_1h": ("1h Range", "1小时区间"),
    "range_4h": ("4h Range", "4小时区间"),
    "range_24h": ("24h Range", "24小时区间"),
    "price_pos_24h": ("24h Price Position", "24小时价格位置"),
    "price_pos_72h": ("72h Price Position", "72小时价格位置"),
    "price_pos_120h": ("120h Price Position", "120小时价格位置"),
    "vol_zscore_20h": ("20h Volume Z-Score", "20小时成交量Z分数"),
    "vol_zscore_48h": ("48h Volume Z-Score", "48小时成交量Z分数"),
    "qvol_zscore_20h": ("20h Quote Vol Z-Score", "20小时成交额Z分数"),
    "qvol_zscore_48h": ("48h Quote Vol Z-Score", "48小时成交额Z分数"),
    "qvol_ma_ratio_5_20": ("Quote Vol MA Ratio 5/20", "成交额均线比 5/20"),
    "qvol_ma_ratio_20_80": ("Quote Vol MA Ratio 20/80", "成交额均线比 20/80"),
    "ma_gap_5_20": ("MA Gap 5/20", "均线差 5/20"),
    "ma_gap_10_40": ("MA Gap 10/40", "均线差 10/40"),
    "ma_gap_20_80": ("MA Gap 20/80", "均线差 20/80"),
    "breakout_dist_20h": ("20h Breakout Distance", "20小时突破距离"),
    "breakout_dist_48h": ("48h Breakout Distance", "48小时突破距离"),
    "candle_body": ("Candle Body Ratio", "K线实体比率"),
    "candle_wick_upper": ("Upper Wick Ratio", "上影线比率"),
    "candle_wick_lower": ("Lower Wick Ratio", "下影线比率"),
    "xs_rank_ret_1h": ("1h Cross-Sectional Return Rank", "1小时截面收益排名"),
    "xs_rank_vol": ("20h Cross-Sectional Volume Rank", "20小时截面成交量排名"),
    "ema_12_26_gap": ("EMA 12/26 Gap", "EMA 12/26差"),
    "williams_r_14h": ("14h Williams %R", "14小时威廉%R"),
    "downside_vol_20h": ("20h Downside Volatility", "20小时下行波动率"),
    "vol_of_vol_20h": ("20h Volatility of Volatility", "20小时波动率的波动率"),
    "taker_buy_ratio_20h": ("20h Taker Buy Ratio", "20小时主动买入比率"),
    "taker_buy_zscore_20h": ("20h Taker Buy Z-Score", "20小时主动买入Z分数"),
    "taker_buy_delta_5h": ("5h Taker Buy Delta", "5小时主动买入变化"),
    "funding_rate_level_20h": ("20h Funding Rate Level", "20小时资金费率水平"),
    "funding_rate_zscore_80h": ("80h Funding Rate Z-Score", "80小时资金费率Z分数"),
    "funding_rate_change_24h": ("24h Funding Rate Change", "24小时资金费率变化"),
    "realized_skew_20h": ("20h Realized Skewness", "20小时已实现偏度"),
    "realized_kurt_20h": ("20h Realized Kurtosis", "20小时已实现峰度"),
    "amihud_illiquidity_20h": ("20h Amihud Illiquidity", "20小时Amihud非流动性"),
    "price_volume_corr_20h": ("20h Price-Volume Correlation", "20小时量价相关性"),
    "trend_efficiency_24h": ("24h Trend Efficiency", "24小时趋势效率"),
    "q158_open_close_2h": ("Alpha158 OPEN2 / Close", "Alpha158 前2期开盘价/当前收盘价"),
    "q158_high_close_2h": ("Alpha158 HIGH2 / Close", "Alpha158 前2期最高价/当前收盘价"),
    "q158_low_close_2h": ("Alpha158 LOW2 / Close", "Alpha158 前2期最低价/当前收盘价"),
    "q158_open_close_3h": ("Alpha158 OPEN3 / Close", "Alpha158 前3期开盘价/当前收盘价"),
    "q158_high_close_3h": ("Alpha158 HIGH3 / Close", "Alpha158 前3期最高价/当前收盘价"),
    "q158_low_close_3h": ("Alpha158 LOW3 / Close", "Alpha158 前3期最低价/当前收盘价"),
    "q158_open_close_4h": ("Alpha158 OPEN4 / Close", "Alpha158 前4期开盘价/当前收盘价"),
    "q158_high_close_4h": ("Alpha158 HIGH4 / Close", "Alpha158 前4期最高价/当前收盘价"),
    "q158_low_close_4h": ("Alpha158 LOW4 / Close", "Alpha158 前4期最低价/当前收盘价"),
    "q158_close_close_4h": ("Alpha158 CLOSE4 / Close", "Alpha158 前4期收盘价/当前收盘价"),
    "q158_volume_ratio_1h": ("Alpha158 VOLUME1 Ratio", "Alpha158 前1期成交量/当前成交量"),
    "q158_volume_ratio_2h": ("Alpha158 VOLUME2 Ratio", "Alpha158 前2期成交量/当前成交量"),
    "q158_volume_ratio_3h": ("Alpha158 VOLUME3 Ratio", "Alpha158 前3期成交量/当前成交量"),
    "q158_volume_ratio_4h": ("Alpha158 VOLUME4 Ratio", "Alpha158 前4期成交量/当前成交量"),
    "q158_ma_5h": ("Alpha158 MA5 / Close", "Alpha158 5期均价/当前收盘价"),
    "q158_std_5h": ("Alpha158 STD5 / Close", "Alpha158 5期价格标准差/当前收盘价"),
    "q158_max_5h": ("Alpha158 MAX5 / Close", "Alpha158 5期最高价/当前收盘价"),
    "q158_min_5h": ("Alpha158 MIN5 / Close", "Alpha158 5期最低价/当前收盘价"),
    "q158_ma_10h": ("Alpha158 MA10 / Close", "Alpha158 10期均价/当前收盘价"),
    "q158_std_10h": ("Alpha158 STD10 / Close", "Alpha158 10期价格标准差/当前收盘价"),
    "q158_max_10h": ("Alpha158 MAX10 / Close", "Alpha158 10期最高价/当前收盘价"),
    "q158_min_10h": ("Alpha158 MIN10 / Close", "Alpha158 10期最低价/当前收盘价"),
    "q158_ma_30h": ("Alpha158 MA30 / Close", "Alpha158 30期均价/当前收盘价"),
    "q158_std_30h": ("Alpha158 STD30 / Close", "Alpha158 30期价格标准差/当前收盘价"),
    "q158_max_30h": ("Alpha158 MAX30 / Close", "Alpha158 30期最高价/当前收盘价"),
    "q158_min_30h": ("Alpha158 MIN30 / Close", "Alpha158 30期最低价/当前收盘价"),
    "q158_ma_60h": ("Alpha158 MA60 / Close", "Alpha158 60期均价/当前收盘价"),
    "q158_std_60h": ("Alpha158 STD60 / Close", "Alpha158 60期价格标准差/当前收盘价"),
    "q158_max_60h": ("Alpha158 MAX60 / Close", "Alpha158 60期最高价/当前收盘价"),
    "q158_min_60h": ("Alpha158 MIN60 / Close", "Alpha158 60期最低价/当前收盘价"),
    "q158_rsv_30h": ("Alpha158 RSV30 Price Position", "Alpha158 30期RSV价格位置"),
    "q158_qtlu_30h": ("Alpha158 QTLU30 / Close", "Alpha158 30期上分位价/当前收盘价"),
    "q158_qtld_30h": ("Alpha158 QTLD30 / Close", "Alpha158 30期下分位价/当前收盘价"),
    "q158_rank_close_30h": ("Alpha158 RANK30 Close", "Alpha158 30期收盘价时序排名"),
    "q158_beta_30h": ("Alpha158 BETA30 / Close", "Alpha158 30期趋势斜率/当前收盘价"),
    "q158_rsqr_30h": ("Alpha158 RSQR30", "Alpha158 30期趋势拟合度"),
    "q158_resi_30h": ("Alpha158 RESI30 / Close", "Alpha158 30期趋势残差/当前收盘价"),
    "q158_imax_30h": ("Alpha158 IMAX30 High Recency", "Alpha158 30期最高价新近度"),
    "q158_cntp_30h": ("Alpha158 CNTP30 Up-Bar Share", "Alpha158 30期上涨K线占比"),
    "q158_cntn_30h": ("Alpha158 CNTN30 Down-Bar Share", "Alpha158 30期下跌K线占比"),
    "q158_cntd_30h": ("Alpha158 CNTD30 Up-Down Balance", "Alpha158 30期涨跌K线差"),
    "q158_sumd_30h": ("Alpha158 SUMD30 Signed Move Dominance", "Alpha158 30期涨跌幅主导度"),
}

# Per-factor formula overrides
FACTOR_FORMULAS: dict[str, tuple[str, str]] = {
    "mom_20h": ("close / close_lag(20) - 1", "收盘价 / 20期前收盘价 - 1"),
    "mom_5h": ("close / close_lag(5) - 1", "收盘价 / 5期前收盘价 - 1"),
    "mom_10h": ("close / close_lag(10) - 1", "收盘价 / 10期前收盘价 - 1"),
    "mom_40h": ("close / close_lag(40) - 1", "收盘价 / 40期前收盘价 - 1"),
    "mom_72h": ("close / close_lag(72) - 1", "收盘价 / 72期前收盘价 - 1"),
    "mom_120h": ("close / close_lag(120) - 1", "收盘价 / 120期前收盘价 - 1"),
    "mom_accel_20h": ("mom_20h - mom_20h_lag(5)", "20小时动量 - 5期前20小时动量"),
    "reversal_5h": ("-(close / close_lag(5) - 1)", "-(收盘价 / 5期前收盘价 - 1)"),
    "rev_1h": ("-(close / close_lag(1) - 1)", "-(收盘价 / 1期前收盘价 - 1)"),
    "rev_3h": ("-(close / close_lag(3) - 1)", "-(收盘价 / 3期前收盘价 - 1)"),
    "rev_10h": ("-(close / close_lag(10) - 1)", "-(收盘价 / 10期前收盘价 - 1)"),
    "rev_24h": ("-(close / close_lag(24) - 1)", "-(收盘价 / 24期前收盘价 - 1)"),
    "rev_72h": ("-(close / close_lag(72) - 1)", "-(收盘价 / 72期前收盘价 - 1)"),
    "volatility_20h": ("std(ret_1h, 20)", "1小时收益的20期标准差"),
    "vol_5h": ("std(ret_1h, 5)", "1小时收益的5期标准差"),
    "vol_40h": ("std(ret_1h, 40)", "1小时收益的40期标准差"),
    "vol_ratio_5_20": ("std(ret,5) / std(ret,20)", "5期波动率 / 20期波动率"),
    "vol_ratio_20_80": ("std(ret,20) / std(ret,80)", "20期波动率 / 80期波动率"),
    "rsi_14h": ("Wilder RSI(14)", "怀尔德RSI(14)"),
    "rsi_7h": ("Wilder RSI(7)", "怀尔德RSI(7)"),
    "rsi_28h": ("Wilder RSI(28)", "怀尔德RSI(28)"),
    "bb_zscore_20h": ("(close - SMA20) / std20", "(收盘价 - 20期均线) / 20期标准差"),
    "wq101_alpha101": ("(close - open) / (high - low + eps)", "(收盘 - 开盘) / (最高 - 最低 + eps)"),
    "wq101_alpha12": ("sign(delta(vol,1)) * (-delta(close,1))", "sign(成交量变化) * (-收盘价变化)"),
    "wq101_alpha53": ("-delta(intraday_position, 9)", "-delta(日内位置, 9)"),
    "wq101_alpha6": ("-correlation(open, volume, 10)", "-correlation(开盘价, 成交量, 10)"),
    "wq101_alpha9": ("conditional delta(close,1) using ts_min/ts_max over 5 bars", "基于5期价格变化最小/最大值的条件式delta(close,1)"),
    "wq101_alpha21": ("close mean/std state with volume / adv20 branch", "收盘价均值/标准差状态 + 成交量/adv20分支"),
    "wq101_alpha41": ("sqrt(high * low) - vwap", "sqrt(最高价 * 最低价) - VWAP"),
    "wq101_alpha54": ("(-1*((low-close)*open^5))/((low-high)*close^5)", "(-1*((最低-收盘)*开盘^5))/((最低-最高)*收盘^5)"),
    "wq101_alpha23": ("if mean(high,20) < high: -delta(high,2); else 0", "若20期最高价均值低于当前最高价：-delta(high,2)；否则 0"),
    "wq101_alpha24": ("mean(close,100) drift branch or -delta(close,3)", "100期均值漂移分支或 -delta(close,3)"),
    "wq101_alpha46": ("close 20/10-bar slope state with -delta(close,1) fallback", "收盘价20/10期斜率状态，带 -delta(close,1) 分支"),
    "wq101_alpha49": ("close 20/10-bar slope state or -delta(close,1)", "收盘价20/10期斜率状态或 -delta(close,1)"),
    "wq101_alpha51": ("close 20/10-bar slope state or -delta(close,1), threshold -0.05", "收盘价20/10期斜率状态或 -delta(close,1)，阈值 -0.05"),
    "wq101_alpha32": ("scale(mean(close,7)-close) + 20*scale(corr(vwap,delay(close,5),230))", "scale(7期均价-收盘价) + 20*scale(VWAP与5期前收盘价230期相关)"),
    "wq101_alpha33": ("rank(-1*(1-open/close))", "rank(-1*(1-开盘价/收盘价))"),
    "wq101_alpha37": ("rank(corr(delay(open-close,1), close, 200)) + rank(open-close)", "rank(1期前开收差与收盘价200期相关) + rank(开盘价-收盘价)"),
    "wq101_alpha38": ("-rank(ts_rank(close,10)) * rank(close/open)", "-rank(收盘价10期时序排名) * rank(收盘价/开盘价)"),
    "wq101_alpha44": ("-corr(high, rank(volume), 5)", "-corr(最高价, 成交量截面排名, 5)"),
    "wq101_alpha45": ("-rank(mean(delay(close,5),20))*corr(close,volume,2)*rank(corr(sum(close,5),sum(close,20),2))", "-rank(5期滞后收盘价20期均值)*corr(收盘价,成交量,2)*rank(corr(5期收盘和,20期收盘和,2))"),
    "wq101_alpha34": ("rank((1-rank(std(ret,2)/std(ret,5))) + (1-rank(delta(close,1))))", "rank((1-rank(2期收益波动/5期收益波动)) + (1-rank(收盘价1期变化)))"),
    "wq101_alpha40": ("-rank(std(high,10)) * corr(high, volume, 10)", "-rank(最高价10期标准差) * corr(最高价,成交量,10)"),
    "wq101_alpha42": ("rank(vwap-close) / rank(vwap+close)", "rank(VWAP-收盘价) / rank(VWAP+收盘价)"),
    "wq101_alpha50": ("-ts_max(rank(corr(rank(volume),rank(vwap),5)),5)", "-5期最大值(rank(corr(rank(成交量),rank(VWAP),5)))"),
    "wq101_alpha55": ("-corr(rank((close-ts_min(low,12))/(ts_max(high,12)-ts_min(low,12))), rank(volume), 6)", "-corr(rank(12期区间内收盘位置), rank(成交量), 6)"),
    "wq101_alpha60": ("-((2*scale(rank(close-location*volume))) - scale(rank(ts_argmax(close,10))))", "-((2*scale(rank(收盘位置*成交量))) - scale(rank(收盘价10期最高位置)))"),
    "q158_high_low_range": ("(high - low) / close", "(最高 - 最低) / 收盘价"),
    "vwap_dev_20h": ("(close - VWAP20) / VWAP20", "(收盘价 - 20期VWAP) / 20期VWAP"),
    "wvma_20h": ("std(ret*vol,20) / mean(vol,20)", "收益*成交量的20期标准差 / 成交量20期均值"),
    "vol_ret_corr_20h": ("corr(ret, delta(vol,1), 20)", "收益与成交量变化的20期相关系数"),
    "intraday_ret": ("(close - open) / open", "(收盘 - 开盘) / 开盘"),
    "klow_close": ("(min(open,close) - low) / close", "(min(开盘,收盘) - 最低) / 收盘"),
    "ksft_5h": ("skewness(ret, 5)", "5期收益偏度"),
    "tech_macd": ("MACD histogram (EMA12 - EMA26 signal)", "MACD柱状图 (EMA12 - EMA26信号)"),
    "tech_atr": ("ATR(14)", "ATR(14)"),
    "range_1h": ("(high - low) / close", "(最高 - 最低) / 收盘价"),
    "range_4h": ("(HH4 - LL4) / close", "(4期最高 - 4期最低) / 收盘价"),
    "range_24h": ("(HH24 - LL24) / close", "(24期最高 - 24期最低) / 收盘价"),
    "price_pos_24h": ("(close - LL24) / (HH24 - LL24)", "(收盘 - 24期最低) / (24期最高 - 24期最低)"),
    "price_pos_72h": ("(close - LL72) / (HH72 - LL72)", "(收盘 - 72期最低) / (72期最高 - 72期最低)"),
    "price_pos_120h": ("(close - LL120) / (HH120 - LL120)", "(收盘 - 120期最低) / (120期最高 - 120期最低)"),
    "vol_zscore_20h": ("(volume - SMA20) / std20", "(成交量 - 20期均线) / 20期标准差"),
    "vol_zscore_48h": ("(volume - SMA48) / std48", "(成交量 - 48期均线) / 48期标准差"),
    "qvol_zscore_20h": ("(quote_volume - SMA20) / std20", "(成交额 - 20期均线) / 20期标准差"),
    "qvol_zscore_48h": ("(quote_volume - SMA48) / std48", "(成交额 - 48期均线) / 48期标准差"),
    "qvol_ma_ratio_5_20": ("SMA(qvol,5) / SMA(qvol,20) - 1", "成交额5期均线 / 20期均线 - 1"),
    "qvol_ma_ratio_20_80": ("SMA(qvol,20) / SMA(qvol,80) - 1", "成交额20期均线 / 80期均线 - 1"),
    "ma_gap_5_20": ("(SMA5 - SMA20) / SMA20", "(5期均线 - 20期均线) / 20期均线"),
    "ma_gap_10_40": ("(SMA10 - SMA40) / SMA40", "(10期均线 - 40期均线) / 40期均线"),
    "ma_gap_20_80": ("(SMA20 - SMA80) / SMA80", "(20期均线 - 80期均线) / 80期均线"),
    "breakout_dist_20h": ("(close - HH20) / (HH20 - LL20)", "(收盘 - 20期最高) / (20期最高 - 20期最低)"),
    "breakout_dist_48h": ("(close - HH48) / (HH48 - LL48)", "(收盘 - 48期最高) / (48期最高 - 48期最低)"),
    "candle_body": ("(close - open) / (high - low)", "(收盘 - 开盘) / (最高 - 最低)"),
    "candle_wick_upper": ("(high - max(open,close)) / (high - low)", "(最高 - max(开盘,收盘)) / (最高 - 最低)"),
    "candle_wick_lower": ("(min(open,close) - low) / (high - low)", "(min(开盘,收盘) - 最低) / (最高 - 最低)"),
    "xs_rank_ret_1h": ("cross_sectional_rank(ret_1h)", "1小时收益的截面排名"),
    "xs_rank_vol": ("cross_sectional_rank(mean(vol,20))", "20期均量的截面排名"),
    "ema_12_26_gap": ("(EMA12 - EMA26) / EMA26", "(EMA12 - EMA26) / EMA26"),
    "williams_r_14h": ("(HH14 - close) / (HH14 - LL14)", "(14期最高 - 收盘) / (14期最高 - 14期最低)"),
    "downside_vol_20h": ("std(min(ret,0), 20)", "负收益的20期标准差"),
    "vol_of_vol_20h": ("std(std(ret,5), 20)", "5期波动率的20期标准差"),
    "taker_buy_ratio_20h": ("mean(taker_buy_qvol / qvol, 20)", "20期主动买入成交额/总成交额均值"),
    "taker_buy_zscore_20h": ("zscore(taker_buy_qvol / qvol, 20)", "主动买入比率的20期Z分数"),
    "taker_buy_delta_5h": ("ratio - ratio_lag(5)", "主动买入比率 - 5期前主动买入比率"),
    "funding_rate_level_20h": ("mean(funding_rate, 20)", "20期资金费率均值"),
    "funding_rate_zscore_80h": ("zscore(funding_rate, 80)", "资金费率的80期Z分数"),
    "funding_rate_change_24h": ("funding_rate - funding_rate_lag(24)", "资金费率 - 24期前资金费率"),
    "realized_skew_20h": ("skewness(ret_1h, 20)", "1小时收益的20期偏度"),
    "realized_kurt_20h": ("kurtosis(ret_1h, 20)", "1小时收益的20期峰度"),
    "amihud_illiquidity_20h": ("mean(|ret| / qvol, 20)", "20期|收益|/成交额均值"),
    "price_volume_corr_20h": ("corr(ret, pctchg(qvol), 20)", "收益与成交额变化的20期相关系数"),
    "trend_efficiency_24h": ("|ret_24h| / sum(|ret_1h|, 24)", "24小时收益绝对值 / 24期小时收益绝对值之和"),
    "q158_open_close_2h": ("Ref(open, 2) / close", "前2期开盘价 / 当前收盘价"),
    "q158_high_close_2h": ("Ref(high, 2) / close", "前2期最高价 / 当前收盘价"),
    "q158_low_close_2h": ("Ref(low, 2) / close", "前2期最低价 / 当前收盘价"),
    "q158_open_close_3h": ("Ref(open, 3) / close", "前3期开盘价 / 当前收盘价"),
    "q158_high_close_3h": ("Ref(high, 3) / close", "前3期最高价 / 当前收盘价"),
    "q158_low_close_3h": ("Ref(low, 3) / close", "前3期最低价 / 当前收盘价"),
    "q158_open_close_4h": ("Ref(open, 4) / close", "前4期开盘价 / 当前收盘价"),
    "q158_high_close_4h": ("Ref(high, 4) / close", "前4期最高价 / 当前收盘价"),
    "q158_low_close_4h": ("Ref(low, 4) / close", "前4期最低价 / 当前收盘价"),
    "q158_close_close_4h": ("Ref(close, 4) / close", "前4期收盘价 / 当前收盘价"),
    "q158_volume_ratio_1h": ("Ref(volume, 1) / (volume + 1e-12)", "前1期成交量 / (当前成交量 + 1e-12)"),
    "q158_volume_ratio_2h": ("Ref(volume, 2) / (volume + 1e-12)", "前2期成交量 / (当前成交量 + 1e-12)"),
    "q158_volume_ratio_3h": ("Ref(volume, 3) / (volume + 1e-12)", "前3期成交量 / (当前成交量 + 1e-12)"),
    "q158_volume_ratio_4h": ("Ref(volume, 4) / (volume + 1e-12)", "前4期成交量 / (当前成交量 + 1e-12)"),
    "q158_ma_5h": ("Mean(close, 5) / close", "5期收盘均价 / 当前收盘价"),
    "q158_std_5h": ("Std(close, 5) / close", "5期收盘价标准差 / 当前收盘价"),
    "q158_max_5h": ("Max(high, 5) / close", "5期最高价 / 当前收盘价"),
    "q158_min_5h": ("Min(low, 5) / close", "5期最低价 / 当前收盘价"),
    "q158_ma_10h": ("Mean(close, 10) / close", "10期收盘均价 / 当前收盘价"),
    "q158_std_10h": ("Std(close, 10) / close", "10期收盘价标准差 / 当前收盘价"),
    "q158_max_10h": ("Max(high, 10) / close", "10期最高价 / 当前收盘价"),
    "q158_min_10h": ("Min(low, 10) / close", "10期最低价 / 当前收盘价"),
    "q158_ma_30h": ("Mean(close, 30) / close", "30期收盘均价 / 当前收盘价"),
    "q158_std_30h": ("Std(close, 30) / close", "30期收盘价标准差 / 当前收盘价"),
    "q158_max_30h": ("Max(high, 30) / close", "30期最高价 / 当前收盘价"),
    "q158_min_30h": ("Min(low, 30) / close", "30期最低价 / 当前收盘价"),
    "q158_ma_60h": ("Mean(close, 60) / close", "60期收盘均价 / 当前收盘价"),
    "q158_std_60h": ("Std(close, 60) / close", "60期收盘价标准差 / 当前收盘价"),
    "q158_max_60h": ("Max(high, 60) / close", "60期最高价 / 当前收盘价"),
    "q158_min_60h": ("Min(low, 60) / close", "60期最低价 / 当前收盘价"),
    "q158_rsv_30h": ("(close - Min(low, 30)) / (Max(high, 30) - Min(low, 30) + eps)", "(收盘价 - 30期最低价) / (30期最高价 - 30期最低价 + eps)"),
    "q158_qtlu_30h": ("Quantile(close, 30, 0.8) / close", "30期收盘价80%分位数 / 当前收盘价"),
    "q158_qtld_30h": ("Quantile(close, 30, 0.2) / close", "30期收盘价20%分位数 / 当前收盘价"),
    "q158_rank_close_30h": ("Rank(close, 30)", "当前收盘价在30期窗口内的百分位排名"),
    "q158_beta_30h": ("Slope(close, 30) / close", "30期收盘价线性斜率 / 当前收盘价"),
    "q158_rsqr_30h": ("Rsquare(close, 30)", "30期收盘价线性趋势R平方"),
    "q158_resi_30h": ("Resi(close, 30) / close", "30期线性趋势最新残差 / 当前收盘价"),
    "q158_imax_30h": ("IdxMax(high, 30) / 30", "30期最高价距当前的条数 / 30"),
    "q158_cntp_30h": ("Mean(close > Ref(close, 1), 30)", "30期内收盘价上涨K线占比"),
    "q158_cntn_30h": ("Mean(close < Ref(close, 1), 30)", "30期内收盘价下跌K线占比"),
    "q158_cntd_30h": ("Mean(close > Ref(close, 1), 30) - Mean(close < Ref(close, 1), 30)", "30期上涨K线占比 - 30期下跌K线占比"),
    "q158_sumd_30h": ("(Sum(up moves, 30) - Sum(down moves, 30)) / Sum(abs moves, 30)", "(30期上涨幅度和 - 30期下跌幅度和) / 30期绝对变动和"),
}

# Per-factor known limitations
FACTOR_LIMITATIONS: dict[str, tuple[str, str]] = {
    "wq101_alpha101": ("Requires intrabar OHLC; single-bar component, noisy in low-liquidity symbols.", "需要K线内OHLC；单根K线分量，低流动性标的噪音大。"),
    "wq101_alpha12": ("Sign-dependent on volume change direction; may flip in choppy markets.", "符号取决于成交量变化方向；震荡市可能翻转。"),
    "wq101_alpha53": ("Intraday position metric sensitive to exchange-specific bar boundaries.", "日内位置指标对交易所特定K线边界敏感。"),
    "wq101_alpha6": ("Open-volume correlation is scale-sensitive and may mostly capture liquidity regimes, not a standalone signal.", "开盘价与成交量相关性对尺度敏感，可能主要捕捉流动性状态，并非独立信号。"),
    "wq101_alpha9": ("Conditional delta rule is short-horizon and direction-ambiguous; choppy bars can flip interpretation.", "条件式价格变化规则偏短周期且方向不明确；震荡K线可能导致解释翻转。"),
    "wq101_alpha21": ("Piecewise state factor uses hard thresholds and adv20; sparse newer symbols have warmup and liquidity sensitivity.", "分段状态因子使用硬阈值和adv20；新标的存在启动期和流动性敏感性。"),
    "wq101_alpha41": ("VWAP is derived from quote_volume/volume; zero or tiny volume bars can make the gap noisy.", "VWAP由成交额/成交量推导；零成交或微小成交量K线会使差值噪音变大。"),
    "wq101_alpha54": ("Power terms can amplify small OHLC differences and should be treated as a diagnostic formula transfer.", "幂项会放大微小OHLC差异，应作为公式迁移诊断看待。"),
    "wq101_alpha23": ("High breakout branch can be sparse in flat markets and is sensitive to wick noise.", "高价突破分支在横盘市场可能很稀疏，且对影线噪音敏感。"),
    "wq101_alpha24": ("Uses a 200-bar effective warmup and hard drift threshold; interpretation is horizon-dependent.", "有效启动期约200根K线且使用硬漂移阈值；解释依赖视野。"),
    "wq101_alpha46": ("Slope thresholds are transferred from daily equities to 1h crypto bars and may produce state-like constants.", "斜率阈值从日频股票迁移到1小时加密K线，可能产生状态型常数输出。"),
    "wq101_alpha49": ("Slope threshold is transferred from daily equities to 1h crypto bars without claiming signal validity.", "斜率阈值从日频股票迁移到1小时加密K线，不声称信号有效性。"),
    "wq101_alpha51": ("Close-slope threshold differs only slightly from Alpha49, so redundancy review is expected.", "收盘斜率阈值与Alpha49只略有差异，预期需要冗余复核。"),
    "wq101_alpha32": ("Uses a 235-bar effective warmup and cross-sectional scale; interpretation depends on universe composition.", "有效启动期约235根K线且使用截面scale；解释会受币种池组成影响。"),
    "wq101_alpha33": ("Pure cross-sectional intrabar rank; very sensitive to bar-level open/close microstructure.", "纯截面K线内排名；对开收盘微观结构非常敏感。"),
    "wq101_alpha37": ("Long 200-bar correlation plus cross-sectional rank; stale symbols and universe changes can affect ranks.", "包含200期长相关和截面排名；冷门标的和币种池变化会影响排名。"),
    "wq101_alpha38": ("Combines time-series rank with cross-sectional ranks; direction can flip between continuation and reversal regimes.", "结合时序排名和截面排名；方向可能在趋势延续和反转状态间切换。"),
    "wq101_alpha44": ("Short high-volume-rank correlation can be noisy around volume spikes and wick-heavy bars.", "短窗口最高价与成交量排名相关在放量和长影线K线附近可能噪音较大。"),
    "wq101_alpha45": ("Mixes very short correlations with cross-sectional ranks; expected to be fragile and redundancy-prone.", "混合极短相关和截面排名，预期较脆弱且可能高度冗余。"),
    "wq101_alpha34": ("Uses nested cross-sectional ranks on short-window volatility and close delta; highly universe-composition sensitive.", "对短窗口波动和收盘变化使用嵌套截面排名；对币种池组成高度敏感。"),
    "wq101_alpha40": ("High-price volatility rank multiplied by high-volume correlation can be dominated by wick noise.", "最高价波动排名乘以量价相关，可能被影线噪音主导。"),
    "wq101_alpha42": ("VWAP is derived from quote_volume/volume; tiny volume bars can distort rank ratios.", "VWAP由成交额/成交量推导；极小成交量K线可能扭曲排名比值。"),
    "wq101_alpha50": ("Nested rank-correlation and ts_max can be sticky and redundant with short volume/VWAP crowding factors.", "嵌套排名相关和ts_max可能较粘滞，并与短周期成交量/VWAP拥挤因子冗余。"),
    "wq101_alpha55": ("Range-position rank can be unstable when high-low range is tiny; volume rank adds universe dependence.", "高低价区间很小时区间位置排名不稳定；成交量排名增加币种池依赖。"),
    "wq101_alpha60": ("Uses close-location volume flow and ts_argmax rank; sensitive to wick-heavy bars and range compression.", "使用收盘位置成交量流和最高价位置排名；对长影线K线和区间压缩敏感。"),
    "taker_buy_ratio_20h": ("Requires taker-enriched data. Not available for all symbols historically.", "需要taker增强数据。并非所有标的都有历史数据。"),
    "taker_buy_zscore_20h": ("Requires taker-enriched data. Z-score assumes stationarity.", "需要taker增强数据。Z分数假设平稳性。"),
    "taker_buy_delta_5h": ("Requires taker-enriched data. Delta amplifies noise.", "需要taker增强数据。变化量放大噪音。"),
    "funding_rate_level_20h": ("Funding rate has structural low coverage for newer symbols.", "资金费率对新上市标的结构上覆盖率低。"),
    "funding_rate_zscore_80h": ("80h window means slow adaptation; Z-score may lag regime changes.", "80小时窗口意味着适应慢；Z分数可能滞后于状态变化。"),
    "funding_rate_change_24h": ("Short window amplifies noise in funding rate.", "短窗口放大资金费率噪音。"),
    "vol_of_vol_20h": ("Nested std computation requires 26 bars; sparse for new symbols.", "嵌套标准差计算需要26根K线；新标的数据稀疏。"),
    "ma_gap_20_80": ("80-bar lookback means slow startup; missing data for newer symbols.", "80根K线回溯意味着启动慢；新标的数据缺失。"),
    "price_pos_120h": ("120h lookback; may not have full history for all symbols.", "120小时回溯；部分标的历史可能不完整。"),
    "q158_open_close_2h": ("Raw lagged normalized price feature; high redundancy risk with reversal and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与反转和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_high_close_2h": ("Raw lagged normalized price feature; high redundancy risk with candle, range, and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与K线、区间和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_low_close_2h": ("Raw lagged normalized price feature; high redundancy risk with candle, range, and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与K线、区间和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_open_close_3h": ("Raw lagged normalized price feature; high redundancy risk with reversal and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与反转和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_high_close_3h": ("Raw lagged normalized price feature; high redundancy risk with candle, range, and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与K线、区间和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_low_close_3h": ("Raw lagged normalized price feature; high redundancy risk with candle, range, and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与K线、区间和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_open_close_4h": ("Raw lagged normalized price feature; high redundancy risk with reversal and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与反转和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_high_close_4h": ("Raw lagged normalized price feature; high redundancy risk with candle, range, and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与K线、区间和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_low_close_4h": ("Raw lagged normalized price feature; high redundancy risk with candle, range, and existing Alpha158 price-location factors.", "原始滞后标准化价格特征；与K线、区间和已有Alpha158价格位置因子存在高冗余风险。"),
    "q158_close_close_4h": ("Raw lagged normalized close ratio; overlaps strongly with short-horizon momentum/reversal diagnostics.", "原始滞后收盘价比率；与短周期动量/反转诊断高度重叠。"),
    "q158_volume_ratio_1h": ("Raw lagged volume ratio; can be unstable when current volume is tiny and may overlap with volume z-score/liquidity diagnostics.", "原始滞后成交量比率；当前成交量很小时可能不稳定，并可能与成交量Z分数/流动性诊断重叠。"),
    "q158_volume_ratio_2h": ("Raw lagged volume ratio; can be unstable when current volume is tiny and may overlap with volume z-score/liquidity diagnostics.", "原始滞后成交量比率；当前成交量很小时可能不稳定，并可能与成交量Z分数/流动性诊断重叠。"),
    "q158_volume_ratio_3h": ("Raw lagged volume ratio; can be unstable when current volume is tiny and may overlap with volume z-score/liquidity diagnostics.", "原始滞后成交量比率；当前成交量很小时可能不稳定，并可能与成交量Z分数/流动性诊断重叠。"),
    "q158_volume_ratio_4h": ("Raw lagged volume ratio; can be unstable when current volume is tiny and may overlap with volume z-score/liquidity diagnostics.", "原始滞后成交量比率；当前成交量很小时可能不稳定，并可能与成交量Z分数/流动性诊断重叠。"),
    "q158_ma_5h": ("Short rolling price average normalized by current close; high redundancy risk with short-horizon momentum and price-location factors.", "短周期滚动均价相对当前收盘价；与短周期动量和价格位置因子存在高冗余风险。"),
    "q158_std_5h": ("Short rolling price dispersion; sensitive to intraday volatility spikes and low-liquidity bars.", "短周期价格离散度；对日内波动尖峰和低流动性K线敏感。"),
    "q158_max_5h": ("Short rolling high normalized by current close; can overlap with breakout/range-position diagnostics.", "短周期最高价相对当前收盘价；可能与突破/区间位置诊断重叠。"),
    "q158_min_5h": ("Short rolling low normalized by current close; can overlap with reversal/range-position diagnostics.", "短周期最低价相对当前收盘价；可能与反转/区间位置诊断重叠。"),
    "q158_ma_10h": ("Medium-short rolling price average normalized by current close; high redundancy risk with momentum and moving-average gap factors.", "中短周期滚动均价相对当前收盘价；与动量和均线差因子存在高冗余风险。"),
    "q158_std_10h": ("Medium-short rolling price dispersion; sensitive to volatility clustering and low-liquidity bars.", "中短周期价格离散度；对波动聚集和低流动性K线敏感。"),
    "q158_max_10h": ("Medium-short rolling high normalized by current close; can overlap with breakout/range-position diagnostics.", "中短周期最高价相对当前收盘价；可能与突破/区间位置诊断重叠。"),
    "q158_min_10h": ("Medium-short rolling low normalized by current close; can overlap with reversal/range-position diagnostics.", "中短周期最低价相对当前收盘价；可能与反转/区间位置诊断重叠。"),
    "q158_ma_30h": ("Medium rolling price average normalized by current close; high redundancy risk with trend and moving-average gap factors.", "中周期滚动均价相对当前收盘价；与趋势和均线差因子存在高冗余风险。"),
    "q158_std_30h": ("Medium rolling price dispersion; sensitive to volatility regime shifts and low-liquidity bars.", "中周期价格离散度；对波动状态切换和低流动性K线敏感。"),
    "q158_max_30h": ("Medium rolling high normalized by current close; can overlap with breakout/range-position diagnostics.", "中周期最高价相对当前收盘价；可能与突破/区间位置诊断重叠。"),
    "q158_min_30h": ("Medium rolling low normalized by current close; can overlap with reversal/range-position diagnostics.", "中周期最低价相对当前收盘价；可能与反转/区间位置诊断重叠。"),
    "q158_ma_60h": ("Medium-long rolling price average normalized by current close; high redundancy risk with trend and moving-average gap factors.", "中长周期滚动均价相对当前收盘价；与趋势和均线差因子存在高冗余风险。"),
    "q158_std_60h": ("Medium-long rolling price dispersion; sensitive to regime shifts and long volatility clustering.", "中长周期价格离散度；对状态切换和长周期波动聚集敏感。"),
    "q158_max_60h": ("Medium-long rolling high normalized by current close; can overlap with breakout/range-position diagnostics.", "中长周期最高价相对当前收盘价；可能与突破/区间位置诊断重叠。"),
    "q158_min_60h": ("Medium-long rolling low normalized by current close; can overlap with reversal/range-position diagnostics.", "中长周期最低价相对当前收盘价；可能与反转/区间位置诊断重叠。"),
    "q158_rsv_30h": ("Medium-window range position; can flip interpretation between breakout continuation and overbought reversal.", "中周期区间位置；在突破延续和超买反转之间可能出现方向解释切换。"),
    "q158_qtlu_30h": ("Medium-window upper quantile normalized by current close; overlaps with rolling high and trend diagnostics.", "中周期上分位价相对当前收盘价；与滚动高点和趋势诊断可能重叠。"),
    "q158_qtld_30h": ("Medium-window lower quantile normalized by current close; overlaps with rolling low and reversal diagnostics.", "中周期下分位价相对当前收盘价；与滚动低点和反转诊断可能重叠。"),
    "q158_rank_close_30h": ("Medium-window time-series rank; direction depends on continuation versus mean-reversion regime.", "中周期时序排名；方向取决于延续或均值回归状态。"),
    "q158_beta_30h": ("Medium-window rolling trend slope; direction depends on continuation versus exhaustion.", "中周期滚动趋势斜率；方向取决于趋势延续或衰竭状态。"),
    "q158_rsqr_30h": ("Measures trend fit quality rather than direction; high values can occur in both uptrends and downtrends.", "衡量趋势拟合质量而非方向；高值可能同时出现在上涨和下跌趋势中。"),
    "q158_resi_30h": ("Latest residual from a rolling trend line; sensitive to local deviations and trend-window choice.", "滚动趋势线最新残差；对局部偏离和趋势窗口选择敏感。"),
    "q158_imax_30h": ("Recency of the rolling high; can overlap with breakout and range-position diagnostics.", "滚动最高价的新近度；可能与突破和区间位置诊断重叠。"),
    "q158_cntp_30h": ("Medium-window up-bar share; can overlap with momentum and persistence diagnostics.", "中周期上涨K线占比；可能与动量和延续性诊断重叠。"),
    "q158_cntn_30h": ("Medium-window down-bar share; negative direction can overlap with reversal and downside persistence diagnostics.", "中周期下跌K线占比；负向方向可能与反转和下行延续诊断重叠。"),
    "q158_cntd_30h": ("Medium-window signed up/down bar balance; direction depends on trend persistence versus exhaustion.", "中周期涨跌K线差；方向取决于趋势延续或衰竭状态。"),
    "q158_sumd_30h": ("Medium-window signed move dominance; can be redundant with momentum and bar-count direction factors.", "中周期涨跌幅主导度；可能与动量和涨跌K线计数方向因子冗余。"),
}


def _get_source_fields(spec: FactorSpec) -> str:
    """Determine source fields from required columns."""
    cols = set(spec.required_columns)
    if cols & {"taker_buy_quote_volume"}:
        return "taker_enriched"
    if "funding_rate" in cols:
        return "funding_rate_aligned"
    return "canonical_bars"


def _get_metadata_quality(spec: FactorSpec) -> str:
    """Determine metadata quality flag."""
    if spec.factor_id.startswith("q158_"):
        return "SOURCE_MAPPED_REVIEW_REQUIRED"
    if spec.status == "DIAGNOSTIC_PROBE":
        return "AUTO_GENERATED_REVIEW_REQUIRED"
    if spec.expected_direction == "conditional":
        return "DIRECTION_AMBIGUOUS"
    return "COMPLETE"


def _get_review_flag(spec: FactorSpec, diagnostics: dict | None) -> str:
    """Determine if review is needed."""
    flags = []
    if spec.status == "DIAGNOSTIC_PROBE":
        flags.append("DIAGNOSTIC_PROBE status")
    if spec.expected_direction == "conditional":
        flags.append("conditional direction")
    if diagnostics and diagnostics.get("decision_bucket") == "REVIEW_REQUIRED":
        flags.append("diagnostics review required")
    return "; ".join(flags) if flags else ""


def build_card(spec: FactorSpec, diagnostics: dict | None) -> dict:
    """Build a single bilingual factor card."""
    meta = FAMILY_META.get(spec.family, FAMILY_META.get("momentum", {}))
    fid = spec.factor_id
    lb = spec.lookback_window
    dir_key = spec.expected_direction

    # Names
    name_en, name_zh = FACTOR_NAMES.get(fid, (fid.replace("_", " ").title(), fid))

    # Formula
    formula_en, formula_zh = FACTOR_FORMULAS.get(fid, (spec.notes or fid, spec.notes or fid))

    # Intuition
    tpl_en = meta.get("intuition_template_en", "Diagnostic factor over {lookback}h.")
    tpl_zh = meta.get("intuition_template_zh", "{lookback}小时诊断因子。")
    intuition_en = tpl_en.format(lookback=lb)
    intuition_zh = tpl_zh.format(lookback=lb)

    # Direction explanation
    dir_expl = meta.get("direction_explanation", {})
    dir_en, dir_zh = dir_expl.get(dir_key, (f"Direction: {dir_key}.", f"方向：{dir_key}。"))

    # Limitations
    lim_en, lim_zh = FACTOR_LIMITATIONS.get(
        fid,
        ("Standard limitations apply: survivorship bias, look-ahead in label computation, no transaction costs.",
         "标准限制适用：幸存者偏差、标签计算中的前视偏差、无交易成本。")
    )

    # Review flag
    review_flag = _get_review_flag(spec, diagnostics)

    return {
        "factor_id": fid,
        "family": spec.family,
        "lifecycle_status": spec.status,
        "name_en": name_en,
        "name_zh": name_zh,
        "family_en": meta.get("family_en", spec.family),
        "family_zh": meta.get("family_zh", spec.family),
        "formula_en": formula_en,
        "formula_zh": formula_zh,
        "intuition_en": intuition_en,
        "intuition_zh": intuition_zh,
        "required_columns": ",".join(sorted(spec.required_columns)),
        "expected_direction": dir_key,
        "expected_direction_explanation_en": dir_en,
        "expected_direction_explanation_zh": dir_zh,
        "known_limitations_en": lim_en,
        "known_limitations_zh": lim_zh,
        "data_source_type": meta.get("data_source_type", "OHLCV"),
        "horizon_notes_en": f"Lookback window: {lb} bars. Evaluation covers 1h/4h/24h/72h horizons.",
        "horizon_notes_zh": f"回溯窗口：{lb}根K线。评价覆盖1h/4h/24h/72h视野。",
        "status_explanation_en": f"Status: {spec.status}. " + ("Diagnostic probe — not yet promoted to active signal." if spec.status == "DIAGNOSTIC_PROBE" else "Registered in factor library."),
        "status_explanation_zh": f"状态：{spec.status}。" + ("诊断探针——尚未升级为活跃信号。" if spec.status == "DIAGNOSTIC_PROBE" else "已注册在因子库中。"),
        "review_required_flag": review_flag,
        "metadata_quality": _get_metadata_quality(spec),
        "source_fields": _get_source_fields(spec),
    }


def main():
    out_dir = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_metadata"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load diagnostics for review flags
    diag_path = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics" / "factor_diagnostics_summary.json"
    diagnostics_by_id: dict[str, dict] = {}
    if diag_path.exists():
        with open(diag_path) as f:
            diag_data = json.load(f)
            diag_list = diag_data.get("factors", diag_data) if isinstance(diag_data, dict) else diag_data
            if isinstance(diag_list, list):
                for d in diag_list:
                    if isinstance(d, dict):
                        diagnostics_by_id[d.get("factor_id", "")] = d

    # Load overrides
    overrides_path = out_dir / "factor_card_overrides.json"
    overrides: dict[str, dict] = {}
    if overrides_path.exists():
        with open(overrides_path) as f:
            overrides = json.load(f)
        print(f"  Loaded {len(overrides)} overrides from {overrides_path.name}")

    # Build cards
    cards = []
    changed_count = 0
    for spec in REGISTRY:
        diag = diagnostics_by_id.get(spec.factor_id)
        card = build_card(spec, diag)

        # Apply overrides
        ov = overrides.get(spec.factor_id)
        if ov:
            for key, val in ov.items():
                if key in card and val is not None:
                    if card[key] != val:
                        changed_count += 1
                    card[key] = val

        cards.append(card)

    # Write CSV
    import csv
    csv_path = out_dir / "factor_bilingual_cards.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cards[0].keys())
        writer.writeheader()
        writer.writerows(cards)
    print(f"  Wrote {csv_path} ({len(cards)} rows)")

    # Write JSON
    json_path = out_dir / "factor_bilingual_cards.json"
    with open(json_path, "w") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {json_path}")

    # QA Report
    qa_path = out_dir / "factor_card_qa_report.csv"
    qa_rows = []
    for c in cards:
        needs_human = c["metadata_quality"] in {"AUTO_GENERATED_REVIEW_REQUIRED", "NEEDS_REVIEW", "FORMULA_AMBIGUOUS", "DIRECTION_AMBIGUOUS"}
        qa_rows.append({
            "factor_id": c["factor_id"],
            "metadata_quality": c["metadata_quality"],
            "qa_notes_zh": c["intuition_zh"][:80],
            "qa_notes_en": c["intuition_en"][:80],
            "changed_in_pm14b": "yes" if c["factor_id"] in overrides else "no",
            "needs_human_review": "yes" if needs_human else "no",
            "reason": c.get("review_required_flag", ""),
        })
    with open(qa_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=qa_rows[0].keys())
        writer.writeheader()
        writer.writerows(qa_rows)
    print(f"  Wrote {qa_path} ({len(qa_rows)} rows)")

    # Manifest
    from collections import Counter
    mq_dist = dict(Counter(c["metadata_quality"] for c in cards))
    ds_dist = dict(Counter(c["data_source_type"] for c in cards))

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "factor_count": len(cards),
        "input_files": [
            "scripts/factor_formula_registry.py",
            "research/.../factor_diagnostics/factor_diagnostics_summary.json",
            "research/.../factor_metadata/factor_card_overrides.json",
        ],
        "output_files": [
            str(csv_path.relative_to(ROOT)),
            str(json_path.relative_to(ROOT)),
            str(qa_path.relative_to(ROOT)),
        ],
        "required_fields": [
            "factor_id", "family", "lifecycle_status",
            "name_en", "name_zh", "family_en", "family_zh",
            "formula_en", "formula_zh", "intuition_en", "intuition_zh",
            "required_columns", "expected_direction",
            "expected_direction_explanation_en", "expected_direction_explanation_zh",
            "known_limitations_en", "known_limitations_zh",
            "data_source_type", "horizon_notes_en", "horizon_notes_zh",
            "status_explanation_en", "status_explanation_zh",
            "review_required_flag", "metadata_quality", "source_fields",
        ],
        "metadata_quality_distribution": mq_dist,
        "data_source_type_distribution": ds_dist,
        "cards_changed_in_pm14b": sum(1 for c in cards if c["factor_id"] in overrides),
        "total_field_overrides_applied": changed_count,
        "validation_status": "PASS",
        "warnings": [],
        "non_change_statement": "No factor formulas, signal panel, or public pages modified.",
    }
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Wrote {manifest_path}")

    # Validation
    errors = []
    required_non_empty = [
        "factor_id", "name_en", "name_zh", "formula_en", "formula_zh",
        "intuition_en", "intuition_zh", "metadata_quality",
    ]
    allowed_mq = {
        "COMPLETE",
        "NEEDS_REVIEW",
        "FORMULA_AMBIGUOUS",
        "DIRECTION_AMBIGUOUS",
        "AUTO_GENERATED_REVIEW_REQUIRED",
        "SOURCE_MAPPED_REVIEW_REQUIRED",
    }

    if len(cards) != len(REGISTRY):
        errors.append(f"Expected {len(REGISTRY)} cards from registry, got {len(cards)}")

    ids = [c["factor_id"] for c in cards]
    if len(set(ids)) != len(ids):
        errors.append("Duplicate factor_ids found")

    for c in cards:
        for field in required_non_empty:
            if not c.get(field):
                errors.append(f"{c['factor_id']}: empty {field}")
        if c["metadata_quality"] not in allowed_mq:
            errors.append(f"{c['factor_id']}: invalid metadata_quality={c['metadata_quality']}")

    if errors:
        print(f"  VALIDATION ERRORS: {errors}")
        manifest["validation_status"] = "FAIL"
        manifest["warnings"] = errors
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
    else:
        print(f"  Validation: PASS ({len(cards)} cards, all fields populated)")

    # Print examples
    print("\n  Example cards:")
    for fid in ["mom_20h", "volatility_20h", "taker_buy_ratio_20h"]:
        c = next((x for x in cards if x["factor_id"] == fid), None)
        if c:
            print(f"    {c['factor_id']}: {c['name_en']} / {c['name_zh']} [{c['metadata_quality']}]")


if __name__ == "__main__":
    main()
