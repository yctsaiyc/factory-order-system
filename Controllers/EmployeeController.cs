using Microsoft.AspNetCore.Mvc;
using FoodOrderSystem.Models;
using FoodOrderSystem.Services;

namespace FoodOrderSystem.Controllers;

[ApiController]
[Route("api/[controller]")]
public class EmployeeController : ControllerBase
{
    private readonly FoodOrderService _service;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public EmployeeController(FoodOrderService service, IHttpContextAccessor httpContextAccessor)
    {
        _service = service;
        _httpContextAccessor = httpContextAccessor;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var (success, employee) = _service.VerifyEmployee(request.EmpId, request.Password);

        if (success && employee != null)
        {
            _httpContextAccessor.HttpContext?.Session.SetString("emp_id", employee.EmpID);
            _httpContextAccessor.HttpContext?.Session.SetString("emp_name", employee.EmpName);
            _httpContextAccessor.HttpContext?.Session.SetString("is_admin", "false");

            return Ok(new
            {
                success = true,
                message = "登入成功",
                employee = new
                {
                    employee.EmpID,
                    employee.EmpName,
                    employee.DeptCode
                }
            });
        }

        return Unauthorized(new { success = false, message = "員工編號或密碼錯誤" });
    }

    [HttpPost("logout")]
    public IActionResult Logout()
    {
        _httpContextAccessor.HttpContext?.Session.Clear();
        return Ok(new { success = true, message = "登出成功" });
    }

    [HttpGet("today-orders")]
    public IActionResult GetTodayOrders()
    {
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        if (string.IsNullOrEmpty(empId))
        {
            return Unauthorized(new { success = false, message = "請先登入" });
        }

        var orders = _service.GetTodayOrders(empId);
        var today = FoodOrderService.FormatDate(DateTime.Now);

        var result = new
        {
            date = today,
            lunch = orders.ContainsKey(MealType.LUNCH.ToString()) && orders[MealType.LUNCH.ToString()]?.IsOrdered == true
                ? new
                {
                    orders[MealType.LUNCH.ToString()]!.DietType,
                    orders[MealType.LUNCH.ToString()]!.RicePortion,
                    orders[MealType.LUNCH.ToString()]!.OrderTime,
                    orders[MealType.LUNCH.ToString()]!.AdminModified
                }
                : null,
            dinner = orders.ContainsKey(MealType.DINNER.ToString()) && orders[MealType.DINNER.ToString()]?.IsOrdered == true
                ? new
                {
                    orders[MealType.DINNER.ToString()]!.DietType,
                    orders[MealType.DINNER.ToString()]!.RicePortion,
                    orders[MealType.DINNER.ToString()]!.OrderTime,
                    orders[MealType.DINNER.ToString()]!.AdminModified
                }
                : null,
            lunch_cutoff = _service.CheckCutoff(MealType.LUNCH.ToString()),
            dinner_cutoff = _service.CheckCutoff(MealType.DINNER.ToString())
        };

        return Ok(new { success = true, data = result });
    }

    [HttpPost("order")]
    public IActionResult CreateOrder([FromBody] CreateOrderRequest request)
    {
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        if (string.IsNullOrEmpty(empId))
        {
            return Unauthorized(new { success = false, message = "請先登入" });
        }

        if (string.IsNullOrEmpty(request.MealType) || string.IsNullOrEmpty(request.DietType) || 
            string.IsNullOrEmpty(request.RicePortion))
        {
            return BadRequest(new { success = false, message = "參數不完整" });
        }

        var (success, message) = _service.CreateOrder(empId, request.MealType, request.DietType, 
            request.RicePortion, request.Date);

        if (success)
        {
            return Ok(new { success = true, message });
        }

        return BadRequest(new { success = false, message });
    }

    [HttpPost("cancel-order")]
    public IActionResult CancelOrder([FromBody] CancelOrderRequest request)
    {
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        if (string.IsNullOrEmpty(empId))
        {
            return Unauthorized(new { success = false, message = "請先登入" });
        }

        if (string.IsNullOrEmpty(request.MealType))
        {
            return BadRequest(new { success = false, message = "參數不完整" });
        }

        var (success, message) = _service.CancelOrder(empId, request.MealType, request.Date);

        if (success)
        {
            return Ok(new { success = true, message });
        }

        return BadRequest(new { success = false, message });
    }

