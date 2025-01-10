@echo off
REM Conda 환경 활성화
call %USERPROFILE%\anaconda3\condabin\conda.bat activate fullstack

REM 첫 번째 스크립트 실행
cd /d C:\Users\bl4an\Documents\college_lectures\fullstack-service-programming\emergency_room_service_server\data_scripts\collect_data
python get_erb_info.py || exit /b 1
timeout /t 5 /nobreak

cd /d C:\Users\bl4an\Documents\college_lectures\fullstack-service-programming\emergency_room_service_server\data_scripts\collect_data
python get_ers_info.py || exit /b 1
timeout /t 5 /nobreak

REM 두 번째 스크립트 실행
cd /d C:\Users\bl4an\Documents\college_lectures\fullstack-service-programming\emergency_room_service_server\data_scripts\db_manager
python upload_erb_info.py || exit /b 1
timeout /t 5 /nobreak

cd /d C:\Users\bl4an\Documents\college_lectures\fullstack-service-programming\emergency_room_service_server\data_scripts\db_manager
python upload_ers_info.py || exit /b 1
timeout /t 5 /nobreak

REM 종료
exit /b 0
