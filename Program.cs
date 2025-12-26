using FoodOrderSystem.Services;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Extensions.FileProviders;
using System.IO;

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

// CORRECTLY enable static file serving from the project root
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(
           Path.Combine(builder.Environment.ContentRootPath)),
    RequestPath = ""
});

app.UseCors();
app.UseSession();
app.UseRouting();

// API routes
app.MapControllers();

// --- HTML Page Routing ---

// Redirect root to the main employee page
app.MapGet("/", (HttpContext context) => {
    context.Response.Redirect("/employee", permanent: false);
    return Task.CompletedTask;
});

// Serve the main employee page (login/order)
app.MapGet("/employee", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "index.html");
    context.Response.ContentType = "text/html";
    await context.Response.SendFileAsync(htmlPath);
});

// Serve the admin login page
app.MapGet("/admin/login", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "admin_login.html");
    context.Response.ContentType = "text/html";
    await context.Response.SendFileAsync(htmlPath);
});

// Serve the admin dashboard
app.MapGet("/admin", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "admin_dashboard.html");
    context.Response.ContentType = "text/html";
    await context.Response.SendFileAsync(htmlPath);
});

// Serve the test page
app.MapGet("/test", async (HttpContext context) =>
{
    var htmlPath = Path.Combine(app.Environment.ContentRootPath, "test_page.html");
    context.Response.ContentType = "text/html";
    await context.Response.SendFileAsync(htmlPath);
});

app.Run();