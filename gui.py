from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from settings import AutomationSettings
from worker import AutomationWorker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyAutoGUI-Customed")
        self._worker: AutomationWorker | None = None

        # 対象画像
        self._path_edit = QLineEdit()
        self._path_edit.setReadOnly(True)
        self._path_edit.setPlaceholderText("対象画像を選択してください")
        browse_btn = QPushButton("参照")
        browse_btn.clicked.connect(self._on_browse)
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("対象画像:"))
        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(browse_btn)

        # CONFIDENCE スライダー（0.1〜1.0、内部は100倍の整数）
        self._conf_slider = QSlider(Qt.Orientation.Horizontal)
        self._conf_slider.setMinimum(int(AutomationSettings.CONFIDENCE_MIN * 100))
        self._conf_slider.setMaximum(int(AutomationSettings.CONFIDENCE_MAX * 100))
        self._conf_slider.setValue(int(AutomationSettings.CONFIDENCE_DEFAULT * 100))
        self._conf_label = QLabel()
        self._conf_slider.valueChanged.connect(self._update_conf_label)
        self._update_conf_label()
        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel("一致精度:"))
        conf_row.addWidget(self._conf_slider, 1)
        conf_row.addWidget(self._conf_label)

        # 待機時間
        self._wait_spin = QDoubleSpinBox()
        self._wait_spin.setRange(0.0, 60.0)
        self._wait_spin.setSingleStep(0.5)
        self._wait_spin.setValue(4.0)
        self._wait_spin.setSuffix(" 秒")
        wait_row = QHBoxLayout()
        wait_row.addWidget(QLabel("待機時間:"))
        wait_row.addWidget(self._wait_spin, 1)

        # グレースケール
        self._grayscale_check = QCheckBox("グレースケールで検出する")
        self._grayscale_check.setChecked(True)

        # 開始/停止
        self._start_btn = QPushButton("開始")
        self._stop_btn = QPushButton("停止")
        self._stop_btn.setEnabled(False)
        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self._on_stop)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)

        # ステータス
        self._status_label = QLabel("停止中")

        # ログ
        self._log = QTextEdit()
        self._log.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addLayout(path_row)
        layout.addLayout(conf_row)
        layout.addLayout(wait_row)
        layout.addWidget(self._grayscale_check)
        layout.addLayout(btn_row)
        layout.addWidget(self._status_label)
        layout.addWidget(QLabel("ログ:"))
        layout.addWidget(self._log, 1)

    def _update_conf_label(self) -> None:
        value = self._conf_slider.value() / 100
        self._conf_label.setText(f"{value:.2f}（推奨 0.80）")

    def collect_settings(self) -> AutomationSettings:
        return AutomationSettings(
            image_path=self._path_edit.text(),
            confidence=self._conf_slider.value() / 100,
            wait_seconds=self._wait_spin.value(),
            grayscale=self._grayscale_check.isChecked(),
        )

    def apply_settings(self, s: AutomationSettings) -> None:
        self._path_edit.setText(s.image_path)
        self._conf_slider.setValue(int(s.confidence * 100))
        self._wait_spin.setValue(s.wait_seconds)
        self._grayscale_check.setChecked(s.grayscale)

    def _append_log(self, text: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self._log.append(f"[{stamp}] {text}")

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "対象画像を選択", "", "画像 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self._path_edit.setText(path)

    def _on_start(self) -> None:
        settings = self.collect_settings()
        if not settings.image_path:
            self._append_log("対象画像が未選択です")
            return

        self._worker = AutomationWorker(settings)
        self._worker.clicked.connect(self._on_clicked)
        self._worker.not_found.connect(self._on_not_found)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText("実行中")
        self._append_log("開始しました")

    def _on_stop(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()
            self._append_log("停止要求を送信しました")

    def _on_clicked(self, x: int, y: int) -> None:
        self._status_label.setText(f"実行中（最後の検出: ({x}, {y}) をクリック）")
        self._append_log(f"検出してクリック: ({x}, {y})")

    def _on_not_found(self) -> None:
        self._status_label.setText("実行中（最後の検出: 見つかりず）")
        self._append_log("画像が見つかりませんでした")

    def _on_error(self, message: str) -> None:
        self._append_log(f"エラー: {message}")

    def _on_finished(self) -> None:
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("停止中")
        self._append_log("停止しました")
        self._worker = None
