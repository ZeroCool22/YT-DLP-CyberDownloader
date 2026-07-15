; Instalador de YT-DLP CyberDownloader v1.1

#define MyAppName "YT-DLP CyberDownloader"
#define MyAppVersion "1.1"
#define MyAppPublisher "ZeroCool22"
#define MyAppURL "https://github.com/ZeroCool22"
#define MyAppExeName "YT-DLP CyberDownloader.exe"

[Setup]
AppId={{61DECC0B-599F-466B-9D2A-7FA66309F381}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
LicenseFile=license.txt
InfoBeforeFile=licenses\THIRD-PARTY-NOTICES.txt
OutputDir=installer_output
OutputBaseFilename=CyberDownloader_v1.1_Setup
SetupIconFile=assests\youtube.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern dynamic

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "output\main\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "output\main\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tools\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "tools\ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "license.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "licenses\*"; DestDir: "{app}\licenses"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
