# CareQueue — 原始碼包(給拿到 zip 的人)

`carequeue-demo/` 是 CareQueue 的完整原始碼,取自 git `main` 分支的 commit `29c23ca`。
裡面**沒有任何密碼、token 或資料庫**,可以安全傳送。

CareQueue 是一個門診預約與候補名單的示範系統(智利 Concepción 的公立衛生中心),
臨床資料全部以 HL7 FHIR R4 標準儲存,病人透過 Telegram 或 WhatsApp 收提醒、回覆確認。

---

## 一、在自己的電腦上跑起來(Windows / macOS / Linux 都一樣)

### 1. 安裝 Node.js

到 <https://nodejs.org> 下載 **LTS 版本**,照安裝程式做完。
需要 Node **22.13 以上**。裝完打開終端機確認:

- Windows:開「PowerShell」或「命令提示字元」
- macOS:開「終端機」

```bash
node --version
```

### 2. 解壓縮、進到資料夾

```bash
cd carequeue-demo
```

(Windows 的 PowerShell 也是同一句。)

### 3. 下載套件

```bash
npm install
```

這會依 `package.json` 下載約 400 個套件、約 700 MB 到 `node_modules/` 資料夾。
只需要做一次,幾分鐘。

### 4. 設定一把加密金鑰

程式用這把金鑰加密 Telegram / Twilio 的憑證。在專案根目錄建一個叫 `.dev.vars` 的檔案:

```
CREDENTIAL_KEY=<32 bytes 的 base64 字串>
```

產生方法(任一)——

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

把印出來的字串貼到等號後面。**這個檔案不要進 git、不要傳給別人。**

### 5. 建立資料庫

```bash
npm run build
```

然後把 10 個遷移檔依序套用(`0000` 到 `0009`):

```bash
npx wrangler d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_motionless_bullseye.sql
```

把最後的檔名換成 `drizzle/` 裡的下一個,重複到 `0009_drop_pre_fhir_tables.sql` 為止。
(檔名可以 `ls drizzle/*.sql` 或在檔案總管看。)

### 6. 開店

```bash
npm run dev
```

瀏覽器打開 <http://localhost:3000>。第一次會要求登入,本機版用內建的假登入:
<http://localhost:3000/signin-with-chatgpt?return_to=/>

要停止:在終端機按 `Ctrl + C`。

---

## 二、接上 Telegram(示範用)

1. 在 Telegram 找 **@BotFather**,送 `/newbot`,照提示命名,會拿到一串 token。
2. 網頁的 **Messaging setup** 分頁 → 選 Telegram → 貼上 token → 儲存。
3. 按 **Generate link code**,拿到一組六位碼。
4. 為每個示範病人開一個 Telegram 群組,把 bot 加進去,在群組裡送
   `/start@你的bot名稱 <六位碼>`。
5. 回網頁等 15 秒(頁面要開著),該群組就會出現在已登記裝置清單。
   每個病人重複 3–5 步。
6. 在 BotFather 用 `/setcommands` 設定指令選單:
   ```
   cita - Ver mis horas
   confirm - Confirmar mi hora
   reschedule - Cambiar mi hora a otro día (día/mes)
   ```
7. 若要讓 bot 看得到群組裡沒有斜線的訊息(例如單純回 `C`),在 BotFather 用
   `/setprivacy` 關閉 privacy mode,然後把 bot 移出群組再加回去。
   **只在示範用的群組這樣做**,因為 bot 會讀到群組裡所有訊息。

之後:Patients 分頁新增病人(選一個已登記的群組),再到 Appointments 訂預約、送提醒。
病人在群組回 `/confirm` 即可確認——**但網頁必須開著**,程式每 15 秒才去 Telegram 拿一次新訊息。

---

## 三、驗證程式沒壞

```bash
npm run build
npx tsc --noEmit
node --test tests/rules.test.ts tests/fhir.test.mjs tests/fhir-workflow.test.mjs
```

測試用假的 Telegram / Twilio,不會送出任何真實訊息。

---

## 四、部署到 ChatGPT Sites

`.openai/hosting.json` 裡有這個專案原本的 `project_id`。**請沿用同一個 Site,不要建第二個。**
部署前確認 Site 的 runtime secret 有 `CREDENTIAL_KEY`;遷移由平台套用
(`dist/.openai/drizzle/**`)。部署後雲端資料庫是空的,需要重新貼 bot token、
重新連結群組、重新建立病人(或用網頁上的 FHIR Bundle 匯入功能)。

---

## 五、要了解這個系統

- `CLAUDE.md` — 專案規則與設計決策(英文,寫給開發者與 AI 助手)
- `README.md` — 使用者角度的設定與限制(英文)
- 程式碼本身註解很多,尤其 `lib/fhir/` 底下每個檔案開頭都說明它負責什麼

主要結構:

| 位置 | 負責 |
|---|---|
| `app/carequeue.tsx` | 網頁介面 |
| `app/api/` | 三個 API:workspace(讀)、actions(寫)、fhir(匯入匯出) |
| `lib/fhir/` | FHIR 資源、文件庫、排程、訊息、匯入匯出 |
| `lib/providers.ts` | 唯一會呼叫 Telegram / Twilio API 的檔案 |
| `db/schema.ts`、`drizzle/` | 資料表定義與遷移 |
| `tests/` | 每個流程的測試 |

---

## 六、注意事項

- 所有病人資料一律虛構。這是示範系統,未連接任何真實醫療資訊系統。
- Twilio 走免費試用時只能送一則固定範本、只能一個收件人;要送真實內容需升級付費帳號。
- 不要把 `.dev.vars`、bot token、Twilio 憑證提交到 git 或傳給他人。
