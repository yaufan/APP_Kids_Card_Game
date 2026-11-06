# 小卡認天下

給 2 歲起小朋友的 APP：一張一張翻卡片，看、聽、找，認識身邊的東西和名字。每張卡片有真實版和卡通版，小朋友當下可以切換。

- 設計：[docs/design.md](docs/design.md)，草圖在 `docs/mockups/`。
- 和「[畫畫小鎮](https://github.com/yaufan/APP_Kids_Paint)」「[字母寵物](https://github.com/yaufan/APP_Kids_Paint_for_learning_writing)」「[動物小餐廳](https://github.com/yaufan/APP_Kids_Cook)」是兄弟 APP：同一個作者、同一套技術、不同畫風。
- 不連網、不定位、沒有廣告、沒有抽卡、沒有帳號；每次玩多久由家長設定。

## 目前進度
- 0.1 做好了，還沒發布：翻翻卡、找找看、真實版和卡通版切換、6 組 120 張卡片（240 張圖）、念名字和動物、車子的聲音、休息提醒、家長模式、APP 圖示。版本紀錄在 [CHANGELOG.md](CHANGELOG.md)。

## 程式和素材在哪裡
- `app/`：Flutter 程式。`lib/core/` 是卡片、存檔和規則、聲音、語音；`lib/features/` 是卡片盒、翻翻卡、找找看、休息、家長模式。
- `design/cards.json`：卡片名單（國語、英文、叫聲的字）。
- `design/art/`：用 Python 畫卡片（`deck_*.py`）和 APP 圖示（`icon.py`）。
- `design/sounds/make_sounds.py`：合成全部的音樂和聲音。
- 測試：在 `app/` 裡 `flutter test`；完整流程 `flutter test test/flow_test.dart`，截圖在 `app/build/screenshots/`。

## 授權
- 非商業使用授權：自己、家人使用，或學校、非營利團體的教學，都可以免費使用、修改、分享，要註明出處。
- 商業用途（販賣、收費、廣告、上架）要先取得作者書面同意。也不可以拿來訓練 AI。
- 細節見 [LICENSE](LICENSE)；別人做的部分（字型）見 [NOTICE.md](NOTICE.md)。
