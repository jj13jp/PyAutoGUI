import time
import pyautogui

while True:
    try:
        # 画面上から画像を探す
        location = pyautogui.locateCenterOnScreen("./assets/ss.jpg")
        if location:
            pyautogui.click(location)  # 見つかったらそこをクリック
        else:
            print("画像が見つかりませんでした")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    time.sleep(8)  # 8秒待つ

    try:
        pyautogui.moveTo(
            pyautogui.size()[0] - 100, pyautogui.size()[1] - 100, duration=0.5
        )
    except pyautogui.FailSafeException:
        print("FailSafeExceptionをキャッチしました")
