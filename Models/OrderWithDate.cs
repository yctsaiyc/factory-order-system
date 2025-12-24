namespace FoodOrderSystem.Models;

/// <summary>
/// 帶日期的訂單（用於查詢結果）
/// </summary>
public class OrderWithDate
{
    public string Date { get; set; } = string.Empty;
    public string EmpID { get; set; } = string.Empty;
    public string MealType { get; set; } = string.Empty;
    public string DietType { get; set; } = string.Empty;
    public string RicePortion { get; set; } = string.Empty;
    public bool IsOrdered { get; set; }
    public string OrderTime { get; set; } = string.Empty;
    public bool AdminModified { get; set; }
}

