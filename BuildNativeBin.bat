IF NOT EXIST bin MKDIR bin
IF NOT EXIST bin\linux MKDIR bin\linux
IF NOT EXIST bin\windows MKDIR bin\windows

for /d %%i in (packages\*) do ( 
  IF EXIST "%%i\runtimes\win-x64\native" (
    copy /y "%%i\runtimes\win-x64\native" bin\windows))

for /d %%i in (packages\*) do ( 
  IF EXIST "%%i\runtimes\linux-x64\native" (
    copy /y "%%i\runtimes\linux-x64\native" bin\linux))
