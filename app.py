# -*- coding: utf-8 -*-
"""
Flask Web API 介面
提供RESTful API給前端使用
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from FoodOrder import FoodOrderSystem, MealType, DietType, RicePortion
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用於session管理
CORS(app)  # 允許跨域請求

# 初始化系統
system = FoodOrderSystem()


# ========== 輔助函數 ==========

def get_meal_type_name(meal_type: str) -> str:
    """獲取餐別中文名稱"""
    return "午餐" if meal_type == MealType.LUNCH.value else "晚餐"


def get_diet_type_name(diet_type: str) -> str:
    """獲取葷素中文名稱"""
    return "葷食" if diet_type == DietType.MEAT.value else "素食"


def get_rice_portion_name(rice_portion: str) -> str:
    """獲取飯量中文名稱"""
    return "全飯" if rice_portion == RicePortion.FULL.value else "半飯"


# ========== 員工API ==========

@app.route('/api/employee/login', methods=['POST'])
def employee_login():
    """員工登入"""
    data = request.json
    emp_id = data.get('emp_id', '').strip()
    password = data.get('password', '').strip()
    
    success, employee = system.verify_employee(emp_id, password)
    
    if success:
        session['emp_id'] = emp_id
        session['emp_name'] = employee['EmpName']
        session['is_admin'] = False
        return jsonify({
            'success': True,
            'message': '登入成功',
            'employee': {
                'EmpID': employee['EmpID'],
                'EmpName': employee['EmpName'],
                'DeptCode': employee['DeptCode']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '員工編號或密碼錯誤'
        }), 401


@app.route('/api/employee/logout', methods=['POST'])
def employee_logout():
    """員工登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})


@app.route('/api/employee/today-orders', methods=['GET'])
def get_today_orders():
    """獲取今日訂單"""
    emp_id = session.get('emp_id')
    if not emp_id:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    orders = system.get_today_orders(emp_id)
    today = system.format_date(datetime.now())
    
    result = {
        'date': today,
        'lunch': None,
        'dinner': None,
        'lunch_cutoff': system.check_cutoff(MealType.LUNCH.value),
        'dinner_cutoff': system.check_cutoff(MealType.DINNER.value)
    }
    
    if orders[MealType.LUNCH.value] and orders[MealType.LUNCH.value].get('IsOrdered'):
        order = orders[MealType.LUNCH.value]
        result['lunch'] = {
            'DietType': order['DietType'],
            'RicePortion': order['RicePortion'],
            'OrderTime': order.get('OrderTime', ''),
            'AdminModified': order.get('AdminModified', False)
        }
    
    if orders[MealType.DINNER.value] and orders[MealType.DINNER.value].get('IsOrdered'):
        order = orders[MealType.DINNER.value]
        result['dinner'] = {
            'DietType': order['DietType'],
            'RicePortion': order['RicePortion'],
            'OrderTime': order.get('OrderTime', ''),
            'AdminModified': order.get('AdminModified', False)
        }
    
    return jsonify({'success': True, 'data': result})


@app.route('/api/employee/order', methods=['POST'])
def create_order():
    """創建訂單"""
    emp_id = session.get('emp_id')
    if not emp_id:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    data = request.json
    meal_type = data.get('meal_type')
    diet_type = data.get('diet_type')
    rice_portion = data.get('rice_portion')
    date_str = data.get('date')  # 可選，用於一週訂餐
    
    if not all([meal_type, diet_type, rice_portion]):
        return jsonify({'success': False, 'message': '參數不完整'}), 400
    
    success, message = system.create_order(emp_id, meal_type, diet_type, rice_portion, date_str)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/employee/cancel-order', methods=['POST'])
def cancel_order():
    """取消訂單"""
    emp_id = session.get('emp_id')
    if not emp_id:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    data = request.json
    meal_type = data.get('meal_type')
    date_str = data.get('date')
    
    if not meal_type:
        return jsonify({'success': False, 'message': '參數不完整'}), 400
    
    success, message = system.cancel_order(emp_id, meal_type, date_str)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/employee/weekly-orders', methods=['GET'])
