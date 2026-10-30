# Misión CESFAM — 宣傳影片原始碼

這兩支影片全部由程式產生：每個畫面是一張 SVG，由瀏覽器（Playwright + Chromium）逐格截圖；配樂與音效用 Python（numpy）即時合成；最後用 ffmpeg 剪接與混音。沒有使用任何外部素材庫或音樂庫。

## 需要的工具
- Node.js 18+，並安裝 `playwright`（`npm i playwright`，再執行 `npx playwright install chromium`）
- Python 3 + `numpy`（需要驗證 QR 時再加 `Pillow`）
- ffmpeg / ffprobe
- Poppins 字型（Google Fonts，需安裝在系統中）
- （選用）zbar 函式庫：`verify_qr.py` 用它解碼、驗證 QR

## 檔案說明
| 檔案 | 用途 |
|---|---|
| `story4.html` | 所有場景（人物、手機、平板、時段標籤、轉場）。每一格都是時間 t 的純函式：`setScene(名稱)` → `render(t)` |
| `render4.js` | 輸出 16:9 場景：`node render4.js video intro sting …` → `st4_<場景>.mp4`；`node render4.js stills day1@2.5` → 單張預覽圖 |
| `render5.js` | 同上，但開啟直式模式（`window.VERT`），輸出 `st5_<場景>.mp4` 給 IG 版用 |
| `music17.py` | 合成主影片配樂與音效 → `music17.wav` |
| `build_main.py` | 剪接主影片、加上圓形轉場與封面格、混入音樂 → `mision-cesfam-v23.mp4` |
| `gen_ig.js` | 產生 IG 直式版的外框、標題與結尾卡圖片 → `ig/` |
| `build_ig.py` | 組合 IG 版 → `mision-cesfam-ig-reel.mp4` |
| `wipes/` | 綠／黃圓形轉場的 PNG 序列 |
| `shots/` | 遊戲畫面截圖（產品展示用） |
| `qr_clean.png` | 片尾 QR（連到 https://qrfy.io/d1jXpn1TmV） |
| `verify_qr.py` | 驗證畫面中的 QR：`python3 verify_qr.py 某一格.png` |

## 重新產生主影片（58 秒）
```bash
node render4.js video intro sting bridge day1 jorge cancel camila assigned climax teaserA teaserB core play outro
node render4.js stills sting@3.4 && cp s3_sting_3.4.png poster17.png   # 封面格
python3 music17.py
python3 build_main.py
```

## 重新產生 IG 版（1080×1920，32.5 秒）
```bash
node render5.js video intro sting jorge cancel camila assigned climax
mkdir -p ig && node gen_ig.js
python3 music17.py            # 若還沒產生 music17.wav
python3 build_ig.py
```

## 常見修改
- **改文字**：在 `story4.html` 裡搜尋要改的西語句子；改底部主標就改場景的 `kick` / `lines`。
- **改長度**：場景的 `dur` 與 `render4.js` 裡的時長表要一起改，`build_main.py` 的 `segs` 和轉場時間點 `bounds`、`music17.py` 的時間點也要跟著調整。
- **換 QR**：替換 `qr_clean.png`，再用 `verify_qr.py` 確認能解碼。

> 備註：`story4.html` 裡仍保留早期版本的場景（`OLD`、`more` 等），部分由新場景重用，刪除前請先確認沒有被引用。
