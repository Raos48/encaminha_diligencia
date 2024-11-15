@echo off
echo Atualizando o programa...
timeout /t 3 /nobreak > nul

:wait_for_exit
tasklist /FI "IMAGENAME eq encaminha_diligencia.exe" 2>NUL | find /I "encaminha_diligencia.exe" >NUL
if not errorlevel 1 (
    echo O programa ainda est� em execu��o. Aguardando...
    timeout /t 2 /nobreak > nul
    goto :wait_for_exit
)

echo Substituindo o execut�vel antigo pelo novo...
move /Y "C:\Users\Ricardo\OneDrive - INSS\PYTHON\encaminha_junta_diligencia\dist\encaminha_diligencia.exe.new" "C:\Users\Ricardo\OneDrive - INSS\PYTHON\encaminha_junta_diligencia\dist\encaminha_diligencia.exe"
if %ERRORLEVEL% neq 0 (
    echo Falha ao mover o novo execut�vel.
    pause
    exit /b
)

echo Atualiza��o conclu�da com sucesso.
echo Por favor, inicie a nova vers�o manualmente.
pause
exit
