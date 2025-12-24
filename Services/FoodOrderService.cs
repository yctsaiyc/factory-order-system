using FoodOrderSystem.Models;
using Newtonsoft.Json;
using System.Linq;

namespace FoodOrderSystem.Services;

/// <summary>
/// 訂便當系統核心服務
/// </summary>
public class FoodOrderService
{
    private readonly string _dataDir;
    private readonly string _deptFile;
    private readonly string _employeeFile;
    private readonly string _windowFile;
    private readonly string _ordersFile;

    // 截止時間設定
    public const int LUNCH_CUTOFF_HOUR = 8;
    public const int LUNCH_CUTOFF_MINUTE = 30;
    public const int DINNER_CUTOFF_HOUR = 16;
    public const int DINNER_CUTOFF_MINUTE = 0;

    // 管理員帳號密碼
    public const string ADMIN_ACCOUNT = "admin";
    public const string ADMIN_PASSWORD = "1234";

    public FoodOrderService(IWebHostEnvironment env)
    {
        _dataDir = Path.Combine(env.ContentRootPath, "data");
        Directory.CreateDirectory(_dataDir);

        _deptFile = Path.Combine(_dataDir, "departments.json");
        _employeeFile = Path.Combine(_dataDir, "employees.json");
        _windowFile = Path.Combine(_dataDir, "windows.json");
        _ordersFile = Path.Combine(_dataDir, "orders.json");

        InitializeData();
    }

    private void InitializeData()
    {
        // 初始化部門
        if (!File.Exists(_deptFile))
        {
            var defaultDepts = new List<Department>
            {
                new() { OID = 1, DeptCode = "A10", DeptName = "生產部" },
                new() { OID = 2, DeptCode = "B20", DeptName = "倉儲部" },
                new() { OID = 3, DeptCode = "C30", DeptName = "行政部" }
            };
            SaveJson(_deptFile, defaultDepts);
        }

        // 初始化員工
        if (!File.Exists(_employeeFile))
        {
            var defaultEmployees = new List<Employee>
            {
                new() { OID = 101, EmpID = "93800", EmpName = "林淑鈺", Password = "1234", DeptCode = "A10" },
                new() { OID = 102, EmpID = "28109", EmpName = "詹金璋", Password = "1234", DeptCode = "B20" },
                new() { OID = 103, EmpID = "2400305", EmpName = "王瀚章", Password = "1234", DeptCode = "C30" }
            };
            SaveJson(_employeeFile, defaultEmployees);
        }

        // 初始化窗口
        if (!File.Exists(_windowFile))
        {
            var defaultWindows = new List<OrderWindow>
            {
                new() { OID = 1, EmpID = "28109", ResponsibleDeptCodes = new List<string> { "A10", "C30" } }
            };
            SaveJson(_windowFile, defaultWindows);
        }

        // 初始化訂單（空字典）
        if (!File.Exists(_ordersFile))
        {
            SaveJson(_ordersFile, new Dictionary<string, MealOrder>());
        }
    }

    private T LoadJson<T>(string filepath)
    {
        try
        {
            if (!File.Exists(filepath))
            {
                if (typeof(T).IsGenericType && typeof(T).GetGenericTypeDefinition() == typeof(Dictionary<,>))
                {
                    return (T)Activator.CreateInstance(typeof(T))!;
                }
                return Activator.CreateInstance<T>();
            }

            var json = File.ReadAllText(filepath, System.Text.Encoding.UTF8);
            return JsonConvert.DeserializeObject<T>(json) ?? Activator.CreateInstance<T>();
        }
        catch
        {
            if (typeof(T).IsGenericType && typeof(T).GetGenericTypeDefinition() == typeof(Dictionary<,>))
            {
                return (T)Activator.CreateInstance(typeof(T))!;
            }
            return Activator.CreateInstance<T>();
        }
    }

    private void SaveJson<T>(string filepath, T data)
    {
        var json = JsonConvert.SerializeObject(data, Formatting.Indented);
        File.WriteAllText(filepath, json, System.Text.Encoding.UTF8);
    }

    // ========== 日期時間輔助函數 ==========

    public static string FormatDate(DateTime date)
    {
        return date.ToString("yyyy-MM-dd");
    }

    public static DateTime ParseDate(string dateStr)
    {
        return DateTime.ParseExact(dateStr, "yyyy-MM-dd", null);
    }

