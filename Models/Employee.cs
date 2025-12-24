namespace FoodOrderSystem.Models;

/// <summary>
/// 員工主檔
/// </summary>
public class Employee
{
    public int OID { get; set; }
    public string EmpID { get; set; } = string.Empty;
    public string EmpName { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string DeptCode { get; set; } = string.Empty;
}

