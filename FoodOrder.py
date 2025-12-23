# -*- coding: utf-8 -*-
"""
工廠訂便當系統
包含員工訂購及管理員維護功能
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class MealType(Enum):
    """餐別類型"""
    LUNCH = "LUNCH"  # 午餐
    DINNER = "DINNER"  # 晚餐


class DietType(Enum):
    """葷素類型"""
    MEAT = "MEAT"  # 葷食
    VEG = "VEG"  # 素食


class RicePortion(Enum):
    """飯量類型"""
    FULL = "FULL"  # 全飯
    HALF = "HALF"  # 半飯


@dataclass
class Department:
    """部門主檔"""
    OID: int
    DeptCode: str
    DeptName: str


@dataclass
class Employee:
    """員工主檔"""
    OID: int
    EmpID: str
    EmpName: str
    Password: str
    DeptCode: str


@dataclass
class OrderWindow:
    """訂餐窗口主檔"""
    OID: int
    EmpID: str
    ResponsibleDeptCodes: List[str]


@dataclass
class MealOrder:
    """餐點訂單"""
    EmpID: str
    MealType: str
    DietType: str
    RicePortion: str
    IsOrdered: bool
    OrderTime: str
    AdminModified: bool = False


class FoodOrderSystem:
    """訂便當系統核心類"""
    
    # 截止時間設定
    LUNCH_CUTOFF_HOUR = 8
    LUNCH_CUTOFF_MINUTE = 30
    DINNER_CUTOFF_HOUR = 16
    DINNER_CUTOFF_MINUTE = 0
    
    # 管理員帳號密碼
    ADMIN_ACCOUNT = "admin"
    ADMIN_PASSWORD = "1234"
    
    def __init__(self, data_dir: str = "data"):
        """初始化系統"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 數據文件路徑
        self.dept_file = os.path.join(data_dir, "departments.json")
        self.employee_file = os.path.join(data_dir, "employees.json")
        self.window_file = os.path.join(data_dir, "windows.json")
        self.orders_file = os.path.join(data_dir, "orders.json")
        
        # 初始化數據
        self._initialize_data()
    
    def _initialize_data(self):
        """初始化預設數據"""
        # 初始化部門
        if not os.path.exists(self.dept_file):
            default_depts = [
                {"OID": 1, "DeptCode": "A10", "DeptName": "生產部"},
                {"OID": 2, "DeptCode": "B20", "DeptName": "倉儲部"},
                {"OID": 3, "DeptCode": "C30", "DeptName": "行政部"}
            ]
            self._save_json(self.dept_file, default_depts)
        
        # 初始化員工
        if not os.path.exists(self.employee_file):
            default_employees = [
                {"OID": 101, "EmpID": "93800", "EmpName": "林淑鈺", "Password": "1234", "DeptCode": "A10"},
                {"OID": 102, "EmpID": "28109", "EmpName": "詹金璋", "Password": "1234", "DeptCode": "B20"},
                {"OID": 103, "EmpID": "2400305", "EmpName": "王瀚章", "Password": "1234", "DeptCode": "C30"}
            ]
            self._save_json(self.employee_file, default_employees)
        
        # 初始化窗口
        if not os.path.exists(self.window_file):
            default_windows = [
                {"OID": 1, "EmpID": "28109", "ResponsibleDeptCodes": ["A10", "C30"]}
            ]
            self._save_json(self.window_file, default_windows)
        
        # 初始化訂單（空字典）
        if not os.path.exists(self.orders_file):
            self._save_json(self.orders_file, {})
    
    def _load_json(self, filepath: str) -> dict:
        """載入JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'orders' in filepath else []
    
    def _save_json(self, filepath: str, data):
        """保存JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== 日期時間輔助函數 ==========
    
    @staticmethod
    def format_date(date: datetime) -> str:
        """格式化日期為 YYYY-MM-DD"""
        return date.strftime("%Y-%m-%d")
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """解析日期字符串"""
        return datetime.strptime(date_str, "%Y-%m-%d")
    
    def check_cutoff(self, meal_type: str, date_str: Optional[str] = None) -> bool:
        """檢查訂餐是否已截止"""
        today = datetime.now()
        if date_str:
            target_date = self.parse_date(date_str)
            # 如果不是今天，不檢查截止時間（過去日期視為已截止，未來日期未截止）
            if target_date.date() != today.date():
                return target_date.date() < today.date()
        
        now = datetime.now()
        
        if meal_type == MealType.LUNCH.value:
            cutoff_time = now.replace(hour=self.LUNCH_CUTOFF_HOUR, minute=self.LUNCH_CUTOFF_MINUTE, second=0, microsecond=0)
            return now > cutoff_time
        elif meal_type == MealType.DINNER.value:
            cutoff_time = now.replace(hour=self.DINNER_CUTOFF_HOUR, minute=self.DINNER_CUTOFF_MINUTE, second=0, microsecond=0)
            return now > cutoff_time
        
        return False
    
    # ========== 部門主檔管理 ==========
    
    def get_departments(self) -> List[Dict]:
        """獲取所有部門"""
        return self._load_json(self.dept_file)
    
    def get_department(self, dept_code: str) -> Optional[Dict]:
        """根據部門代號獲取部門"""
        depts = self.get_departments()
        for dept in depts:
            if dept["DeptCode"] == dept_code:
                return dept
        return None
    
    def save_department(self, oid: Optional[int], dept_code: str, dept_name: str) -> Tuple[bool, str]:
        """新增或修改部門"""
        depts = self.get_departments()
        dept_code = dept_code.strip().upper()
        dept_name = dept_name.strip()
        
        if not dept_code or not dept_name:
            return False, "部門代號和部門名稱不能為空！"
        
        if oid:
            # 修改現有部門
            for dept in depts:
                if dept["OID"] == oid:
                    # 檢查代號是否與其他部門衝突
                    if any(d["DeptCode"] == dept_code and d["OID"] != oid for d in depts):
                        return False, "部門代號已存在！"
                    dept["DeptCode"] = dept_code
                    dept["DeptName"] = dept_name
                    self._save_json(self.dept_file, depts)
                    return True, "部門資料修改成功！"
            return False, "找不到指定的部門！"
        else:
            # 新增部門
            if any(d["DeptCode"] == dept_code for d in depts):
                return False, "部門代號已存在！"
            new_oid = max([d["OID"] for d in depts], default=0) + 1
            depts.append({"OID": new_oid, "DeptCode": dept_code, "DeptName": dept_name})
            self._save_json(self.dept_file, depts)
            return True, "部門資料新增成功！"
    
    def delete_department(self, oid: int) -> Tuple[bool, str]:
        """刪除部門"""
        depts = self.get_departments()
        depts = [d for d in depts if d["OID"] != oid]
        self._save_json(self.dept_file, depts)
        return True, "部門資料刪除成功！"
    
    # ========== 員工主檔管理 ==========
    
    def get_employees(self) -> List[Dict]:
        """獲取所有員工"""
        return self._load_json(self.employee_file)
    
    def get_employee(self, emp_id: str) -> Optional[Dict]:
        """根據員工編號獲取員工"""
        employees = self.get_employees()
        for emp in employees:
            if emp["EmpID"] == emp_id:
                return emp
        return None
    
    def verify_employee(self, emp_id: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """驗證員工登入"""
        emp = self.get_employee(emp_id.upper().strip())
        if not emp:
            return False, None
        if emp["Password"] != password:
            return False, None
        return True, emp
    
    def save_employee(self, oid: Optional[int], emp_id: str, emp_name: str, password: str, dept_code: str) -> Tuple[bool, str]:
        """新增或修改員工"""
        employees = self.get_employees()
        depts = self.get_departments()
        emp_id = emp_id.strip().upper()
        emp_name = emp_name.strip()
        dept_code = dept_code.strip().upper()
        
        if not emp_id or not emp_name or not password or not dept_code:
            return False, "員工編號、姓名、密碼和部門都不能為空！"
        
        # 檢查部門是否存在
        if not self.get_department(dept_code):
            return False, "指定的部門不存在！"
        
        if oid:
            # 修改現有員工
            for emp in employees:
                if emp["OID"] == oid:
                    # 檢查員工編號是否與其他員工衝突
                    if any(e["EmpID"] == emp_id and e["OID"] != oid for e in employees):
                        return False, "員工編號已存在！"
                    emp["EmpID"] = emp_id
                    emp["EmpName"] = emp_name
                    emp["Password"] = password
                    emp["DeptCode"] = dept_code
                    self._save_json(self.employee_file, employees)
                    return True, "員工資料修改成功！"
            return False, "找不到指定的員工！"
        else:
            # 新增員工
            if any(e["EmpID"] == emp_id for e in employees):
                return False, "員工編號已存在！"
            new_oid = max([e["OID"] for e in employees], default=100) + 1
            employees.append({
                "OID": new_oid,
                "EmpID": emp_id,
                "EmpName": emp_name,
                "Password": password,
                "DeptCode": dept_code
            })
            self._save_json(self.employee_file, employees)
            return True, "員工資料新增成功！"
    
    def delete_employee(self, oid: int) -> Tuple[bool, str]:
        """刪除員工"""
        employees = self.get_employees()
        employees = [e for e in employees if e["OID"] != oid]
        self._save_json(self.employee_file, employees)
        return True, "員工資料刪除成功！"
    
    # ========== 窗口主檔管理 ==========
    
    def get_windows(self) -> List[Dict]:
        """獲取所有窗口"""
        return self._load_json(self.window_file)
    
    def save_window(self, oid: Optional[int], emp_id: str, responsible_dept_codes: List[str]) -> Tuple[bool, str]:
        """新增或修改窗口"""
        windows = self.get_windows()
        emp_id = emp_id.strip().upper()
        
        if not emp_id:
            return False, "請選擇一個窗口員工！"
        
        if not responsible_dept_codes:
            return False, "請至少選擇一個負責單位！"
        
        # 檢查員工是否存在
        if not self.get_employee(emp_id):
            return False, "指定的員工不存在！"
        
        if oid:
            # 修改現有窗口
            for win in windows:
                if win["OID"] == oid:
                    win["EmpID"] = emp_id
                    win["ResponsibleDeptCodes"] = responsible_dept_codes
                    self._save_json(self.window_file, windows)
                    return True, "訂餐窗口資料修改成功！"
            return False, "找不到指定的窗口！"
        else:
            # 新增窗口
            if any(w["EmpID"] == emp_id for w in windows):
                return False, "該員工已經是訂餐窗口！請使用編輯功能修改。"
            new_oid = max([w["OID"] for w in windows], default=0) + 1
            windows.append({
                "OID": new_oid,
                "EmpID": emp_id,
                "ResponsibleDeptCodes": responsible_dept_codes
            })
            self._save_json(self.window_file, windows)
            return True, "訂餐窗口資料新增成功！"
    
    def delete_window(self, oid: int) -> Tuple[bool, str]:
        """刪除窗口"""
        windows = self.get_windows()
        windows = [w for w in windows if w["OID"] != oid]
        self._save_json(self.window_file, windows)
        return True, "訂餐窗口資料刪除成功！"
    
    # ========== 訂單管理 ==========
    
    def _get_order_key(self, date_str: str, emp_id: str, meal_type: str) -> str:
        """生成訂單鍵值"""
        return f"{date_str}_{emp_id}_{meal_type}"
    
    def get_orders(self) -> Dict:
        """獲取所有訂單"""
        return self._load_json(self.orders_file)
    
    def get_order(self, date_str: str, emp_id: str, meal_type: str) -> Optional[Dict]:
        """獲取特定訂單"""
        orders = self.get_orders()
        key = self._get_order_key(date_str, emp_id, meal_type)
        return orders.get(key)
    
    def get_today_orders(self, emp_id: str) -> Dict[str, Optional[Dict]]:
        """獲取員工今日訂單"""
        today = self.format_date(datetime.now())
        return {
            MealType.LUNCH.value: self.get_order(today, emp_id, MealType.LUNCH.value),
            MealType.DINNER.value: self.get_order(today, emp_id, MealType.DINNER.value)
        }
    
    def create_order(self, emp_id: str, meal_type: str, diet_type: str, rice_portion: str, 
                    date_str: Optional[str] = None, is_admin: bool = False) -> Tuple[bool, str]:
        """創建訂單"""
        if not date_str:
            date_str = self.format_date(datetime.now())
        
        # 檢查截止時間（管理員不受限制）
        if not is_admin and self.check_cutoff(meal_type, date_str):
            meal_name = "午餐" if meal_type == MealType.LUNCH.value else "晚餐"
            return False, f"{meal_name}訂餐時間已截止！"
        
        orders = self.get_orders()
        key = self._get_order_key(date_str, emp_id, meal_type)
        
        # 檢查員工是否存在
        if not self.get_employee(emp_id):
            return False, "員工不存在！"
        
        order_time = datetime.now().strftime("%H:%M:%S")
        orders[key] = {
            "EmpID": emp_id,
            "MealType": meal_type,
            "DietType": diet_type,
            "RicePortion": rice_portion,
            "IsOrdered": True,
            "OrderTime": order_time,
            "AdminModified": is_admin
        }
        
        self._save_json(self.orders_file, orders)
        meal_name = "午餐" if meal_type == MealType.LUNCH.value else "晚餐"
        return True, f"{meal_name}訂購成功！"
    
    def cancel_order(self, emp_id: str, meal_type: str, date_str: Optional[str] = None, 
                    is_admin: bool = False) -> Tuple[bool, str]:
        """取消訂單"""
        if not date_str:
            date_str = self.format_date(datetime.now())
        
        # 檢查截止時間（管理員不受限制）
        if not is_admin and self.check_cutoff(meal_type, date_str):
            meal_name = "午餐" if meal_type == MealType.LUNCH.value else "晚餐"
            return False, f"{meal_name}訂餐時間已截止，無法取消！"
        
        orders = self.get_orders()
        key = self._get_order_key(date_str, emp_id, meal_type)
        
        if key in orders:
            del orders[key]
            self._save_json(self.orders_file, orders)
            meal_name = "午餐" if meal_type == MealType.LUNCH.value else "晚餐"
            return True, f"{meal_name}訂單已取消！"
        
        return False, "找不到該訂單！"
    
    def update_order(self, emp_id: str, meal_type: str, diet_type: str, rice_portion: str,
                    date_str: str, is_cancelled: bool = False) -> Tuple[bool, str]:
        """更新訂單（管理員功能）"""
        orders = self.get_orders()
        key = self._get_order_key(date_str, emp_id, meal_type)
        
        if is_cancelled:
            if key in orders:
                del orders[key]
                self._save_json(self.orders_file, orders)
                return True, "訂單已取消！"
            return False, "找不到該訂單！"
        else:
            if key not in orders:
                return False, "找不到該訂單！"
            
            order = orders[key]
            order["DietType"] = diet_type
            order["RicePortion"] = rice_portion
            order["AdminModified"] = True
            self._save_json(self.orders_file, orders)
            return True, "訂單修改成功！"
    
    def get_orders_by_date_range(self, date_from: str, date_to: str, 
                                 emp_id: Optional[str] = None,
                                 dept_code: Optional[str] = None) -> List[Dict]:
        """根據日期區間獲取訂單"""
        date_from_dt = self.parse_date(date_from)
        date_to_dt = self.parse_date(date_to)
        orders = self.get_orders()
        employees = self.get_employees()
        employee_map = {e["EmpID"]: e for e in employees}
        
        result = []
        current_date = date_from_dt
        
        while current_date <= date_to_dt:
            date_str = self.format_date(current_date)
            
            for key, order in orders.items():
                if not order.get("IsOrdered", False):
                    continue
                
                parts = key.split("_")
                if len(parts) != 3:
                    continue
                
                order_date, order_emp_id, meal_type = parts
                
                if order_date != date_str:
                    continue
                
                # 篩選條件
                if emp_id and order_emp_id != emp_id:
                    continue
                
                if dept_code:
                    emp = employee_map.get(order_emp_id)
                    if not emp or emp.get("DeptCode") != dept_code:
                        continue
                
                order_info = order.copy()
                order_info["Date"] = date_str
                result.append(order_info)
            
            current_date += timedelta(days=1)
        
        return result
    
    def get_weekly_orders(self, emp_id: str, week_type: str = "current") -> List[Dict]:
        """獲取一週訂單"""
        today = datetime.now()
        
        if week_type == "current":
            # 本週
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
        elif week_type == "next":
            # 下週
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday) + timedelta(days=7)
        else:
            return []
        
        result = []
        for i in range(5):  # 週一到週五
            date = start_date + timedelta(days=i)
            date_str = self.format_date(date)
            
            for meal_type in [MealType.LUNCH.value, MealType.DINNER.value]:
                order = self.get_order(date_str, emp_id, meal_type)
                if order:
                    order_info = order.copy()
                    order_info["Date"] = date_str
                    result.append(order_info)
        
        return result
    
    # ========== 統計與匯出 ==========
    
    def get_meal_quantity_stats(self, date_from: str, date_to: str) -> Dict:
        """獲取餐點總數量統計"""
        orders = self.get_orders_by_date_range(date_from, date_to)
        counts = {}
        
        for order in orders:
            key = f"{order['Date']}_{order['MealType']}_{order['DietType']}_{order['RicePortion']}"
            counts[key] = counts.get(key, 0) + 1
        
        return counts
    
    def get_employee_order_stats(self, date_from: str, date_to: str) -> Dict:
        """獲取員工訂購數量統計"""
        orders = self.get_orders_by_date_range(date_from, date_to)
        employees = self.get_employees()
        stats = {}
        
        # 初始化所有員工
        for emp in employees:
            stats[emp["EmpID"]] = {
                "EmpID": emp["EmpID"],
                "EmpName": emp["EmpName"],
                "LunchCount": 0,
                "DinnerCount": 0,
                "TotalCount": 0
            }
        
        # 統計訂單
        for order in orders:
            emp_id = order["EmpID"]
            if emp_id in stats:
                stats[emp_id]["TotalCount"] += 1
                if order["MealType"] == MealType.LUNCH.value:
                    stats[emp_id]["LunchCount"] += 1
                elif order["MealType"] == MealType.DINNER.value:
                    stats[emp_id]["DinnerCount"] += 1
        
        return stats
    
    # ========== 管理員驗證 ==========
    
    def verify_admin(self, account: str, password: str) -> bool:
        """驗證管理員登入"""
        return account == self.ADMIN_ACCOUNT and password == self.ADMIN_PASSWORD


