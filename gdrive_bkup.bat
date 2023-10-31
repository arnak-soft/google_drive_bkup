set newdir="C:\mySand\GDriveBkup\%date:~6,4%_%date:~3,2%_%date:~0,2%_%time:~0,2%_%time:~3,2%_gdrive_bkup"
rem md "C:\mySand\GDriveBkup\%date:~6,4%_%date:~3,2%_%date:~0,2%_%time:~0,2%_%time:~3,2%_gdrive_bkup"
echo Creating new dir %newdir%
md %newdir%
xcopy /E /I /-B "G:\Мой диск" %newdir%