from dataclasses import dataclass
from typing import ClassVar


@dataclass
class AutomationSettings:
    """自動操作の設定値を集約する単一モデル。

    GUI と worker はこのオブジェクトを介して設定をやり取りする。
    将来の永続化（保存/復元）はこの dataclass のシリアライズとして
    最小差分で追加できるようにしておく。
    """

    CONFIDENCE_MIN: ClassVar[float] = 0.1
    CONFIDENCE_MAX: ClassVar[float] = 1.0
    CONFIDENCE_DEFAULT: ClassVar[float] = 0.8

    image_path: str = ""
    confidence: float = 0.8
    wait_seconds: float = 4.0
    grayscale: bool = True
