# -*- coding: utf-8 -*-
"""
API 測試腳本
使用 Python requests 庫進行自動化測試
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

# 測試會話（用於保存 cookies）
session = requests.Session()

# 測試結果統計
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}


def print_test(name):
    """打印測試名稱"""
    print(f"\n{'='*60}")
    print(f"測試: {name}")
    print(f"{'='*60}")


def assert_test(condition, message):
    """斷言測試結果"""
    test_results["total"] += 1
    if condition:
        test_results["passed"] += 1
        print(f"✓ {message}")
        return True
    else:
        test_results["failed"] += 1
        test_results["errors"].append(message)
        print(f"✗ {message}")
        return False


def format_date(date):
    """格式化日期"""
    return date.strftime("%Y-%m-%d")


# ========== 一、基礎功能測試 ==========

def test_service_running():
    """測試服務是否運行"""
    print_test("1. 服務啟動測試")
    try:
        response = requests.get("http://localhost:5000/")
        assert_test(response.status_code == 200, "根路由可訪問")
        assert_test("API" in response.text, "API 信息頁面內容正確")
    except Exception as e:
        assert_test(False, f"服務無法訪問: {e}")


# ========== 二、員工端功能測試 ==========

def test_employee_login():
    """測試員工登入"""
    print_test("2.1 員工登入測試")
    
    # 正確登入
    response = session.post(f"{BASE_URL}/employee/login", json={
        "emp_id": "93800",
        "password": "1234"
    })
    result = response.json()
    assert_test(response.status_code == 200, "登入請求成功")
    assert_test(result.get("success") == True, "登入成功")
    assert_test("employee" in result, "返回員工信息")
    
    # 錯誤密碼
    response = session.post(f"{BASE_URL}/employee/login", json={
        "emp_id": "93800",
        "password": "wrong"
    })
    result = response.json()
    assert_test(result.get("success") == False, "錯誤密碼登入失敗")
    
    # 不存在的員工
    response = session.post(f"{BASE_URL}/employee/login", json={
        "emp_id": "99999",
        "password": "1234"
    })
    result = response.json()
    assert_test(result.get("success") == False, "不存在員工登入失敗")


def test_check_session():
    """測試 Session 檢查"""
    print_test("2.2 Session 檢查測試")
    
    response = session.get(f"{BASE_URL}/check-session")
    result = response.json()
    assert_test(response.status_code == 200, "Session 檢查請求成功")
    assert_test(result.get("success") == True, "Session 存在")
    assert_test(result.get("emp_id") == "93800", "Session 包含正確的員工ID")


def test_today_orders():
    """測試今日訂單查詢"""
    print_test("2.3 今日訂單查詢測試")
    
    response = session.get(f"{BASE_URL}/employee/today-orders")
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回訂單數據")
    
    data = result["data"]
    assert_test("date" in data, "包含日期")
    assert_test("lunch" in data, "包含午餐字段")
    assert_test("dinner" in data, "包含晚餐字段")


def test_create_order():
    """測試創建訂單"""
    print_test("2.4 創建訂單測試")
    
    # 先檢查截止時間狀態
    response = session.get(f"{BASE_URL}/employee/today-orders")
    cutoff_info = response.json()["data"]
    lunch_cutoff = cutoff_info.get("lunch_cutoff", False)
    dinner_cutoff = cutoff_info.get("dinner_cutoff", False)
    
    # 根據截止時間選擇可用的餐別
    if lunch_cutoff and dinner_cutoff:
        print("  注意: 午餐和晚餐都已截止，跳過訂單創建測試")
        assert_test(True, "已截止時間檢查（跳過訂單創建）")
        return
    
    # 選擇未截止的餐別進行測試
    meal_type = "DINNER" if lunch_cutoff else "LUNCH"
    meal_name = "晚餐" if lunch_cutoff else "午餐"
    
    print(f"  測試 {meal_name} 訂購（當前時間未截止）")
    
    response = session.post(f"{BASE_URL}/employee/order", json={
        "meal_type": meal_type,
        "diet_type": "MEAT",
        "rice_portion": "FULL"
    })
    
    result = response.json()
    
    # 如果返回 400，可能是其他原因（如已經訂過），檢查錯誤訊息
    if response.status_code == 400:
        error_msg = result.get("message", "")
        if "截止" in error_msg:
            print(f"  注意: {meal_name}已截止，跳過測試")
            assert_test(True, f"截止時間檢查（{meal_name}已截止）")
        else:
            assert_test(False, f"創建訂單失敗: {error_msg}")
        return
    
    assert_test(response.status_code == 200, "創建訂單請求成功")
    assert_test(result.get("success") == True, "訂單創建成功")
    
    # 再次查詢確認訂單存在
    response = session.get(f"{BASE_URL}/employee/today-orders")
    result = response.json()
    data = result["data"]
    
    # 根據餐別檢查對應的字段
    order_field = "dinner" if meal_type == "DINNER" else "lunch"
    assert_test(data.get(order_field) is not None, f"{meal_name}訂單已創建並可查詢到")


def test_cancel_order():
    """測試取消訂單"""
    print_test("2.5 取消訂單測試")
    
    # 先檢查截止時間，選擇一個可能未截止的餐別
    response = session.get(f"{BASE_URL}/employee/today-orders")
    cutoff_info = response.json()["data"]
    dinner_cutoff = cutoff_info.get("dinner_cutoff", False)
    
    # 如果晚餐未截止，嘗試創建並取消；否則跳過
    if dinner_cutoff:
        print("  注意: 晚餐已截止，跳過取消訂單測試")
        assert_test(True, "已截止時間檢查（跳過取消訂單）")
        return
    
    # 先創建一個訂單
    create_response = session.post(f"{BASE_URL}/employee/order", json={
        "meal_type": "DINNER",
        "diet_type": "VEG",
        "rice_portion": "HALF"
    })
    
    # 如果創建失敗（如已存在或其他原因），嘗試取消現有訂單
    if create_response.status_code != 200:
        print("  注意: 訂單可能已存在，直接測試取消")
    
    # 取消訂單
    response = session.post(f"{BASE_URL}/employee/cancel-order", json={
        "meal_type": "DINNER"
    })
    result = response.json()
    
    # 如果返回 400，檢查是否因為已截止
    if response.status_code == 400:
        error_msg = result.get("message", "")
        if "截止" in error_msg:
            print("  注意: 取消時已截止，跳過測試")
            assert_test(True, "截止時間檢查（取消時已截止）")
            return
    
    assert_test(response.status_code == 200, "取消訂單請求成功")
    assert_test(result.get("success") == True, "訂單取消成功")


def test_weekly_orders():
    """測試一週訂單"""
    print_test("2.6 一週訂單測試")
    
    # 獲取本週訂單
    response = session.get(f"{BASE_URL}/employee/weekly-orders?week_type=current")
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回訂單數據")


def test_history_orders():
    """測試歷史訂單查詢"""
    print_test("2.7 歷史訂單查詢測試")
    
    today = datetime.now()
    date_from = format_date(today - timedelta(days=30))
    date_to = format_date(today)
    
    response = session.get(f"{BASE_URL}/employee/history", params={
        "date_from": date_from,
        "date_to": date_to
    })
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回訂單數據")
    assert_test("count" in result, "返回訂單數量")


def test_employee_logout():
    """測試員工登出"""
    print_test("2.8 員工登出測試")
    
    response = session.post(f"{BASE_URL}/employee/logout")
    result = response.json()
    assert_test(response.status_code == 200, "登出請求成功")
    assert_test(result.get("success") == True, "登出成功")
    
    # 驗證 session 已清除
    response = session.get(f"{BASE_URL}/check-session")
    result = response.json()
    assert_test(result.get("success") == False, "Session 已清除")


# ========== 三、管理員端功能測試 ==========

def test_admin_login():
    """測試管理員登入"""
    print_test("3.1 管理員登入測試")
    
    response = session.post(f"{BASE_URL}/admin/login", json={
        "account": "admin",
        "password": "1234"
    })
    result = response.json()
    assert_test(response.status_code == 200, "登入請求成功")
    assert_test(result.get("success") == True, "管理員登入成功")
    
    # 錯誤密碼
    response = session.post(f"{BASE_URL}/admin/login", json={
        "account": "admin",
        "password": "wrong"
    })
    result = response.json()
    assert_test(result.get("success") == False, "錯誤密碼登入失敗")


def test_departments():
    """測試部門主檔維護"""
    print_test("3.2 部門主檔維護測試")
    
    # 獲取部門列表
    response = session.get(f"{BASE_URL}/admin/departments")
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回部門數據")
    
    dept_count = len(result["data"])
    
    # 新增部門
    response = session.post(f"{BASE_URL}/admin/departments", json={
        "DeptCode": "TEST",
        "DeptName": "測試部門"
    })
    result = response.json()
    assert_test(response.status_code == 200, "新增請求成功")
    assert_test(result.get("success") == True, "部門新增成功")
    
    # 確認新增成功
    response = session.get(f"{BASE_URL}/admin/departments")
    new_count = len(response.json()["data"])
    assert_test(new_count == dept_count + 1, "部門數量增加")
    
    # 獲取新增的部門 OID（用於刪除測試）
    depts = response.json()["data"]
    test_dept = next((d for d in depts if d["DeptCode"] == "TEST"), None)
    if test_dept:
        test_dept_oid = test_dept["OID"]
        
        # 刪除測試部門
        response = session.delete(f"{BASE_URL}/admin/departments/{test_dept_oid}")
        result = response.json()
        assert_test(response.status_code == 200, "刪除請求成功")
        assert_test(result.get("success") == True, "部門刪除成功")


def test_employees():
    """測試員工主檔維護"""
    print_test("3.3 員工主檔維護測試")
    
    # 獲取員工列表
    response = session.get(f"{BASE_URL}/admin/employees")
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回員工數據")
    
    # 確認密碼已隱藏
    employees = result["data"]
    if employees:
        assert_test("Password" not in employees[0], "密碼已隱藏")
        assert_test("PasswordLength" in employees[0], "顯示密碼長度")


def test_windows():
    """測試窗口主檔維護"""
    print_test("3.4 窗口主檔維護測試")
    
    # 獲取窗口列表
    response = session.get(f"{BASE_URL}/admin/windows")
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回窗口數據")


def test_admin_orders():
    """測試管理員訂單查詢"""
    print_test("3.5 管理員訂單查詢測試")
    
    today = datetime.now()
    date_from = format_date(today - timedelta(days=7))
    date_to = format_date(today)
    
    response = session.get(f"{BASE_URL}/admin/orders", params={
        "date_from": date_from,
        "date_to": date_to
    })
    result = response.json()
    assert_test(response.status_code == 200, "查詢請求成功")
    assert_test(result.get("success") == True, "查詢成功")
    assert_test("data" in result, "返回訂單數據")


def test_admin_stats():
    """測試統計報表"""
    print_test("3.6 統計報表測試")
    
    today = datetime.now()
    date_from = format_date(today - timedelta(days=7))
    date_to = format_date(today)
    
    # 餐點數量統計
    response = session.get(f"{BASE_URL}/admin/stats/meal-quantity", params={
        "date_from": date_from,
        "date_to": date_to
    })
    result = response.json()
    assert_test(response.status_code == 200, "統計請求成功")
    assert_test(result.get("success") == True, "統計成功")
    
    # 員工訂購統計
    response = session.get(f"{BASE_URL}/admin/stats/employee-orders", params={
        "date_from": date_from,
        "date_to": date_to
    })
    result = response.json()
    assert_test(response.status_code == 200, "統計請求成功")
    assert_test(result.get("success") == True, "統計成功")


def test_admin_logout():
    """測試管理員登出"""
    print_test("3.7 管理員登出測試")
    
    response = session.post(f"{BASE_URL}/admin/logout")
    result = response.json()
    assert_test(response.status_code == 200, "登出請求成功")
    assert_test(result.get("success") == True, "登出成功")


# ========== 四、錯誤處理測試 ==========

def test_error_handling():
    """測試錯誤處理"""
    print_test("4. 錯誤處理測試")
    
    # 未登入訪問受保護端點
    new_session = requests.Session()
    response = new_session.get(f"{BASE_URL}/employee/today-orders")
    result = response.json()
    assert_test(response.status_code == 401, "未登入返回 401")
    
    # 無效的路徑
    response = requests.get(f"{BASE_URL}/invalid/path")
    assert_test(response.status_code == 404, "無效路徑返回 404")
    
    # 缺失必需參數
    admin_session = requests.Session()
    admin_session.post(f"{BASE_URL}/admin/login", json={
        "account": "admin",
        "password": "1234"
    })
    response = admin_session.post(f"{BASE_URL}/admin/departments", json={})
    result = response.json()
    assert_test(result.get("success") == False, "缺失參數返回錯誤")


# ========== 主測試函數 ==========

def run_all_tests():
    """運行所有測試"""
    print("\n" + "="*60)
    print("開始運行自動化測試")
    print("="*60)
    
    try:
        # 一、基礎功能測試
        test_service_running()
        
        # 二、員工端功能測試
        test_employee_login()
        test_check_session()
        test_today_orders()
        test_create_order()
        test_cancel_order()
        test_weekly_orders()
        test_history_orders()
        test_employee_logout()
        
        # 三、管理員端功能測試
        test_admin_login()
        test_departments()
        test_employees()
        test_windows()
        test_admin_orders()
        test_admin_stats()
        test_admin_logout()
        
        # 四、錯誤處理測試
        test_error_handling()
        
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    # 打印測試結果
    print("\n" + "="*60)
    print("測試結果總結")
    print("="*60)
    print(f"總測試數: {test_results['total']}")
    print(f"通過: {test_results['passed']}")
    print(f"失敗: {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print(f"\n失敗的測試:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n通過率: {success_rate:.1f}%")
    print("="*60)


if __name__ == "__main__":
    # 檢查服務是否運行
    try:
        response = requests.get("http://localhost:5000/", timeout=2)
        print("服務運行正常，開始測試...")
    except:
        print("錯誤: 無法連接到 http://localhost:5000")
        print("請確認 Flask 應用正在運行 (python app.py)")
        exit(1)
    
    run_all_tests()