def get_weekly_orders():
    """獲取一週訂單"""
    emp_id = session.get('emp_id')
    if not emp_id:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    week_type = request.args.get('week_type', 'current')  # current, next, month
    
    if week_type == 'month':
        # 當月全部週別
        today = datetime.now()
        year = today.year
        month = today.month
        start_date = datetime(year, month, 1)
        
        # 獲取當月最後一天
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        date_from = system.format_date(start_date)
        date_to = system.format_date(end_date)
        
        orders = system.get_orders_by_date_range(date_from, date_to, emp_id=emp_id)
        
        # 整理為按日期分組的格式
        orders_by_date = {}
        for order in orders:
            date_key = order['Date']
            meal_type = order['MealType']
            if date_key not in orders_by_date:
                orders_by_date[date_key] = {'LUNCH': None, 'DINNER': None}
            orders_by_date[date_key][meal_type] = order
        
        return jsonify({'success': True, 'data': orders_by_date})
    else:
        orders = system.get_weekly_orders(emp_id, week_type)
        orders_by_date = {}
        for order in orders:
            date_key = order['Date']
            meal_type = order['MealType']
            if date_key not in orders_by_date:
                orders_by_date[date_key] = {'LUNCH': None, 'DINNER': None}
            orders_by_date[date_key][meal_type] = order
        
        return jsonify({'success': True, 'data': orders_by_date})


@app.route('/api/employee/weekly-orders', methods=['POST'])
def save_weekly_orders():
    """批量保存一週訂單"""
    emp_id = session.get('emp_id')
    if not emp_id:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    data = request.json
    orders_list = data.get('orders', [])  # [{date, meal_type, diet_type, rice_portion}, ...]
    
    success_count = 0
    error_count = 0
    errors = []
    
    for order_data in orders_list:
        date_str = order_data.get('date')
        meal_type = order_data.get('meal_type')
        diet_type = order_data.get('diet_type')
        rice_portion = order_data.get('rice_portion')
        
        # 如果diet_type和rice_portion為空，表示取消訂單
        if not diet_type or not rice_portion:
            success, message = system.cancel_order(emp_id, meal_type, date_str)
        else:
            success, message = system.create_order(emp_id, meal_type, diet_type, rice_portion, date_str)
        
        if success:
            success_count += 1
        else:
            error_count += 1
            errors.append(f"{date_str} {meal_type}: {message}")
    
    return jsonify({
        'success': True,
        'message': f'共處理 {success_count + error_count} 筆，成功 {success_count} 筆，失敗 {error_count} 筆',
        'success_count': success_count,
        'error_count': error_count,
        'errors': errors
    })


@app.route('/api/employee/history', methods=['GET'])
def get_history_orders():
    """獲取歷史訂單"""
    emp_id = session.get('emp_id')
    if not emp_id:
        return jsonify({'success': False, 'message': '請先登入'}), 401
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not date_from or not date_to:
        return jsonify({'success': False, 'message': '請提供日期區間'}), 400
    
    try:
        orders = system.get_orders_by_date_range(date_from, date_to, emp_id=emp_id)
        return jsonify({'success': True, 'data': orders, 'count': len(orders)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ========== 管理員API ==========

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理員登入"""
    data = request.json
    account = data.get('account', '').strip()
    password = data.get('password', '').strip()
    
    if system.verify_admin(account, password):
        session['is_admin'] = True
        session['admin_account'] = account
        return jsonify({'success': True, 'message': '管理員登入成功'})
    else:
        return jsonify({'success': False, 'message': '帳號或密碼錯誤'}), 401


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """管理員登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})


@app.route('/api/admin/departments', methods=['GET'])
def get_departments():
    """獲取所有部門"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    depts = system.get_departments()
    return jsonify({'success': True, 'data': depts})


@app.route('/api/admin/departments', methods=['POST'])
def save_department():
    """新增或修改部門"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    data = request.json
    oid = data.get('OID')
    dept_code = data.get('DeptCode', '').strip()
    dept_name = data.get('DeptName', '').strip()
    
    success, message = system.save_department(oid, dept_code, dept_name)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/admin/departments/<int:oid>', methods=['DELETE'])
def delete_department(oid):
    """刪除部門"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    success, message = system.delete_department(oid)
    return jsonify({'success': success, 'message': message})


@app.route('/api/admin/employees', methods=['GET'])
def get_employees():
    """獲取所有員工"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    employees = system.get_employees()
    # 隱藏密碼，只顯示長度
    for emp in employees:
        if 'Password' in emp:
            emp['PasswordLength'] = len(emp['Password'])
            del emp['Password']
    
    return jsonify({'success': True, 'data': employees})


