IF NOT EXIST mikecore MKDIR mikecore
IF NOT EXIST mikecore\bin MKDIR mikecore\bin
IF NOT EXIST mikecore\bin\linux MKDIR mikecore\bin\linux
IF NOT EXIST mikecore\bin\windows MKDIR mikecore\bin\windows

for /d %%i in (packages\*) do ( 
  IF EXIST "%%i\runtimes\win-x64\native" (
    copy /y "%%i\runtimes\win-x64\native" mikecore\bin\windows))

for /d %%i in (packages\*) do ( 
  IF EXIST "%%i\runtimes\linux-x64\native" (
    copy /y "%%i\runtimes\linux-x64\native" mikecore\bin\linux))
