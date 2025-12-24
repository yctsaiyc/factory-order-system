namespace FoodOrderSystem.Models;

/// <summary>
/// 餐點訂單
/// </summary>
public class MealOrder
{
    public string EmpID { get; set; } = string.Empty;
    public string MealType { get; set; } = string.Empty;
    public string DietType { get; set; } = string.Empty;
    public string RicePortion { get; set; } = string.Empty;
    public bool IsOrdered { get; set; }
    public string OrderTime { get; set; } = string.Empty;
    public bool AdminModified { get; set; }
}