    public bool CheckCutoff(string mealType, string? dateStr = null)
    {
        var today = DateTime.Now;
        if (!string.IsNullOrEmpty(dateStr))
        {
            var targetDate = ParseDate(dateStr);
            if (targetDate.Date != today.Date)
            {
                return targetDate.Date < today.Date;
            }
        }

        var now = DateTime.Now;

        if (mealType == MealType.LUNCH.ToString())
        {
            var cutoffTime = now.Date.AddHours(LUNCH_CUTOFF_HOUR).AddMinutes(LUNCH_CUTOFF_MINUTE);
            return now > cutoffTime;
        }
        else if (mealType == MealType.DINNER.ToString())
        {
            var cutoffTime = now.Date.AddHours(DINNER_CUTOFF_HOUR).AddMinutes(DINNER_CUTOFF_MINUTE);
            return now > cutoffTime;
        }

        return false;
    }

    // ========== 部門主檔管理 ==========

    public List<Department> GetDepartments()
    {
        return LoadJson<List<Department>>(_deptFile);
    }

    public Department? GetDepartment(string deptCode)
    {
        var depts = GetDepartments();
        return depts.FirstOrDefault(d => d.DeptCode == deptCode);
    }

    public (bool Success, string Message) SaveDepartment(int? oid, string deptCode, string deptName)
    {
        var depts = GetDepartments();
        deptCode = deptCode.Trim().ToUpper();
        deptName = deptName.Trim();

        if (string.IsNullOrEmpty(deptCode) || string.IsNullOrEmpty(deptName))
        {
            return (false, "部門代號和部門名稱不能為空！");
        }

        if (oid.HasValue)
        {
            var dept = depts.FirstOrDefault(d => d.OID == oid.Value);
            if (dept == null)
            {
                return (false, "找不到指定的部門！");
            }

            if (depts.Any(d => d.DeptCode == deptCode && d.OID != oid.Value))
            {
                return (false, "部門代號已存在！");
            }

            dept.DeptCode = deptCode;
            dept.DeptName = deptName;
            SaveJson(_deptFile, depts);
            return (true, "部門資料修改成功！");
        }
        else
        {
            if (depts.Any(d => d.DeptCode == deptCode))
            {
                return (false, "部門代號已存在！");
            }

            var newOid = depts.Count > 0 ? depts.Max(d => d.OID) + 1 : 1;
            depts.Add(new Department { OID = newOid, DeptCode = deptCode, DeptName = deptName });
            SaveJson(_deptFile, depts);
            return (true, "部門資料新增成功！");
        }
    }

    public (bool Success, string Message) DeleteDepartment(int oid)
    {
        var depts = GetDepartments();
        depts.RemoveAll(d => d.OID == oid);
        SaveJson(_deptFile, depts);
        return (true, "部門資料刪除成功！");
    }

    // ========== 員工主檔管理 ==========

    public List<Employee> GetEmployees()
    {
        return LoadJson<List<Employee>>(_employeeFile);
    }

    public Employee? GetEmployee(string empId)
    {
        var employees = GetEmployees();
        return employees.FirstOrDefault(e => e.EmpID == empId);
    }

    public (bool Success, Employee? Employee) VerifyEmployee(string empId, string password)
    {
        var emp = GetEmployee(empId.Trim().ToUpper());
        if (emp == null || emp.Password != password)
        {
            return (false, null);
        }
        return (true, emp);
    }

    public (bool Success, string Message) SaveEmployee(int? oid, string empId, string empName, string password, string deptCode)
    {
        var employees = GetEmployees();
        empId = empId.Trim().ToUpper();
        empName = empName.Trim();
        deptCode = deptCode.Trim().ToUpper();

        if (string.IsNullOrEmpty(empId) || string.IsNullOrEmpty(empName) || 
            string.IsNullOrEmpty(password) || string.IsNullOrEmpty(deptCode))
        {
            return (false, "員工編號、姓名、密碼和部門都不能為空！");
        }

        if (GetDepartment(deptCode) == null)
        {
            return (false, "指定的部門不存在！");
        }

        if (oid.HasValue)
        {
            var emp = employees.FirstOrDefault(e => e.OID == oid.Value);
            if (emp == null)
            {
                return (false, "找不到指定的員工！");
            }

            if (employees.Any(e => e.EmpID == empId && e.OID != oid.Value))
            {
                return (false, "員工編號已存在！");
            }

            emp.EmpID = empId;
            emp.EmpName = empName;
            emp.Password = password;
            emp.DeptCode = deptCode;
            SaveJson(_employeeFile, employees);
            return (true, "員工資料修改成功！");
        }
        else
        {
            if (employees.Any(e => e.EmpID == empId))
            {
                return (false, "員工編號已存在！");
            }

            var newOid = employees.Count > 0 ? employees.Max(e => e.OID) + 1 : 101;
            employees.Add(new Employee
            {
                OID = newOid,
                EmpID = empId,
                EmpName = empName,
                Password = password,
                DeptCode = deptCode
            });
            SaveJson(_employeeFile, employees);
            return (true, "員工資料新增成功！");
        }
    }

