# Сборка и загрузка расширения УЗ_ext в тестовые базы с замером времени каждого шага.
#   .\tools\деплой.ps1                 — УНФ
#   .\tools\деплой.ps1 -Базы УНФ,БП,УТ — все три
#   .\tools\деплой.ps1 -БезСборки      — не пересобирать src_ext
# Бюджеты — docs/план_перевода_в_расширение.md, «Бюджеты времени проверок». Превышение — ПРЕДУПРЕЖДЕНИЕ.
param(
	[string[]]$Базы = @('УНФ'),
	[string]$СвояБаза = '',      # путь к своей файловой копии УНФ (вход Администратор) — для параллельной работы
	[switch]$БезСборки
)
$ErrorActionPreference = 'Stop'
$Корень = Split-Path $PSScriptRoot -Parent
$Exe = 'C:\Program Files\1cv8\8.3.27.1936\bin\1cv8.exe'
$Логи = if ($СвояБаза) { Join-Path $СвояБаза 'логи' } else { 'C:\1c_bases\логи' }
New-Item -ItemType Directory -Force $Логи | Out-Null
$Стенд = @{
	'УНФ' = @{ Путь = 'C:\1c_bases\UZ_UNF'; Пользователь = 'Администратор' }
	'БП'  = @{ Путь = 'C:\1c_bases\UZ_BP';  Пользователь = '1' }
	'УТ'  = @{ Путь = 'C:\1c_bases\UZ_UT';  Пользователь = 'Admin' }
}
if ($СвояБаза) {
	$Стенд['СВОЯ'] = @{ Путь = $СвояБаза; Пользователь = 'Администратор' }
	$Базы = @('СВОЯ')
}
$Итог = @()
$Ошибок = 0

function Шаг([string]$Название, [int]$Бюджет, [scriptblock]$Действие) {
	$Начало = Get-Date
	$Код = & $Действие
	$Сек = [math]::Round(((Get-Date) - $Начало).TotalSeconds, 1)
	$Метка = if ($Сек -gt $Бюджет) { "ПРЕДУПРЕЖДЕНИЕ: бюджет $Бюджет с превышен" } else { '' }
	$script:Итог += '{0,-32} {1,6} с  код {2}  {3}' -f $Название, $Сек, $Код, $Метка
	if ($Код -ne 0) { $script:Ошибок++ }
	return $Код
}

function Конфигуратор([hashtable]$База, [string]$Лог, [string[]]$Команда) {
	$Аргументы = @('DESIGNER', '/F', $База.Путь, '/N', $База.Пользователь,
		'/DisableStartupDialogs', '/DisableStartupMessages') + $Команда + @('/Out', $Лог)
	# Start-Process склеивает аргументы через пробел — значения с пробелами берём в кавычки
	$Аргументы = $Аргументы | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }
	# таймаут 3× бюджета: зависший конфигуратор (диалог, блокировка) не ждём вечно
	$Процесс = Start-Process -FilePath $Exe -ArgumentList $Аргументы -PassThru -WindowStyle Hidden
	if (-not $Процесс.WaitForExit(90000)) {
		$Процесс.Kill()
		Add-Content -Encoding utf8 $Лог 'ТАЙМАУТ 90 с: процесс снят'
		return 99
	}
	$Текст = Get-Content $Лог -Encoding utf8 -ErrorAction SilentlyContinue
	# код возврата 0 бывает и при ошибке — читаем лог
	$Плохие = $Текст | Where-Object { $_ -cmatch 'Ошибк|ошибк|не найден|Невозможно|ТАЙМАУТ' -and $_ -notmatch 'ошибок не обнаружено' }
	if ($Плохие) { return [math]::Max(1, $Процесс.ExitCode) }
	return $Процесс.ExitCode
}

# src_ext зафиксирован (исходник): сборка конвертером только до фиксации
if (-not $БезСборки -and -not (Test-Path "$Корень\src_ext\.ЗАФИКСИРОВАНО")) {
	[void](Шаг 'Сборка src_ext' 15 { python "$Корень\tools\собрать_src_ext.py" | Out-Null; $LASTEXITCODE })
}
[void](Шаг 'Проверка src_ext' 5 { python "$Корень\tools\собрать_src_ext.py" --проверка | Out-Null; $LASTEXITCODE })
[void](Шаг 'Офлайн-аудиты' 5 { python "$Корень\tools\аудиты\все_аудиты.py" --каталог "$Корень\src_ext" | Out-Null; $LASTEXITCODE })

foreach ($Имя in $Базы) {
	$База = $Стенд[$Имя]
	$Код = Шаг "$Имя загрузка" 20 { Конфигуратор $База "$Логи\$Имя`_load.log" @('/LoadConfigFromFiles', "$Корень\src_ext", '-Extension', 'УЗ_ext') }
	if ($Код -ne 0) { continue }
	$Код = Шаг "$Имя применение" 20 { Конфигуратор $База "$Логи\$Имя`_upd.log" @('/UpdateDBCfg', '-Extension', 'УЗ_ext') }
	if ($Код -ne 0) { continue }
	[void](Шаг "$Имя проверка модулей" 20 { Конфигуратор $База "$Логи\$Имя`_check.log" @('/CheckModules', '-ThinClient', '-Server', '-Extension', 'УЗ_ext') })
}

$Итог | ForEach-Object { $_ }
"ИТОГО шагов с ошибкой: $Ошибок   (логи: $Логи)"
exit [int]($Ошибок -gt 0)
