import time
import pyautogui

CONFIDENCE = 0.8  # 1.0=完全一致、下げるほど緩く検出（検出漏れ時は下げる）

while True:
    try:
        # 画面上から画像を探す
        location = pyautogui.locateCenterOnScreen(
            "./assets/target.jpg",
            confidence=CONFIDENCE,
            grayscale=True,
        )
        if location:
            pyautogui.click(location)  # 見つかったらそこをクリック
        else:
            print("画像が見つかりませんでした")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    time.sleep(4)  # 4秒待つ

    try:
        pyautogui.moveTo(
            pyautogui.size()[0] - 100, pyautogui.size()[1] - 100, duration=0.5
        )
    except pyautogui.FailSafeException:
        print("FailSafeExceptionをキャッチしました")
