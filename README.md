# 工廠訂便當系統

一個完整的工廠員工訂餐管理系統，包含員工訂購功能和管理員維護功能。

## 功能特點

### 員工端功能
- ✅ 員工登入驗證
- ✅ 今日訂餐（午餐/晚餐）
- ✅ 訂餐截止時間控制（午餐 08:30，晚餐 16:00）
- ✅ 一週/當月訂餐（批量訂購）
- ✅ 訂單取消
- ✅ 歷史訂單查詢

### 管理員端功能
- ✅ 管理員登入
- ✅ 部門主檔維護（CRUD）
- ✅ 員工主檔維護（CRUD）
- ✅ 訂餐窗口維護（CRUD）
- ✅ 訂單查詢與修改（不受截止時間限制）
- ✅ 統計報表（餐點數量統計、員工訂購統計）

## 系統架構

```
factory-order-system/
├── FoodOrder.py          # 核心業務邏輯類
├── app.py                # Flask Web API
├── requirements.txt      # Python依賴包
├── README.md            # 使用說明
├── data/                # 數據存儲目錄（自動創建）
│   ├── departments.json  # 部門數據
│   ├── employees.json    # 員工數據
│   ├── windows.json      # 窗口數據
│   └── orders.json       # 訂單數據
└── [前端文件]
    ├── index.html
    ├── admin_dashboard.html
    ├── admin_login.html
    └── styles.css
```

## 安裝與運行

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 運行方式

#### 方式一：命令行介面（測試用）

直接運行 `FoodOrder.py`：

```bash
python FoodOrder.py
```

這會啟動一個簡單的命令行介面，可以用來測試系統功能。

#### 方式二：Flask Web API

運行 `app.py` 啟動 Web API 服務：

```bash
python app.py
```

API 服務將在 `http://localhost:5000` 啟動。

### 3. 使用前端界面

如果有前端 HTML 文件，可以通過以下方式訪問：

1. 直接打開 `index.html` 使用前端界面（需要修改前端代碼以連接 API）
2. 或使用 Flask 提供靜態文件服務

## API 端點說明

### 員工 API

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/employee/login` | 員工登入 |
| POST | `/api/employee/logout` | 員工登出 |
| GET | `/api/employee/today-orders` | 獲取今日訂單 |
| POST | `/api/employee/order` | 創建訂單 |
| POST | `/api/employee/cancel-order` | 取消訂單 |
| GET | `/api/employee/weekly-orders` | 獲取一週訂單 |
| GET | `/api/employee/history` | 獲取歷史訂單 |

### 管理員 API

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/admin/login` | 管理員登入 |
| POST | `/api/admin/logout` | 管理員登出 |
| GET | `/api/admin/departments` | 獲取部門列表 |
| POST | `/api/admin/departments` | 新增/修改部門 |
| DELETE | `/api/admin/departments/<oid>` | 刪除部門 |
| GET | `/api/admin/employees` | 獲取員工列表 |
| POST | `/api/admin/employees` | 新增/修改員工 |
| DELETE | `/api/admin/employees/<oid>` | 刪除員工 |
| GET | `/api/admin/windows` | 獲取窗口列表 |
| POST | `/api/admin/windows` | 新增/修改窗口 |
| DELETE | `/api/admin/windows/<oid>` | 刪除窗口 |
| GET | `/api/admin/orders` | 查詢訂單 |
| PUT | `/api/admin/orders` | 修改訂單 |
| GET | `/api/admin/stats/meal-quantity` | 餐點數量統計 |
| GET | `/api/admin/stats/employee-orders` | 員工訂購統計 |

## 預設帳號

### 管理員
- 帳號：`admin`
- 密碼：`1234`

### 測試員工
- 員工編號：`93800`，密碼：`1234`（林淑鈺）
- 員工編號：`28109`，密碼：`1234`（詹金璋）
- 員工編號：`2400305`，密碼：`1234`（王瀚章）

## 數據存儲

系統使用 JSON 文件存儲數據，所有數據文件保存在 `data/` 目錄下：

- `departments.json` - 部門主檔
- `employees.json` - 員工主檔
- `windows.json` - 訂餐窗口主檔
- `orders.json` - 訂單數據

首次運行時會自動創建預設數據。

## 訂餐規則

- **午餐截止時間**：每日 08:30
- **晚餐截止時間**：每日 16:00（4:00 PM）
- **管理員修改**：不受截止時間限制
- **工作日期**：系統預設週一至週五為工作日

## 技術特點

- 使用 Python 3 開發
- Flask 提供 RESTful API
- JSON 文件存儲（可輕鬆擴展為數據庫）
- 完整的業務邏輯封裝
- 支持命令行和 Web API 兩種使用方式

## 注意事項

1. 首次運行會自動創建 `data/` 目錄和預設數據
2. 生產環境請修改 `app.py` 中的 `secret_key`
3. 建議將 JSON 文件存儲改為數據庫（SQLite/MySQL/PostgreSQL）
4. 可根據需要添加身份驗證機制（JWT等）

## 開發者

系統使用模塊化設計，易於擴展和維護。核心業務邏輯在 `FoodOrder.py` 中，API 介面在 `app.py` 中。

## 授權

本系統供學習和內部使用。

