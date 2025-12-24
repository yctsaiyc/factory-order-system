using FoodOrderSystem.Services;
using Microsoft.AspNetCore.HttpOverrides;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Session support
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Services
builder.Services.AddSingleton<FoodOrderService>();
builder.Services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.UseSession();
app.UseStaticFiles();
app.UseRouting();

// API routes
app.MapControllers();

// Serve static HTML files
app.MapGet("/", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "index.html");
    if (File.Exists(htmlPath))
    {
        context.Response.ContentType = "text/html";
        await context.Response.SendFileAsync(htmlPath);
    }
    else
    {
        await context.Response.WriteAsync("API Service is running. Please check /swagger for API documentation.");
    }
});

app.MapGet("/employee", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "index.html");
    if (File.Exists(htmlPath))
    {
        context.Response.ContentType = "text/html";
        await context.Response.SendFileAsync(htmlPath);
    }
});

app.MapGet("/admin/login", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "admin_login.html");
    if (File.Exists(htmlPath))
    {
        context.Response.ContentType = "text/html";
        await context.Response.SendFileAsync(htmlPath);
    }
});

app.MapGet("/admin", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "admin_dashboard.html");
    if (File.Exists(htmlPath))
    {
        context.Response.ContentType = "text/html";
        await context.Response.SendFileAsync(htmlPath);
    }
});

app.MapGet("/test", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "test_page.html");
    if (File.Exists(htmlPath))
    {
        context.Response.ContentType = "text/html";
        await context.Response.SendFileAsync(htmlPath);
    }
});

app.Run("http://localhost:5000");

