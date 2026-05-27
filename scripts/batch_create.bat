@echo off
REM batch_create.bat — массовое создание видео (Windows)
REM Запуск: batch_create.bat 7

set COUNT=%1
if "%COUNT%"=="" set COUNT=7

echo Создание %COUNT% видео...
echo ================================

for /L %%i in (1,1,%COUNT%) do (
    echo.
    echo [%%i/%COUNT%] Создание видео...
    python create_video.py --auto --no-upload

    if %%i LSS %COUNT% (
        echo Пауза 30 секунд...
        timeout /t 30 /nobreak >nul
    )
)

echo.
echo Все %COUNT% видео созданы!
pause
