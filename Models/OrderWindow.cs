namespace FoodOrderSystem.Models;

/// <summary>
/// 訂餐窗口主檔
/// </summary>
public class OrderWindow
{
    public int OID { get; set; }
    public string EmpID { get; set; } = string.Empty;
    public List<string> ResponsibleDeptCodes { get; set; } = new();
}

