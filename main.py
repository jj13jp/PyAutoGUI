import os
import sys

from PySide6.QtWidgets import QApplication

from gui import MainWindow


def main() -> None:
    # pyautogui/pyscreeze が import 時に SetProcessDPIAware()（システムDPI aware）を
    # 呼ぶため、Qt 既定の per-monitor aware v2 設定が後から失敗し警告が出る。
    # 座標の一貫性のため pyautogui 側の設定を活かし、Qt をシステム aware に合わせて競合を防ぐ。
    if sys.platform == "win32":
        os.environ.setdefault("QT_QPA_PLATFORM", "windows:dpiawareness=1")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
