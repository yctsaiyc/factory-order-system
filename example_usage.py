# -*- coding: utf-8 -*-
"""
使用範例：演示如何使用 FoodOrderSystem
"""

from FoodOrder import FoodOrderSystem, MealType, DietType, RicePortion
from datetime import datetime, timedelta

def example_usage():
    """使用範例"""
    # 初始化系統
    system = FoodOrderSystem()
    
    print("=" * 50)
    print("工廠訂便當系統 - 使用範例")
    print("=" * 50)
    
    # 1. 員工登入
    print("\n1. 員工登入測試")
    success, employee = system.verify_employee("93800", "1234")
    if success:
        print(f"✓ 登入成功：{employee['EmpName']} ({employee['EmpID']})")
    else:
        print("✗ 登入失敗")
        return
    
    emp_id = employee['EmpID']
    
    # 2. 查看今日訂單
    print("\n2. 查看今日訂單")
    today_orders = system.get_today_orders(emp_id)
    today = system.format_date(datetime.now())
    print(f"今日 ({today}) 訂單：")
    for meal_type, order in today_orders.items():
        meal_name = "午餐" if meal_type == MealType.LUNCH.value else "晚餐"
        if order and order.get("IsOrdered"):
            diet = "葷食" if order["DietType"] == DietType.MEAT.value else "素食"
            rice = "全飯" if order["RicePortion"] == RicePortion.FULL.value else "半飯"
            print(f"  {meal_name}: {diet} / {rice}")
        else:
            print(f"  {meal_name}: 尚未訂購")
    
    # 3. 訂購午餐
    print("\n3. 訂購午餐（葷食/全飯）")
    success, message = system.create_order(
        emp_id, 
        MealType.LUNCH.value, 
        DietType.MEAT.value, 
        RicePortion.FULL.value
    )
    print(f"{'✓' if success else '✗'} {message}")
    
    # 4. 查詢歷史訂單
    print("\n4. 查詢本月訂單")
    today = datetime.now()
    date_from = system.format_date(datetime(today.year, today.month, 1))
    date_to = system.format_date(today)
    orders = system.get_orders_by_date_range(date_from, date_to, emp_id=emp_id)
    print(f"共找到 {len(orders)} 筆訂單")
    for order in orders[:5]:  # 只顯示前5筆
        meal_name = "午餐" if order["MealType"] == MealType.LUNCH.value else "晚餐"
        diet = "葷食" if order["DietType"] == DietType.MEAT.value else "素食"
        rice = "全飯" if order["RicePortion"] == RicePortion.FULL.value else "半飯"
        print(f"  {order['Date']} {meal_name}: {diet} / {rice}")
    
    # 5. 管理員功能範例
    print("\n5. 管理員功能範例")
    if system.verify_admin("admin", "1234"):
        print("✓ 管理員登入成功")
        
        # 獲取所有部門
        depts = system.get_departments()
        print(f"\n部門列表（共 {len(depts)} 個）：")
        for dept in depts:
            print(f"  {dept['DeptCode']} - {dept['DeptName']}")
        
        # 獲取所有員工
        employees = system.get_employees()
        print(f"\n員工列表（共 {len(employees)} 人）：")
        for emp in employees:
            print(f"  {emp['EmpID']} - {emp['EmpName']} ({emp['DeptCode']})")
    
    print("\n" + "=" * 50)
    print("範例執行完成！")
    print("=" * 50)


if __name__ == "__main__":
    example_usage()

