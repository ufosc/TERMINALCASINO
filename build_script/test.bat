
@echo off

echo.
echo ============================================================
echo                    TEST SCRIPTS
echo ============================================================
echo.

cd /d %~dp0..

set TARGET_DIR=tests
set "TEST_EXIT_CODE=0"


echo ============================================================
echo                    RUNNING TESTS
echo ============================================================
echo.

for %%f in (%TARGET_DIR%/*.py) do (

    if not %%~nf == __init__ (
        echo.
        echo ------------------------------------------------------------
        echo                  Running script: %%f
        echo ------------------------------------------------------------
        echo.

        pytest tests/%%~nf.py
        if errorlevel 1 set "TEST_EXIT_CODE=1"

        echo.
        echo.
    )
)

echo.
echo ============================================================
echo                    ALL TESTS COMPLETE
echo ============================================================
echo.

exit /b %TEST_EXIT_CODE%