# ========== 命令行介面（測試用） ==========

def main():
    """主函數 - 簡單的命令行測試介面"""
    system = FoodOrderSystem()
    
    print("=" * 50)
    print("工廠訂便當系統")
    print("=" * 50)
    
    while True:
        print("\n請選擇功能：")
        print("1. 員工登入")
        print("2. 管理員登入")
        print("3. 退出")
        
        choice = input("請輸入選項 (1-3): ").strip()
        
        if choice == "1":
            emp_id = input("員工編號: ").strip()
            password = input("密碼: ").strip()
            success, employee = system.verify_employee(emp_id, password)
            
            if success:
                print(f"\n歡迎 {employee['EmpName']}！")
                emp_menu(system, emp_id)
            else:
                print("登入失敗！")
        
        elif choice == "2":
            account = input("管理員帳號: ").strip()
            password = input("密碼: ").strip()
            
            if system.verify_admin(account, password):
                print("\n管理員登入成功！")
                admin_menu(system)
            else:
                print("登入失敗！")
        
        elif choice == "3":
            print("感謝使用！")
            break
        
        else:
            print("無效選項！")


def emp_menu(system: FoodOrderSystem, emp_id: str):
    """員工功能選單"""
    while True:
        print("\n--- 員工功能選單 ---")
        print("1. 查看今日訂單")
        print("2. 訂購午餐")
        print("3. 訂購晚餐")
        print("4. 取消午餐")
        print("5. 取消晚餐")
        print("6. 查詢歷史訂單")
        print("7. 返回主選單")
        
        choice = input("請輸入選項 (1-7): ").strip()
        
        if choice == "1":
            orders = system.get_today_orders(emp_id)
            today = system.format_date(datetime.now())
            print(f"\n今日 ({today}) 訂單：")
            
            for meal_type, order in orders.items():
                meal_name = "午餐" if meal_type == MealType.LUNCH.value else "晚餐"
                if order and order.get("IsOrdered"):
                    diet = "葷食" if order["DietType"] == DietType.MEAT.value else "素食"
                    rice = "全飯" if order["RicePortion"] == RicePortion.FULL.value else "半飯"
                    print(f"  {meal_name}: {diet} / {rice} (訂購時間: {order.get('OrderTime', 'N/A')})")
                else:
                    print(f"  {meal_name}: 尚未訂購")
        
        elif choice == "2":
            print("\n請選擇：")
            print("1. 葷食")
            print("2. 素食")
            diet_choice = input("選項 (1-2): ").strip()
            diet_type = DietType.MEAT.value if diet_choice == "1" else DietType.VEG.value
            
            print("\n請選擇飯量：")
            print("1. 全飯")
            print("2. 半飯")
            rice_choice = input("選項 (1-2): ").strip()
            rice_portion = RicePortion.FULL.value if rice_choice == "1" else RicePortion.HALF.value
            
            success, msg = system.create_order(emp_id, MealType.LUNCH.value, diet_type, rice_portion)
            print(msg)
        
        elif choice == "3":
            print("\n請選擇：")
            print("1. 葷食")
            print("2. 素食")
            diet_choice = input("選項 (1-2): ").strip()
            diet_type = DietType.MEAT.value if diet_choice == "1" else DietType.VEG.value
            
            print("\n請選擇飯量：")
            print("1. 全飯")
            print("2. 半飯")
            rice_choice = input("選項 (1-2): ").strip()
            rice_portion = RicePortion.FULL.value if rice_choice == "1" else RicePortion.HALF.value
            
            success, msg = system.create_order(emp_id, MealType.DINNER.value, diet_type, rice_portion)
            print(msg)
        
        elif choice == "4":
            success, msg = system.cancel_order(emp_id, MealType.LUNCH.value)
            print(msg)
        
        elif choice == "5":
            success, msg = system.cancel_order(emp_id, MealType.DINNER.value)
            print(msg)
        
        elif choice == "6":
            date_from = input("起始日期 (YYYY-MM-DD): ").strip()
            date_to = input("結束日期 (YYYY-MM-DD): ").strip()
            
            try:
                orders = system.get_orders_by_date_range(date_from, date_to, emp_id=emp_id)
                print(f"\n查詢結果 (共 {len(orders)} 筆)：")
                for order in orders:
                    meal_name = "午餐" if order["MealType"] == MealType.LUNCH.value else "晚餐"
                    diet = "葷食" if order["DietType"] == DietType.MEAT.value else "素食"
                    rice = "全飯" if order["RicePortion"] == RicePortion.FULL.value else "半飯"
                    print(f"  {order['Date']} {meal_name}: {diet} / {rice}")
            except Exception as e:
                print(f"查詢失敗: {e}")
        
        elif choice == "7":
            break
        
        else:
            print("無效選項！")