    [HttpGet("weekly-orders")]
    public IActionResult GetWeeklyOrders([FromQuery] string weekType = "current")
    {
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        if (string.IsNullOrEmpty(empId))
        {
            return Unauthorized(new { success = false, message = "請先登入" });
        }

        // 簡化實現，實際應根據weekType處理
        var today = DateTime.Now;
        var dateFrom = today.AddDays(-(int)today.DayOfWeek + 1).ToString("yyyy-MM-dd");
        var dateTo = today.AddDays(-(int)today.DayOfWeek + 5).ToString("yyyy-MM-dd");

        if (weekType == "next")
        {
            dateFrom = today.AddDays(-(int)today.DayOfWeek + 8).ToString("yyyy-MM-dd");
            dateTo = today.AddDays(-(int)today.DayOfWeek + 12).ToString("yyyy-MM-dd");
        }
        else if (weekType == "month")
        {
            dateFrom = new DateTime(today.Year, today.Month, 1).ToString("yyyy-MM-dd");
            dateTo = new DateTime(today.Year, today.Month, DateTime.DaysInMonth(today.Year, today.Month)).ToString("yyyy-MM-dd");
        }

        var orders = _service.GetOrdersByDateRange(dateFrom, dateTo, empId);
        var ordersByDate = new Dictionary<string, object>();

        foreach (var order in orders)
        {
            var dateKey = order.Date;
            if (!ordersByDate.ContainsKey(dateKey))
            {
                ordersByDate[dateKey] = new Dictionary<string, object?> { { "LUNCH", null }, { "DINNER", null } };
            }

            var dateDict = (Dictionary<string, object?>)ordersByDate[dateKey];
            dateDict[order.MealType] = new
            {
                order.Date,
                order.EmpID,
                order.MealType,
                order.DietType,
                order.RicePortion,
                order.IsOrdered,
                order.OrderTime,
                order.AdminModified
            };
        }

        return Ok(new { success = true, data = ordersByDate });
    }

    [HttpPost("weekly-orders")]
    public IActionResult SaveWeeklyOrders([FromBody] WeeklyOrdersRequest request)
    {
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        if (string.IsNullOrEmpty(empId))
        {
            return Unauthorized(new { success = false, message = "請先登入" });
        }

        var successCount = 0;
        var errorCount = 0;
        var errors = new List<string>();

        foreach (var orderData in request.Orders)
        {
            if (string.IsNullOrEmpty(orderData.DietType) || string.IsNullOrEmpty(orderData.RicePortion))
            {
                var (success, message) = _service.CancelOrder(empId, orderData.MealType, orderData.Date);
                if (success) successCount++; else { errorCount++; errors.Add($"{orderData.Date} {orderData.MealType}: {message}"); }
            }
            else
            {
                var (success, message) = _service.CreateOrder(empId, orderData.MealType, orderData.DietType, 
                    orderData.RicePortion, orderData.Date);
                if (success) successCount++; else { errorCount++; errors.Add($"{orderData.Date} {orderData.MealType}: {message}"); }
            }
        }

        return Ok(new
        {
            success = true,
            message = $"共處理 {successCount + errorCount} 筆，成功 {successCount} 筆，失敗 {errorCount} 筆",
            success_count = successCount,
            error_count = errorCount,
            errors
        });
    }

    [HttpGet("history")]
    public IActionResult GetHistory([FromQuery] string dateFrom, [FromQuery] string dateTo)
    {
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        if (string.IsNullOrEmpty(empId))
        {
            return Unauthorized(new { success = false, message = "請先登入" });
        }

        if (string.IsNullOrEmpty(dateFrom) || string.IsNullOrEmpty(dateTo))
        {
            return BadRequest(new { success = false, message = "請提供日期區間" });
        }

        try
        {
            var orders = _service.GetOrdersByDateRange(dateFrom, dateTo, empId);
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
}

public class LoginRequest
{
    public string EmpId { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class CreateOrderRequest
{
    public string MealType { get; set; } = string.Empty;
    public string DietType { get; set; } = string.Empty;
    public string RicePortion { get; set; } = string.Empty;
    public string? Date { get; set; }
}

public class CancelOrderRequest
{
    public string MealType { get; set; } = string.Empty;
    public string? Date { get; set; }
}

public class WeeklyOrdersRequest
{
    public List<WeeklyOrderItem> Orders { get; set; } = new();
}

public class WeeklyOrderItem
{
    public string Date { get; set; } = string.Empty;
    public string MealType { get; set; } = string.Empty;
    public string? DietType { get; set; }
    public string? RicePortion { get; set; }
}

