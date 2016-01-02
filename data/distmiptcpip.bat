@echo off
REM Copyright IBM Corporation 2013. All Rights Reserved.
REM Example .bat file that starts up a TCP/IP worker on the local
REM for use with distributed parallel MIP. The first argument to
REM this script is the port number on which to listen, the remaining
REM arguments are the distributed MIP application and its arguments.

REM Start the TCP/IP worker on the localhost. The port on which
REM the worker listens is the first argument to this script. The
REM task id of the worker is stored in file tcpippid. We use that
REM to check whether the worker did start up and to kill it later.
echo Starting worker
DEL /Q tcpippid 2>NUL
START /MIN %CPLEX_STUDIO_DIR126%\cplex\bin\x86_win32\cplex.exe -worker=tcpip -address=localhost:%1 -pidfile=tcpippid
IF ERRORLEVEL 1 GOTO ERROR
SHIFT

REM Wait 5 seconds so that we can be sure the worker did start up
REM before we continue. Use TASKLIST to make sure the worker did
REM actually start up.
START /MIN /WAIT C:\Windows\System32\TIMEOUT 5
FOR /f %%P IN (tcpippid) DO (C:\Windows\System32\TASKLIST /fo LIST /fi "PID eq %%P")
IF ERRORLEVEL 1 GOTO ERROR

REM Now run the distmip example. What to run is specified by the
REM remaining command line arguments.
echo Running example
%1 %2 %3 %4 %5 %6 %7 %8 %9
IF ERRORLEVEL 1 GOTO ERROR
SET EXITCODE=0

GOTO OK
:ERROR
SET EXITCODE=1
echo Failed to run.

:OK
REM Kill the TCP/IP worker
echo Stopping worker
FOR /f %%P IN (tcpippid) DO (C:\Windows\System32\TASKKILL /t /f /pid %%P)
DEL /Q tcpippid

SET ERRORLEVEL=%EXITCODE%
