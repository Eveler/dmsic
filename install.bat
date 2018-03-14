python-3.5.4-webinstall.exe /passive InstallAllUsers=1 TargetDir=c:\Python35
c:\Python35\python.exe -m pip install -U zeep requests lxml sqlalchemy PyQt5
rem md c:\dmsic
rem xcopy xmlsigner c:\dmsic /E /H /Y
rem xcopy *.py c:\dmsic /E /H /Y
