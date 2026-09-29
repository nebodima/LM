# Финальная проверка одной командой: аудиты → деплой → полный прогон → (сценарии ролей).
# Печатает по строке на шаг и один итог; останавливается на первом красном шаге.
#   pwsh -File tools\финал.ps1 -База C:\1c_bases\UZ_BP_E
#   pwsh -File tools\финал.ps1 -База C:\1c_bases\UZ_BP_E -Сценарии
#   pwsh -File tools\финал.ps1 -База C:\1c_bases\UZ_BP_E -БезДеплоя      (база уже с текущим кодом)
# Код выхода 0 — всё зелёное, 1 — красный шаг (его хвост вывода напечатан).
param(
	[Parameter(Mandatory = $true)][string]$База,
	[string]$Пользователь = '1',
	[switch]$Сценарии,
	[switch]$БезДеплоя
)
$ErrorActionPreference = 'Continue'
$env:PYTHONIOENCODING = 'utf-8'
$Корень = Split-Path -Parent $PSScriptRoot
Set-Location $Корень
$Итог = @()
$Всего = [Diagnostics.Stopwatch]::StartNew()

function Шаг([string]$Имя, [int]$Бюджет, [scriptblock]$Команда) {
	$Часы = [Diagnostics.Stopwatch]::StartNew()
	$Вывод = & $Команда 2>&1 | Out-String
	$Код = $LASTEXITCODE
	$Сек = [math]::Round($Часы.Elapsed.TotalSeconds, 1)
	$Метка = if ($Код -eq 0) { 'ок' } else { 'КРАСНЫЙ' }
	$Сверх = if ($Сек -gt $Бюджет) { "  ПРЕВЫШЕН бюджет $Бюджет с" } else { '' }
	$Строка = '{0,-22} {1,-8} {2,6} с{3}' -f $Имя, $Метка, $Сек, $Сверх
	$script:Итог += $Строка
	Write-Output $Строка
	if ($Код -ne 0) {
		Write-Output '--- хвост вывода ---'
		Write-Output (($Вывод -split "`n" | Select-Object -Last 25) -join "`n")
		Write-Output ('ИТОГ: КРАСНЫЙ на шаге «{0}», всего {1:N0} с' -f $Имя, $Всего.Elapsed.TotalSeconds)
		exit 1
	}
}

Шаг 'аудиты' 6 { python tools\аудиты\все_аудиты.py }
if (-not $БезДеплоя) {
	Шаг 'деплой' 90 { pwsh -NoProfile -File tools\деплой.ps1 -СвояБаза $База -Пользователь $Пользователь }
}
Шаг 'полный прогон' 120 { python tools\прогон.py "--база=$База" "--пользователь=$Пользователь" }
if ($Сценарии) {
	Шаг 'сценарии ролей' 150 { python tools\сценарии\прогон_сценариев.py "--база=$База" }
}
Write-Output ('ИТОГ: зелёный, всего {0:N0} с' -f $Всего.Elapsed.TotalSeconds)
exit 0
