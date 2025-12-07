# Script para actualizar el sitio web en Render
# Uso: .\actualizar.ps1 "mensaje de commit"

param(
    [Parameter(Mandatory=$true)]
    [string]$mensaje
)

Write-Host "🚀 Iniciando proceso de actualización..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar si hay cambios
Write-Host "📋 Verificando cambios..." -ForegroundColor Yellow
git status --short

if ((git status --short).Length -eq 0) {
    Write-Host "❌ No hay cambios para subir." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Agregando archivos al commit..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💾 Creando commit..." -ForegroundColor Yellow
git commit -m "$mensaje"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al crear commit." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🌐 Subiendo cambios a GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al subir cambios." -ForegroundColor Red
    Write-Host "💡 Tip: Verifica tu token de acceso de GitHub" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "✅ ¡Cambios subidos exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Render detectará los cambios automáticamente..." -ForegroundColor Cyan
Write-Host "🕐 Tiempo estimado de despliegue: 2-5 minutos" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Monitorea el progreso en: https://dashboard.render.com/" -ForegroundColor Blue
Write-Host "🌍 Tu sitio: https://transportesdelbajio.com" -ForegroundColor Blue
Write-Host ""
Write-Host "✨ ¡Proceso completado!" -ForegroundColor Green
