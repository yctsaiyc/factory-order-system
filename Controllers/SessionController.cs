using Microsoft.AspNetCore.Mvc;

namespace FoodOrderSystem.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SessionController : ControllerBase
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public SessionController(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    [HttpGet("check-session")]
    public IActionResult CheckSession()
    {
        var isAdmin = _httpContextAccessor.HttpContext?.Session.GetString("is_admin");
        var adminAccount = _httpContextAccessor.HttpContext?.Session.GetString("admin_account");
        var empId = _httpContextAccessor.HttpContext?.Session.GetString("emp_id");
        var empName = _httpContextAccessor.HttpContext?.Session.GetString("emp_name");

        if (isAdmin == "true")
        {
            return Ok(new
            {
                success = true,
                is_admin = true,
                account = adminAccount
            });
        }
        else if (!string.IsNullOrEmpty(empId))
        {
            return Ok(new
            {
                success = true,
                is_admin = false,
                emp_id = empId,
                emp_name = empName
            });
        }

        return Ok(new { success = false, message = "未登入" });
    }
}

