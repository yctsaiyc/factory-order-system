using Microsoft.AspNetCore.Mvc;
using FoodOrderSystem.Models;
using FoodOrderSystem.Services;

namespace FoodOrderSystem.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AdminController : ControllerBase
{
    private readonly FoodOrderService _service;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public AdminController(FoodOrderService service, IHttpContextAccessor httpContextAccessor)
    {
        _service = service;
        _httpContextAccessor = httpContextAccessor;
    }

    private bool IsAdmin()
    {
        var isAdmin = _httpContextAccessor.HttpContext?.Session.GetString("is_admin");
        return isAdmin == "true";
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] AdminLoginRequest request)
    {
        if (_service.VerifyAdmin(request.Account, request.Password))
        {
            _httpContextAccessor.HttpContext?.Session.SetString("is_admin", "true");
            _httpContextAccessor.HttpContext?.Session.SetString("admin_account", request.Account);
            return Ok(new { success = true, message = "管理員登入成功" });
        }

        return Unauthorized(new { success = false, message = "帳號或密碼錯誤" });
    }

    [HttpPost("logout")]
    public IActionResult Logout()
    {
        _httpContextAccessor.HttpContext?.Session.Clear();
        return Ok(new { success = true, message = "登出成功" });
    }

    [HttpGet("departments")]
    public IActionResult GetDepartments()
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var depts = _service.GetDepartments();
        return Ok(new { success = true, data = depts });
    }

    [HttpPost("departments")]
    public IActionResult SaveDepartment([FromBody] DepartmentRequest request)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var (success, message) = _service.SaveDepartment(request.OID, request.DeptCode, request.DeptName);

        if (success)
        {
            return Ok(new { success = true, message });
        }

        return BadRequest(new { success = false, message });
    }

    [HttpDelete("departments/{oid}")]
    public IActionResult DeleteDepartment(int oid)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var (success, message) = _service.DeleteDepartment(oid);
        return Ok(new { success, message });
    }

    [HttpGet("employees")]
    public IActionResult GetEmployees()
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var employees = _service.GetEmployees();
        // 隱藏密碼
        var result = employees.Select(e => new
        {
            e.OID,
            e.EmpID,
            e.EmpName,
            PasswordLength = e.Password.Length,
            e.DeptCode
        }).ToList();

        return Ok(new { success = true, data = result });
    }

    [HttpPost("employees")]
    public IActionResult SaveEmployee([FromBody] EmployeeRequest request)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var (success, message) = _service.SaveEmployee(request.OID, request.EmpID, request.EmpName, 
            request.Password, request.DeptCode);

        if (success)
        {
            return Ok(new { success = true, message });
        }

        return BadRequest(new { success = false, message });
    }

    [HttpDelete("employees/{oid}")]
    public IActionResult DeleteEmployee(int oid)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var (success, message) = _service.DeleteEmployee(oid);
        return Ok(new { success, message });
    }

    [HttpGet("windows")]
    public IActionResult GetWindows()
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var windows = _service.GetWindows();
        return Ok(new { success = true, data = windows });
    }

    [HttpPost("windows")]
    public IActionResult SaveWindow([FromBody] WindowRequest request)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var (success, message) = _service.SaveWindow(request.OID, request.EmpID, request.ResponsibleDeptCodes);

        if (success)
        {
            return Ok(new { success = true, message });
        }

        return BadRequest(new { success = false, message });
    }

    [HttpDelete("windows/{oid}")]
    public IActionResult DeleteWindow(int oid)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        var (success, message) = _service.DeleteWindow(oid);
        return Ok(new { success, message });
    }

    [HttpGet("orders")]
    public IActionResult GetOrders([FromQuery] string dateFrom, [FromQuery] string dateTo,
        [FromQuery] string? empId = null, [FromQuery] string? deptCode = null)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        if (string.IsNullOrEmpty(dateFrom) || string.IsNullOrEmpty(dateTo))
        {
            return BadRequest(new { success = false, message = "請提供日期區間" });
        }

        try
        {
            var orders = _service.GetOrdersByDateRange(dateFrom, dateTo, empId, deptCode);
            var ordersList = orders.Select(o => new
            {
                Date = o.Date,
                EmpID = o.EmpID,
                MealType = o.MealType,
                DietType = o.DietType,
                RicePortion = o.RicePortion,
                IsOrdered = o.IsOrdered,
                OrderTime = o.OrderTime,
                AdminModified = o.AdminModified
            }).ToList();
            return Ok(new { success = true, data = ordersList, count = ordersList.Count });
        }
        catch (Exception e)
        {
            return BadRequest(new { success = false, message = e.Message });
        }
    }

    [HttpPut("orders")]
    public IActionResult UpdateOrder([FromBody] UpdateOrderRequest request)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        if (string.IsNullOrEmpty(request.Date) || string.IsNullOrEmpty(request.EmpId) || 
            string.IsNullOrEmpty(request.MealType))
        {
            return BadRequest(new { success = false, message = "參數不完整" });
        }

        var (success, message) = _service.UpdateOrder(request.EmpId, request.MealType, request.DietType,
            request.RicePortion, request.Date, request.IsCancelled);

        if (success)
        {
            return Ok(new { success = true, message });
        }

        return BadRequest(new { success = false, message });
    }

    [HttpGet("stats/meal-quantity")]
    public IActionResult GetMealQuantityStats([FromQuery] string dateFrom, [FromQuery] string dateTo)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        if (string.IsNullOrEmpty(dateFrom) || string.IsNullOrEmpty(dateTo))
        {
            return BadRequest(new { success = false, message = "請提供日期區間" });
        }

        try
        {
            var stats = _service.GetMealQuantityStats(dateFrom, dateTo);
            return Ok(new { success = true, data = stats });
        }
        catch (Exception e)
        {
            return BadRequest(new { success = false, message = e.Message });
        }
    }

    [HttpGet("stats/employee-orders")]
    public IActionResult GetEmployeeOrderStats([FromQuery] string dateFrom, [FromQuery] string dateTo)
    {
        if (!IsAdmin())
        {
            return Forbid();
        }

        if (string.IsNullOrEmpty(dateFrom) || string.IsNullOrEmpty(dateTo))
        {
            return BadRequest(new { success = false, message = "請提供日期區間" });
        }

        try
        {
            var stats = _service.GetEmployeeOrderStats(dateFrom, dateTo);
            return Ok(new { success = true, data = stats.Values.ToList() });
        }
        catch (Exception e)
        {
            return BadRequest(new { success = false, message = e.Message });
        }
    }
}

public class AdminLoginRequest
{
    public string Account { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class DepartmentRequest
{
    public int? OID { get; set; }
    public string DeptCode { get; set; } = string.Empty;
    public string DeptName { get; set; } = string.Empty;
}

public class EmployeeRequest
{
    public int? OID { get; set; }
    public string EmpID { get; set; } = string.Empty;
    public string EmpName { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string DeptCode { get; set; } = string.Empty;
}

public class WindowRequest
{
    public int? OID { get; set; }
    public string EmpID { get; set; } = string.Empty;
    public List<string> ResponsibleDeptCodes { get; set; } = new();
}

public class UpdateOrderRequest
{
    public string Date { get; set; } = string.Empty;
    public string EmpId { get; set; } = string.Empty;
    public string MealType { get; set; } = string.Empty;
    public string DietType { get; set; } = string.Empty;
    public string RicePortion { get; set; } = string.Empty;
    public bool IsCancelled { get; set; }
}

