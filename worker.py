import time
from dataclasses import dataclass

import pyautogui
from PySide6.QtCore import QThread, Signal

from settings import AutomationSettings


@dataclass
class IterationResult:
    status: str  # "clicked" | "not_found" | "error"
    location: tuple[int, int] | None = None
    message: str = ""


class AutomationWorker(QThread):
    """自動操作ループを担うワーカースレッド。

    検出ロジックは iterate() に分離してあり、pyautogui をモックすれば
    Qt なしでユニットテストできる。
    """

    clicked = Signal(int, int)
    not_found = Signal()
    error = Signal(str)
    moved = Signal()

    def __init__(self, settings: AutomationSettings):
        super().__init__()
        self._settings = settings
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    def iterate(self) -> IterationResult:
        try:
            location = pyautogui.locateCenterOnScreen(
                self._settings.image_path,
                confidence=self._settings.confidence,
                grayscale=self._settings.grayscale,
            )
        except Exception as e:  # noqa: BLE001 - 検出失敗を握り潰さず通知する
            return IterationResult(status="error", message=str(e))

        if location is None:
            return IterationResult(status="not_found")

        point = (int(location[0]), int(location[1]))
        pyautogui.click(point)
        return IterationResult(status="clicked", location=point)

    def run(self) -> None:
        while not self._stop_requested:
            result = self.iterate()
            if result.status == "clicked" and result.location is not None:
                self.clicked.emit(result.location[0], result.location[1])
            elif result.status == "not_found":
                self.not_found.emit()
            elif result.status == "error":
                self.error.emit(result.message)

            if self._stop_requested:
                break
            time.sleep(self._settings.wait_seconds)
            if self._stop_requested:
                break

            # ホバー解除のためマウスを右下から100px内側へ移動（必須）
            try:
                width, height = pyautogui.size()
                pyautogui.moveTo(width - 100, height - 100, duration=0.5)
                self.moved.emit()
            except pyautogui.FailSafeException:
                self.error.emit("FailSafeException をキャッチしました")
                break
