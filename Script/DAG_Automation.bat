@echo off
REM Define the paths to the Python interpreter and scripts
set python_path="C:\Users\Temidayo\anaconda3\python.exe"
set borrow_path="C:\Users\Temidayo\Desktop\Test_Question\Script\Borrow_Scripts\borrow.py"
set loan_path="C:\Users\Temidayo\Desktop\Test_Question\Script\Loan_Scripts\loan.py"
set repayment_path="C:\Users\Temidayo\Desktop\Test_Question\Script\Repayment_Scripts\Repayment.py"
set schedule_path="C:\Users\Temidayo\Desktop\Test_Question\Script\Schedule_Scripts\schedule.py"

REM Define the path for log files
set log_path="C:\Users\Temidayo\Desktop\Test_Question\Script\log.txt"

REM Get current date and time
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%b-%%a)
for /f "tokens=1-4 delims=:. " %%a in ('time /t') do (set mytime=%%a:%%b:%%c)

REM Run borrow script and log output with date and time
echo %mydate% %mytime% Running borrow script >> %log_path% 2>&1
%python_path% %borrow_path% >> %log_path% 2>&1
set borrow_exit_code=%errorlevel%

REM Check if borrow script was successful
if %borrow_exit_code% equ 0 (
    REM Borrow script was successful, now run loan script
    echo %mydate% %mytime% Running loan script >> %log_path% 2>&1
    %python_path% %loan_path% >> %log_path% 2>&1
    set loan_exit_code=%errorlevel%
    
    REM Check if loan script was successful
    if %loan_exit_code% equ 0 (
        REM Loan script was successful, now run repayment script
        echo %mydate% %mytime% Running repayment script >> %log_path% 2>&1
        %python_path% %repayment_path% >> %log_path% 2>&1
        set repayment_exit_code=%errorlevel%
        
        REM Check if repayment script was successful
        if %repayment_exit_code% equ 0 (
            REM Repayment script was successful, now run schedule script
            echo %mydate% %mytime% Running schedule script >> %log_path% 2>&1
            %python_path% %schedule_path% >> %log_path% 2>&1
            set schedule_exit_code=%errorlevel%
            
            REM Optionally, you can check schedule script exit code here if needed
            if %schedule_exit_code% equ 0 (
                echo %mydate% %mytime% All scripts completed successfully. >> %log_path%
            ) else (
                echo %mydate% %mytime% Schedule script failed. >> %log_path%
            )
        ) else (
            echo %mydate% %mytime% Repayment script failed. Schedule script will not be executed. >> %log_path%
        )
    ) else (
        echo %mydate% %mytime% Loan script failed. Repayment and Schedule scripts will not be executed. >> %log_path%
    )
) else (
    echo %mydate% %mytime% Borrow script failed. Loan, Repayment, and Schedule scripts will not be executed. >> %log_path%
)

echo %mydate% %mytime% Task completed. Check log at %log_path%