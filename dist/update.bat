@echo off
echo Atualizando o programa...
timeout /t 3 /nobreak > nul

:wait_for_exit
tasklist /FI "IMAGENAME eq encaminha_diligencia.exe" 2>NUL | find /I "encaminha_diligencia.exe" >NUL
if not errorlevel 1 (
    echo O programa ainda está em execução. Aguardando...
    timeout /t 2 /nobreak > nul
    goto :wait_for_exit
)

echo Substituindo o executável antigo pelo novo...
move /Y "C:\Users\Ricardo\OneDrive - INSS\PYTHON\encaminha_junta_diligencia\dist\encaminha_diligencia.exe.new" "C:\Users\Ricardo\OneDrive - INSS\PYTHON\encaminha_junta_diligencia\dist\encaminha_diligencia.exe"
if %ERRORLEVEL% neq 0 (
    echo Falha ao mover o novo executável.
    pause
    exit /b
)

echo Atualização concluída com sucesso.
echo Por favor, inicie a nova versão manualmente.
pause
exit