def admin_menu(system: FoodOrderSystem):
    """管理員功能選單"""
    while True:
        print("\n--- 管理員功能選單 ---")
        print("1. 部門主檔維護")
        print("2. 員工主檔維護")
        print("3. 窗口主檔維護")
        print("4. 查詢訂單")
        print("5. 返回主選單")
        
        choice = input("請輸入選項 (1-5): ").strip()
        
        if choice == "1":
            print("\n部門列表：")
            depts = system.get_departments()
            for dept in depts:
                print(f"  OID: {dept['OID']}, 代號: {dept['DeptCode']}, 名稱: {dept['DeptName']}")
        
        elif choice == "2":
            print("\n員工列表：")
            employees = system.get_employees()
            for emp in employees:
                print(f"  OID: {emp['OID']}, 編號: {emp['EmpID']}, 姓名: {emp['EmpName']}, 部門: {emp['DeptCode']}")
        
        elif choice == "3":
            print("\n窗口列表：")
            windows = system.get_windows()
            for win in windows:
                print(f"  OID: {win['OID']}, 員工: {win['EmpID']}, 負責部門: {', '.join(win['ResponsibleDeptCodes'])}")
        
        elif choice == "4":
            date_from = input("起始日期 (YYYY-MM-DD): ").strip()
            date_to = input("結束日期 (YYYY-MM-DD): ").strip()
            
            try:
                orders = system.get_orders_by_date_range(date_from, date_to)
                print(f"\n查詢結果 (共 {len(orders)} 筆)：")
                for order in orders:
                    meal_name = "午餐" if order["MealType"] == MealType.LUNCH.value else "晚餐"
                    diet = "葷食" if order["DietType"] == DietType.MEAT.value else "素食"
                    rice = "全飯" if order["RicePortion"] == RicePortion.FULL.value else "半飯"
                    print(f"  {order['Date']} {order['EmpID']} {meal_name}: {diet} / {rice}")
            except Exception as e:
                print(f"查詢失敗: {e}")
        
        elif choice == "5":
            break
        
        else:
            print("無效選項！")


if __name__ == "__main__":
    main()
