# 工廠訂便當系統 - C# .NET 7.0 版本

## 系統要求

- .NET 7.0 SDK 或更高版本
- Visual Studio 2022 / VS Code / Rider 或其他 .NET 開發工具

## 安裝與運行

### 1. 還原依賴

```bash
dotnet restore
```

### 2. 運行應用

```bash
dotnet run
```

應用將在 `http://localhost:5000` 啟動。

### 3. Swagger API 文檔（開發模式）

訪問 `http://localhost:5000/swagger` 查看 API 文檔。

## 項目結構

```
FoodOrderSystem/
├── Controllers/          # API 控制器
│   ├── EmployeeController.cs    # 員工端 API
│   ├── AdminController.cs       # 管理員端 API
│   └── SessionController.cs     # Session 管理
├── Models/              # 數據模型
│   ├── Enums.cs         # 枚舉類型
│   ├── Department.cs    # 部門模型
│   ├── Employee.cs      # 員工模型
│   ├── OrderWindow.cs   # 窗口模型
│   └── MealOrder.cs     # 訂單模型
├── Services/            # 業務邏輯服務
│   └── FoodOrderService.cs  # 核心業務邏輯
├── Program.cs           # 應用入口點
├── appsettings.json     # 配置文件
└── FoodOrderSystem.csproj  # 項目文件
```

## API 端點

與 Python 版本保持相同的 API 接口：

### 員工 API

- `POST /api/employee/login` - 員工登入
- `POST /api/employee/logout` - 員工登出
- `GET /api/employee/today-orders` - 獲取今日訂單
- `POST /api/employee/order` - 創建訂單
- `POST /api/employee/cancel-order` - 取消訂單
- `GET /api/employee/weekly-orders` - 獲取一週訂單
- `POST /api/employee/weekly-orders` - 批量保存一週訂單
- `GET /api/employee/history` - 獲取歷史訂單

### 管理員 API

- `POST /api/admin/login` - 管理員登入
- `POST /api/admin/logout` - 管理員登出
- `GET /api/admin/departments` - 獲取部門列表
- `POST /api/admin/departments` - 新增/修改部門
- `DELETE /api/admin/departments/{oid}` - 刪除部門
- `GET /api/admin/employees` - 獲取員工列表
- `POST /api/admin/employees` - 新增/修改員工
- `DELETE /api/admin/employees/{oid}` - 刪除員工
- `GET /api/admin/windows` - 獲取窗口列表
- `POST /api/admin/windows` - 新增/修改窗口
- `DELETE /api/admin/windows/{oid}` - 刪除窗口
- `GET /api/admin/orders` - 查詢訂單
- `PUT /api/admin/orders` - 修改訂單
- `GET /api/admin/stats/meal-quantity` - 餐點數量統計
- `GET /api/admin/stats/employee-orders` - 員工訂購統計

### 通用 API

- `GET /api/session/check-session` - 檢查 session 狀態

## 數據存儲

系統使用 JSON 文件存儲數據，所有數據文件保存在 `data/` 目錄下：

- `departments.json` - 部門主檔
- `employees.json` - 員工主檔
- `windows.json` - 訂餐窗口主檔
- `orders.json` - 訂單數據

首次運行時會自動創建預設數據。

## 預設帳號

### 管理員
- 帳號：`admin`
- 密碼：`1234`

### 測試員工
- 員工編號：`93800`，密碼：`1234`（林淑鈺）
- 員工編號：`28109`，密碼：`1234`（詹金璋）
- 員工編號：`2400305`，密碼：`1234`（王瀚章）

## 前端頁面

訪問以下 URL 使用前端界面：

- `http://localhost:5000/` - 根頁面（API 信息）
- `http://localhost:5000/test` - API 測試頁面
- `http://localhost:5000/employee` - 員工訂餐頁面
- `http://localhost:5000/admin/login` - 管理員登入頁面
- `http://localhost:5000/admin` - 管理員後台頁面

## 開發說明

### Session 管理

使用 ASP.NET Core 的 Session 中間件來管理用戶登入狀態。Session 數據存儲在內存中。

### CORS 配置

已配置允許所有來源的 CORS 策略，用於開發環境。生產環境應限制允許的來源。

### JSON 序列化

使用 Newtonsoft.Json 進行 JSON 序列化和反序列化，與 Python 版本保持數據格式兼容。

## 部署

### 發佈應用

```bash
dotnet publish -c Release -o ./publish
```

### 運行發佈版本

```bash
cd publish
dotnet FoodOrderSystem.dll
```

## 從 Python 版本遷移

C# 版本與 Python 版本保持相同的 API 接口和數據格式，可以直接替換使用。現有的前端代碼和測試腳本無需修改。

## 授權

本系統供學習和內部使用。

