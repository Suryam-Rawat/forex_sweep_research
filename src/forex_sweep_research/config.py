from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyConfig:
    atr_window: int = 14
    swing_window: int = 10
    sr_lookback: int = 40
    zone_atr_mult: float = 0.3
    wick_atr_mult: float = 0.1
    volume_window: int = 20
    volume_z_threshold: float = 1.5
    reward_risk: float = 1.5
    outcome_horizon: int = 20
    transaction_cost_r: float = 0.0
    use_trend_filter: bool = False
    trend_ema_span: int = 100
    london_open: tuple[int, int] = (8, 10)
    new_york_open: tuple[int, int] = (13, 15)
