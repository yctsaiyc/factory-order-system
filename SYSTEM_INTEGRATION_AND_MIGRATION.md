# 系統整合與遷移說明

此文件以中文、淺顯易懂為原則，說明從前端以 localStorage 儲存轉為後端 API 儲存的整體思路、必要步驟、驗證要點與回滾方案，並提供優先順序建議，方便團隊快速執行與測試。

---

## 目標

- 將使用者資料與訂單儲存從瀏覽器端 `localStorage` 遷移至後端（`FoodOrderService` 與 API）。
- 確保使用者操作（登入、今日訂單、一週訂單、歷史查詢）在前後端之間一致且持久化。
- 保持最小破壞（逐步遷移、可回滾），並在短期內修正使用者立即會遇到的錯誤。

---

## 核心思路（簡要）

1. 把原本在前端讀/寫 `localStorage` 的邏輯，改成呼叫後端 API。前端仍負責 UI 與驗證，後端負責資料一致性、持久化與商業邏輯。
2. 前後端以 session 或 cookie 管理登入狀態（後端現有 `SessionController` 與 `EmployeeController` 支援 session）。
3. 保留現有 `FoodOrderService` 的資料結構（orders key 與回傳格式），減少後端調整量；前端直接使用後端回傳的 JSON 結構填 UI。
4. 逐頁面遷移：先員工端（index.html）→ 再管理員端（admin_dashboard.html），逐步驗證與修復。

---

## 具體步驟（可執行清單）

1. 建立 API helper（前端）
   - 實作通用 `apiRequest(path, method, body)`：自動加 `credentials: 'include'`，處理錯誤與 JSON 解析。

2. 登入流程改為呼叫後端
   - 前端送 `POST /api/employee/login`，後端建立 session（目前已支援）。
   - 前端收到成功回應後顯示使用者資訊與切換頁面。

3. 今日訂單顯示
   - 前端呼叫 `GET /api/employee/today-orders` 取得 `lunch` / `dinner` 與 cutoff 資訊，更新 UI。

4. 建立與取消訂單
   - 建立：`POST /api/employee/order`（body: { MealType, DietType, RicePortion, Date? }）。
   - 取消：`POST /api/employee/cancel-order`（body: { MealType, Date? }）。
   - 以後端回傳成功/失敗訊息決定前端提示。

5. 一週/當月操作
   - 讀取：`GET /api/employee/weekly-orders?weekType=current|next|month` → 回傳每個日期的訂單狀態（LUNCH/DINNER 或 null）。
   - 儲存：`POST /api/employee/weekly-orders`，body 範例：{ Orders: [{ Date, MealType, DietType, RicePortion }, ...] }。
   - 後端逐筆處理（Create / Cancel），並回傳摘要（成功與失敗數量與錯誤訊息）。

6. 歷史查詢
   - 前端改為 `GET /api/employee/history?dateFrom=yyyy-MM-dd&dateTo=yyyy-MM-dd`，呈現由後端回傳的清單。

7. 管理員頁面遷移（次階段）
   - 把 `admin_dashboard.html` 中 `localStorage` 的 master 資料改為呼叫：
     - `GET /api/admin/departments`
     - `GET /api/admin/employees`
     - `GET /api/admin/windows`
   - 管理員的 CRUD 呼叫對應 API（專案已有 `AdminController` 可直接使用），並更新 UI 回傳處理結果。

---

## API Contract（前端與後端需對齊的最小契約）

- `POST /api/employee/login` → body: { EmpId, Password } → 回傳 { success, message, employee: { EmpID, EmpName, DeptCode } }
- `GET /api/employee/today-orders` → 回傳 { success, data: { date, lunch: {...}|null, dinner: {...}|null, lunch_cutoff: bool, dinner_cutoff: bool } }
- `POST /api/employee/order` → body: { MealType, DietType, RicePortion, Date? } → 回傳 { success, message }
- `POST /api/employee/cancel-order` → body: { MealType, Date? } → 回傳 { success, message }
- `GET /api/employee/weekly-orders?weekType=...` → 回傳 { success, data: { [date]: { LUNCH: obj|null, DINNER: obj|null } } }
- `POST /api/employee/weekly-orders` → body: { Orders: [...] } → 回傳 { success, message, success_count, error_count, errors[] }
- `GET /api/employee/history?dateFrom=...&dateTo=...` → 回傳 { success, data: [ { Date, EmpID, MealType, DietType, RicePortion, IsOrdered, OrderTime, AdminModified } ] }

> 注意：若後端回傳格式與前端期望不符，需在後端或前端做一層適配。

---

## 驗證要點與測試場景

1. 登入/登出
   - 正確帳密能登入，會建立 session（`/api/session/check-session` 檢查）。
2. 今日訂單建立/取消
   - 在截止前可建立/取消；截止後 API 應回 400/失敗並回傳友善訊息。
3. 一週儲存
   - 部分日期帶空值代表取消；檢查後端是否正確新增/刪除。
4. 多標籤/多視窗
   - 同時在兩個頁面操作時，資料不應互相覆蓋；建議後端以鎖或交易處理寫入。
5. 錯誤處理
   - 模擬後端錯誤或網路失敗，前端應顯示錯誤訊息並避免資料遺失。

---

## 回滾方案

- 如果上線後出現嚴重錯誤，可暫時改回前端 `localStorage`（保留原程式碼分支），或關閉前端新功能回復到舊頁面版本。
- 在部署前建立資料備份（若做 DB 遷移），並在版本控制中保留變更紀錄。

---

## 優先順序（建議）

1. 員工端：登入、今日訂單、建立/取消（最短路徑修正使用者痛點）。
2. 一週/當月表單（把表單儲存改為 API），並測試大量操作情境。 
3. 歷史查詢與錯誤顯示強化。 
4. 管理員後台遷移與 master 資料同步（次階段）。

---

## 其他注意事項

- 同源政策與 cookie 設定：若前端/後端在不同 origin，請確保 CORS 與 SameSite、Secure 設定允許 cookie。 
- Session vs Token：目前專案用 session 存放登入狀態；若未來改 JWT，前端需調整儲存與每次呼叫的授權標頭。
- 資料一致性：短期可使用 `lock` 或後端同步寫入以避免 race condition；長期建議使用資料庫（SQLite/SQL Server）替代 JSON 檔案。

---

## 如需，我可以：
- 依此文件繼續把 `admin_dashboard.html` 遷移成呼叫後端（我會依序提交變更）；或
- 製作一份簡單的測試清單（step-by-step）讓 QA 驗收；或
- 幫你建立 Dockerfile 並示範在 WSL/docker 中執行用以驗證整合。