@app.route('/api/admin/employees', methods=['POST'])
def save_employee():
    """新增或修改員工"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    data = request.json
    oid = data.get('OID')
    emp_id = data.get('EmpID', '').strip()
    emp_name = data.get('EmpName', '').strip()
    password = data.get('Password', '').strip()
    dept_code = data.get('DeptCode', '').strip()
    
    success, message = system.save_employee(oid, emp_id, emp_name, password, dept_code)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/admin/employees/<int:oid>', methods=['DELETE'])
def delete_employee(oid):
    """刪除員工"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    success, message = system.delete_employee(oid)
    return jsonify({'success': success, 'message': message})


@app.route('/api/admin/windows', methods=['GET'])
def get_windows():
    """獲取所有窗口"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    windows = system.get_windows()
    return jsonify({'success': True, 'data': windows})


@app.route('/api/admin/windows', methods=['POST'])
def save_window():
    """新增或修改窗口"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    data = request.json
    oid = data.get('OID')
    emp_id = data.get('EmpID', '').strip()
    responsible_dept_codes = data.get('ResponsibleDeptCodes', [])
    
    success, message = system.save_window(oid, emp_id, responsible_dept_codes)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/admin/windows/<int:oid>', methods=['DELETE'])
def delete_window(oid):
    """刪除窗口"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    success, message = system.delete_window(oid)
    return jsonify({'success': success, 'message': message})


@app.route('/api/admin/orders', methods=['GET'])
def admin_get_orders():
    """管理員查詢訂單"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    emp_id = request.args.get('emp_id')
    dept_code = request.args.get('dept_code')
    
    if not date_from or not date_to:
        return jsonify({'success': False, 'message': '請提供日期區間'}), 400
    
    try:
        orders = system.get_orders_by_date_range(date_from, date_to, emp_id=emp_id, dept_code=dept_code)
        return jsonify({'success': True, 'data': orders, 'count': len(orders)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/admin/orders', methods=['PUT'])
def admin_update_order():
    """管理員修改訂單"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    data = request.json
    date_str = data.get('date')
    emp_id = data.get('emp_id')
    meal_type = data.get('meal_type')
    diet_type = data.get('diet_type')
    rice_portion = data.get('rice_portion')
    is_cancelled = data.get('is_cancelled', False)
    
    if not all([date_str, emp_id, meal_type]):
        return jsonify({'success': False, 'message': '參數不完整'}), 400
    
    success, message = system.update_order(emp_id, meal_type, diet_type, rice_portion, date_str, is_cancelled)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/api/admin/stats/meal-quantity', methods=['GET'])
def get_meal_quantity_stats():
    """獲取餐點總數量統計"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not date_from or not date_to:
        return jsonify({'success': False, 'message': '請提供日期區間'}), 400
    
    try:
        stats = system.get_meal_quantity_stats(date_from, date_to)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/admin/stats/employee-orders', methods=['GET'])
def get_employee_order_stats():
    """獲取員工訂購數量統計"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': '需要管理員權限'}), 403
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not date_from or not date_to:
        return jsonify({'success': False, 'message': '請提供日期區間'}), 400
    
    try:
        stats = system.get_employee_order_stats(date_from, date_to)
        return jsonify({'success': True, 'data': list(stats.values())})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ========== 通用API ==========

@app.route('/api/check-session', methods=['GET'])
def check_session():
    """檢查session狀態"""
    if session.get('is_admin'):
        return jsonify({
            'success': True,
            'is_admin': True,
            'account': session.get('admin_account')
        })
    elif session.get('emp_id'):
        return jsonify({
            'success': True,
            'is_admin': False,
            'emp_id': session.get('emp_id'),
            'emp_name': session.get('emp_name')
        })
    else:
        return jsonify({'success': False, 'message': '未登入'})


if __name__ == '__main__':
    print("=" * 50)
    print("工廠訂便當系統 Web API")
    print("=" * 50)
    print("API服務啟動在 http://localhost:5000")
    print("API文檔請參考各端點說明")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

