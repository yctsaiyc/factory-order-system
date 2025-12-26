# 工廠員工訂餐系統 (Factory Employee Food Order System)

這是一個使用 C# 和 .NET 7 開發的工廠員工訂餐系統。它提供了一個簡單的 Web 介面，讓員工可以預訂午餐和晚餐，並讓管理員可以管理系統資料。

## 主要功能

### 員工端
- **登入/登出**: 員工使用員工編號和密碼登入。
- **今日訂餐**: 查詢今天的訂餐狀態，並可訂購或取消午餐/晚餐。
- **歷史紀錄查詢**: 查詢自己的歷史訂餐紀錄。

### 管理員端
- **主檔資料維護 (CRUD)**:
    - 部門管理
    - 員工管理
    - 訂餐窗口管理
- **訂單管理**:
    - 查詢所有員工的訂單 (可依條件篩選)。
    - 手動修改或取消訂單。
- **統計報表**: 產生訂餐數量的統計報表。

## 技術棧

- **後端**: C# .NET 7, ASP.NET Core Web API
- **前端**: HTML, CSS, JavaScript
- **測試**: MSTest

## 如何在本機運行

### 1. 執行後端服務

在專案根目錄下，開啟終端機並執行以下指令：

```bash
dotnet run
```

服務預設會在本機的 5000 和 5001 (https) port 啟動。您會在終端機看到類似以下的輸出：

```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: https://localhost:5001
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5000
```

### 2. 開啟使用者介面

- **員工登入頁面**: 打開瀏覽器，訪問 [http://localhost:5000](http://localhost:5000)

## 如何執行單元測試

在專案根目錄下，開啟終端機並執行以下指令：

```bash
dotnet test
```

此指令會自動尋找並執行 `FoodOrderSystem.Tests` 專案中的所有測試。
