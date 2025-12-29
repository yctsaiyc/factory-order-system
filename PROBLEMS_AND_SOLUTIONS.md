## 專案現況問題與建議解決方案

### 概要
此專案為簡單的工廠員工訂餐系統（ASP.NET Core + 靜態前端），資料以 `data/*.json` 儲存。系統功能齊全但有數個可改善之處（可靠性、資安、可維運性、部署）。

---

### 主要問題清單

- **同步檔案 I/O（使用 JSON 檔）**：所有資料儲存在單一 JSON 檔案並以同步方式讀寫，會在多個並發請求下造成資料競爭、資料遺失或損壞。  
- **密碼與管理員帳密明文**：員工 `Password` 與管理員帳密為明文，無雜湊或安全儲存。  
- **硬編碼的管理員帳密**（`ADMIN_ACCOUNT` / `ADMIN_PASSWORD`）：不安全且難以管理。  
- **Session 存在記憶體（開發環境）**：使用 `DistributedMemoryCache` + Session，在多節點或容器化環境不適用。  
- **CORS 過於寬鬆**：`AllowAnyOrigin`／`AnyMethod`／`AnyHeader`，生產環境應收緊。  
- **錯誤處理與日誌不足**：缺少集中式 logging 與錯誤追蹤。  
- **測試覆蓋不足**：目前測試只有範例測試，未覆蓋 `FoodOrderService` 的主要邏輯（截止檢查、建立/取消/更新訂單、CRUD 等）。  
- **部署/執行注意事項**：在公司 Windows 環境直接執行時可能會遭防毒或系統政策攔截（已觀察 10013 綁定被拒），缺少 Dockerfile 或方便在 WSL/Docker 運行的配置。  
- **安全性檢查不足**：缺少輸入驗證、API 授權（session 仍可被竄改的風險）、輸入邊界檢查等。  
- **時區/日期處理**：使用系統時間 `DateTime.Now`，未考慮時區或一致性的時間來源（若需跨主機或日光節約時間會有問題）。

---

### 建議的解決方案（分階段）

**優先（短期，可快速降低風險）**

1. 將密碼從明文改為雜湊（bcrypt/Argon2）：在 `SaveEmployee` 時對密碼做雜湊；在比對時使用雜湊比對。  
   - 估時：半天到 1 天（含相依性與測試）。
   - 指令/套件建議：使用 `BCrypt.Net-Next` 或 `Argon2` 套件（NuGet）。

2. 將管理員帳號改為環境變數或 `appsettings.json` 配置（非硬編碼）。  
   - 估時：1 小時。

3. 在 `FoodOrderService` 實作簡單的檔案鎖或同步鎖（`lock`）以避免同時寫入造成資料破壞；同時加上基本例外處理與重試策略。  
   - 估時：半天。

4. 收緊 CORS 與 API 權限：在 production 設定允許的 origin，並對管理員 API 加上更嚴格的授權檢查。  
   - 估時：半天。

**中期（提升可靠性、可維運性）**

5. 導入輕量資料庫（推薦 SQLite）或 EF Core：將 JSON 儲存遷移到 SQLite（單檔、輕量、支援鎖與交易），或使用 EF Core 以便未來換到 PostgreSQL/SQL Server。  
   - 估時：1~3 天（取決於資料模型與遷移程式）。

6. 將 Session 從 Memory 換成 Distributed Cache（Redis）或使用 JWT 授權：若持續使用 session，建議在多節點環境選 Redis。若要無狀態 API，建議改用 JWT。  
   - 估時：1~2 天。

7. 新增 logging（例如 `Microsoft.Extensions.Logging`）與錯誤追蹤（Sentry/Seq 等）。  
   - 估時：半天到 1 天。

**長期（測試、部署、維運）**

8. 擴充測試覆蓋：新增單元測試與整合測試（模擬 I/O 或使用測試資料庫），覆蓋 `FoodOrderService` 的關鍵邏輯（截止時間、Create/Cancel/Update、統計）。  
   - 估時：1~3 天（逐步補齊）。

9. 建立 Dockerfile 與 CI/CD 流程：在 WSL/docker 環境內執行能避開 Windows 的限制，也方便部署。  
   - 估時：半天到 1 天。

10. 安全檢查與強化：輸入驗證（防 XSS/Injection）、HTTPS 強制、Content-Security-Policy、避免在靜態檔案目錄暴露敏感檔案，審查第三方套件。  
    - 估時：視範圍而定。

---

### 具體執行步驟（建議順序與可複製指令）

1) 在 WSL 開發（短期）

   - 在 WSL 裡還原並執行：

   ```bash
   cd /mnt/c/Users/***/test/factory-order-system
   dotnet restore
   dotnet run --project FoodOrderSystem.csproj --urls "http://0.0.0.0:5000"
   ```

2) 修正第一波高風險項目（密碼雜湊、管理員設定檔、檔案鎖）

   - 新增 BCrypt 套件：
   ```powershell
   dotnet add package BCrypt.Net-Next
   ```

   - 更新 `FoodOrderService`：在 `SaveEmployee` 雜湊密碼；在 `VerifyEmployee` 比對雜湊。  
   - 對 `ADMIN_ACCOUNT`/`ADMIN_PASSWORD` 改為從 `appsettings.json` 或 `DOTNET_` 環境變數讀取。

3) 建立 SQLite 資料層（中期目標）

   - 新增 EF Core 與 SQLite：
   ```powershell
   dotnet add package Microsoft.EntityFrameworkCore
   dotnet add package Microsoft.EntityFrameworkCore.Sqlite
   dotnet add package Microsoft.EntityFrameworkCore.Design
   ```

   - 建立簡單的 migration 與轉換腳本：將 `data/*.json` 匯入 SQLite 作為一次性遷移工具。

4) 新增 Dockerfile（方便在 WSL/docker 上運行）

   - 建議簡單 multi-stage Dockerfile，把應用執行在 linux runtime：

   ```dockerfile
   FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
   WORKDIR /src
   COPY . ./
   RUN dotnet publish FoodOrderSystem.csproj -c Release -o /app/publish

   FROM mcr.microsoft.com/dotnet/aspnet:7.0
   WORKDIR /app
   COPY --from=build /app/publish ./
   EXPOSE 5000
   ENTRYPOINT ["dotnet", "FoodOrderSystem.dll"]
   ```

5) 測試與 CI

   - 新增測試以覆蓋 `FoodOrderService` 關鍵行為；在 GitHub Actions 或其他 CI 執行 `dotnet test` 與 lint。

---

### 建議優先順序（簡短）

1. 密碼雜湊 + 移除硬編碼管理員（高）  
2. 檔案 I/O 加鎖或短期改為 SQLite（高）  
3. 在 WSL/docker 執行並建立 Dockerfile（中）  
4. 加入 logging、錯誤處理、收緊 CORS（中）  
5. 擴充測試與 CI（中至長）  

---

### 補充說明

- 若你希望我直接幫你：我可以逐步提交 PR／檔案修改，第一步建議從「密碼雜湊」與「管理員改配置」著手。  
- 若偏好短期在 WSL 開發：建立 `Dockerfile` 並在 WSL/docker 執行是最穩定、可重現的方式，也較少遇到 Windows 企業端安全政策的干擾。

檔案已產出於本專案根目錄。