    public (bool Success, string Message) DeleteEmployee(int oid)
    {
        var employees = GetEmployees();
        employees.RemoveAll(e => e.OID == oid);
        SaveJson(_employeeFile, employees);
        return (true, "員工資料刪除成功！");
    }

    // ========== 窗口主檔管理 ==========

    public List<OrderWindow> GetWindows()
    {
        return LoadJson<List<OrderWindow>>(_windowFile);
    }

    public (bool Success, string Message) SaveWindow(int? oid, string empId, List<string> responsibleDeptCodes)
    {
        var windows = GetWindows();
        empId = empId.Trim().ToUpper();

        if (string.IsNullOrEmpty(empId))
        {
            return (false, "請選擇一個窗口員工！");
        }

        if (responsibleDeptCodes == null || responsibleDeptCodes.Count == 0)
        {
            return (false, "請至少選擇一個負責單位！");
        }

        if (GetEmployee(empId) == null)
        {
            return (false, "指定的員工不存在！");
        }

        if (oid.HasValue)
        {
            var win = windows.FirstOrDefault(w => w.OID == oid.Value);
            if (win == null)
            {
                return (false, "找不到指定的窗口！");
            }

            win.EmpID = empId;
            win.ResponsibleDeptCodes = responsibleDeptCodes;
            SaveJson(_windowFile, windows);
            return (true, "訂餐窗口資料修改成功！");
        }
        else
        {
            if (windows.Any(w => w.EmpID == empId))
            {
                return (false, "該員工已經是訂餐窗口！請使用編輯功能修改。");
            }

            var newOid = windows.Count > 0 ? windows.Max(w => w.OID) + 1 : 1;
            windows.Add(new OrderWindow
            {
                OID = newOid,
                EmpID = empId,
                ResponsibleDeptCodes = responsibleDeptCodes
            });
            SaveJson(_windowFile, windows);
            return (true, "訂餐窗口資料新增成功！");
        }
    }

    public (bool Success, string Message) DeleteWindow(int oid)
    {
        var windows = GetWindows();
        windows.RemoveAll(w => w.OID == oid);
        SaveJson(_windowFile, windows);
        return (true, "訂餐窗口資料刪除成功！");
    }

    // ========== 訂單管理 ==========

    private string GetOrderKey(string dateStr, string empId, string mealType)
    {
        return $"{dateStr}_{empId}_{mealType}";
    }

    private Dictionary<string, MealOrder> GetOrders()
    {
        return LoadJson<Dictionary<string, MealOrder>>(_ordersFile);
    }

    public MealOrder? GetOrder(string dateStr, string empId, string mealType)
    {
        var orders = GetOrders();
        var key = GetOrderKey(dateStr, empId, mealType);
        return orders.TryGetValue(key, out var order) ? order : null;
    }

    public Dictionary<string, MealOrder?> GetTodayOrders(string empId)
    {
        var today = FormatDate(DateTime.Now);
        return new Dictionary<string, MealOrder?>
        {
            { MealType.LUNCH.ToString(), GetOrder(today, empId, MealType.LUNCH.ToString()) },
            { MealType.DINNER.ToString(), GetOrder(today, empId, MealType.DINNER.ToString()) }
        };
    }

    public (bool Success, string Message) CreateOrder(string empId, string mealType, string dietType, 
        string ricePortion, string? dateStr = null, bool isAdmin = false)
    {
        dateStr ??= FormatDate(DateTime.Now);

        if (!isAdmin && CheckCutoff(mealType, dateStr))
        {
            var mealName = mealType == MealType.LUNCH.ToString() ? "午餐" : "晚餐";
            return (false, $"{mealName}訂餐時間已截止！");
        }

        var orders = GetOrders();
        var key = GetOrderKey(dateStr, empId, mealType);

        if (GetEmployee(empId) == null)
        {
            return (false, "員工不存在！");
        }

        var orderTime = DateTime.Now.ToString("HH:mm:ss");
        orders[key] = new MealOrder
        {
            EmpID = empId,
            MealType = mealType,
            DietType = dietType,
            RicePortion = ricePortion,
            IsOrdered = true,
            OrderTime = orderTime,
            AdminModified = isAdmin
        };

        SaveJson(_ordersFile, orders);
        var mealName2 = mealType == MealType.LUNCH.ToString() ? "午餐" : "晚餐";
        return (true, $"{mealName2}訂購成功！");
    }

    public (bool Success, string Message) CancelOrder(string empId, string mealType, string? dateStr = null, bool isAdmin = false)
    {
        dateStr ??= FormatDate(DateTime.Now);

        if (!isAdmin && CheckCutoff(mealType, dateStr))
        {
            var mealName = mealType == MealType.LUNCH.ToString() ? "午餐" : "晚餐";
            return (false, $"{mealName}訂餐時間已截止，無法取消！");
        }

        var orders = GetOrders();
        var key = GetOrderKey(dateStr, empId, mealType);

        if (orders.ContainsKey(key))
        {
            orders.Remove(key);
            SaveJson(_ordersFile, orders);
            var mealName = mealType == MealType.LUNCH.ToString() ? "午餐" : "晚餐";
            return (true, $"{mealName}訂單已取消！");
        }

        return (false, "找不到該訂單！");
    }

