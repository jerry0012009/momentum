"""
Input schema for signal evaluation.

Minimal contract:
- signal_df: timestamp, symbol, signal_name, signal_value
- label_df (tidy): timestamp, symbol, horizon, forward_return
- label_df (wide): timestamp, symbol, fwd_ret_1h, fwd_ret_4h, fwd_ret_24h, fwd_ret_72h

Long-term recommendation: tidy format (horizon as a column).
"""

from dataclasses import dataclass


@dataclass
class SignalPanelSchema:
    """Expected columns for signal panel input."""
    timestamp: str = "timestamp"
    symbol: str = "symbol"
    signal_name: str = "signal_name"
    signal_value: str = "signal_value"

    def validate(self, df) -> bool:
        cols = set(df.columns)
        required = {self.timestamp, self.symbol, self.signal_name, self.signal_value}
        return required.issubset(cols)


@dataclass
class LabelPanelSchema:
    """Expected columns for label panel input (tidy format)."""
    timestamp: str = "timestamp"
    symbol: str = "symbol"
    horizon: str = "horizon"
    forward_return: str = "forward_return"


WIDE_LABEL_COLUMNS = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]

SIGNAL_EVALUATION_VERSION = "0.1.0"