    public (bool Success, string Message) UpdateOrder(string empId, string mealType, string dietType,
        string ricePortion, string dateStr, bool isCancelled = false)
    {
        var orders = GetOrders();
        var key = GetOrderKey(dateStr, empId, mealType);

        if (isCancelled)
        {
            if (orders.ContainsKey(key))
            {
                orders.Remove(key);
                SaveJson(_ordersFile, orders);
                return (true, "訂單已取消！");
            }
            return (false, "找不到該訂單！");
        }
        else
        {
            if (!orders.ContainsKey(key))
            {
                return (false, "找不到該訂單！");
            }

            var order = orders[key];
            order.DietType = dietType;
            order.RicePortion = ricePortion;
            order.AdminModified = true;
            SaveJson(_ordersFile, orders);
            return (true, "訂單修改成功！");
        }
    }

    public List<OrderWithDate> GetOrdersByDateRange(string dateFrom, string dateTo, string? empId = null, string? deptCode = null)
    {
        var dateFromDt = ParseDate(dateFrom);
        var dateToDt = ParseDate(dateTo);
        var orders = GetOrders();
        var employees = GetEmployees();
        var employeeMap = employees.ToDictionary(e => e.EmpID);

        var result = new List<OrderWithDate>();

        foreach (var kvp in orders)
        {
            var order = kvp.Value;
            if (!order.IsOrdered)
                continue;

            var parts = kvp.Key.Split('_');
            if (parts.Length != 3)
                continue;

            var orderDate = parts[0];
            var orderEmpId = parts[1];
            var orderMealType = parts[2];

            // 檢查日期是否在範圍內
            var orderDateDt = ParseDate(orderDate);
            if (orderDateDt < dateFromDt || orderDateDt > dateToDt)
                continue;

            if (!string.IsNullOrEmpty(empId) && orderEmpId != empId)
                continue;

            if (!string.IsNullOrEmpty(deptCode))
            {
                if (!employeeMap.TryGetValue(orderEmpId, out var emp) || emp.DeptCode != deptCode)
                    continue;
            }

            var orderInfo = new OrderWithDate
            {
                Date = orderDate,
                EmpID = order.EmpID,
                MealType = order.MealType,
                DietType = order.DietType,
                RicePortion = order.RicePortion,
                IsOrdered = order.IsOrdered,
                OrderTime = order.OrderTime,
                AdminModified = order.AdminModified
            };
            result.Add(orderInfo);
        }

        return result.OrderBy(o => o.Date).ToList();
    }

    public bool VerifyAdmin(string account, string password)
    {
        return account == ADMIN_ACCOUNT && password == ADMIN_PASSWORD;
    }

    // ========== 統計與匯出 ==========

    public Dictionary<string, int> GetMealQuantityStats(string dateFrom, string dateTo)
    {
        var orders = GetOrdersByDateRange(dateFrom, dateTo);
        var counts = new Dictionary<string, int>();

        foreach (var order in orders)
        {
            var key = $"{order.Date}_{order.MealType}_{order.DietType}_{order.RicePortion}";
            if (!counts.ContainsKey(key))
                counts[key] = 0;
            counts[key]++;
        }

        return counts;
    }

    public Dictionary<string, EmployeeOrderStats> GetEmployeeOrderStats(string dateFrom, string dateTo)
    {
        var orders = GetOrdersByDateRange(dateFrom, dateTo);
        var employees = GetEmployees();
        var stats = new Dictionary<string, EmployeeOrderStats>();

        foreach (var emp in employees)
        {
            stats[emp.EmpID] = new EmployeeOrderStats
            {
                EmpID = emp.EmpID,
                EmpName = emp.EmpName,
                LunchCount = 0,
                DinnerCount = 0,
                TotalCount = 0
            };
        }

        foreach (var order in orders)
        {
            if (stats.TryGetValue(order.EmpID, out var stat))
            {
                stat.TotalCount++;
                if (order.MealType == MealType.LUNCH.ToString())
                    stat.LunchCount++;
                else if (order.MealType == MealType.DINNER.ToString())
                    stat.DinnerCount++;
            }
        }

        return stats;
    }
}

/// <summary>
/// 員工訂購統計
/// </summary>
public class EmployeeOrderStats
{
    public string EmpID { get; set; } = string.Empty;
    public string EmpName { get; set; } = string.Empty;
    public int LunchCount { get; set; }
    public int DinnerCount { get; set; }
    public int TotalCount { get; set; }
}

