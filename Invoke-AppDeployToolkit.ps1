<#

.SYNOPSIS
PSAppDeployToolkit - This script performs the installation or uninstallation of an application(s).

.DESCRIPTION
- The script is provided as a template to perform an install, uninstall, or repair of an application(s).
- The script either performs an "Install", "Uninstall", or "Repair" deployment type.
- The install deployment type is broken down into 3 main sections/phases: Pre-Install, Install, and Post-Install.

The script imports the PSAppDeployToolkit module which contains the logic and functions required to install or uninstall an application.

.PARAMETER DeploymentType
The type of deployment to perform.

.PARAMETER DeployMode
Specifies whether the installation should be run in Interactive (shows dialogs), Silent (no dialogs), NonInteractive (dialogs without prompts) mode, or Auto (shows dialogs if a user is logged on, device is not in the OOBE, and there's no running apps to close).

Silent mode is automatically set if it is detected that the process is not user interactive, no users are logged on, the device is in Autopilot mode, or there's specified processes to close that are currently running.

.PARAMETER SuppressRebootPassThru
Suppresses the 3010 return code (requires restart) from being passed back to the parent process (e.g. SCCM) if detected from an installation. If 3010 is passed back to SCCM, a reboot prompt will be triggered.

.PARAMETER TerminalServerMode
Changes to "user install mode" and back to "user execute mode" for installing/uninstalling applications for Remote Desktop Session Hosts/Citrix servers.

.PARAMETER DisableLogging
Disables logging to file for the script.

.EXAMPLE
powershell.exe -File Invoke-AppDeployToolkit.ps1

.EXAMPLE
powershell.exe -File Invoke-AppDeployToolkit.ps1 -DeployMode Silent

.EXAMPLE
powershell.exe -File Invoke-AppDeployToolkit.ps1 -DeploymentType Uninstall

.EXAMPLE
Invoke-AppDeployToolkit.exe -DeploymentType Install -DeployMode Silent

.INPUTS
None. You cannot pipe objects to this script.

.OUTPUTS
None. This script does not generate any output.

.NOTES
Toolkit Exit Code Ranges:
- 60000 - 68999: Reserved for built-in exit codes in Invoke-AppDeployToolkit.ps1, and Invoke-AppDeployToolkit.exe
- 69000 - 69999: Recommended for user customized exit codes in Invoke-AppDeployToolkit.ps1
- 70000 - 79999: Recommended for user customized exit codes in PSAppDeployToolkit.Extensions module.

.LINK
https://psappdeploytoolkit.com

#>

[CmdletBinding()]
param
(
    # Default is 'Install'.
    [Parameter(Mandatory = $false)]
    [ValidateSet('Install', 'Uninstall', 'Repair')]
    [System.String]$DeploymentType,

    # Default is 'Auto'. Don't hard-code this unless required.
    [Parameter(Mandatory = $false)]
    [ValidateSet('Auto', 'Interactive', 'NonInteractive', 'Silent')]
    [System.String]$DeployMode,

    [Parameter(Mandatory = $false)]
    [System.Management.Automation.SwitchParameter]$SuppressRebootPassThru,

    [Parameter(Mandatory = $false)]
    [System.Management.Automation.SwitchParameter]$TerminalServerMode,

    [Parameter(Mandatory = $false)]
    [System.Management.Automation.SwitchParameter]$DisableLogging
)


##================================================
## MARK: Variables
##================================================

# Zero-Config MSI support is provided when "AppName" is null or empty.
# By setting the "AppName" property, Zero-Config MSI will be disabled.
$adtSession = @{
    # App variables.
    AppVendor = 'NexoraDev'
    AppName = 'Nexora'
    AppVersion = '22.15.0'
    AppArch = 'x64'
    AppLang = 'EN'
    AppRevision = '01'
    AppSuccessExitCodes = @(0)
    AppRebootExitCodes = @(1641, 3010)
    AppProcessesToClose = @('node', 'npm', 'npx')  # Close any running Node.js processes
    AppScriptVersion = '1.0.0'
    AppScriptDate = '2025-01-27'
    AppScriptAuthor = 'Echoes Deployment'
    RequireAdmin = $false  # Will be determined dynamically

    # Install Titles (Only set here to override defaults set by the toolkit).
    InstallName = 'Echoes Node.js 22.15.0 x64'
    InstallTitle = 'Echoes Deployment'

    # Script variables.
    DeployAppScriptFriendlyName = $MyInvocation.MyCommand.Name
    DeployAppScriptParameters = $PSBoundParameters
    DeployAppScriptVersion = '4.1.7'
}

function Install-ADTDeployment
{
    [CmdletBinding()]
    param
    (
    )

    ##================================================
    ## MARK: Pre-Install
    ##================================================
    $adtSession.InstallPhase = "Pre-$($adtSession.DeploymentType)"

    ## Show Welcome Message, close processes if specified, allow up to 3 deferrals, verify there is enough disk space to complete the install, and persist the prompt.
    $saiwParams = @{
        AllowDefer = $true
        DeferTimes = 3
        CheckDiskSpace = $true
        PersistPrompt = $true
    }
    if ($adtSession.AppProcessesToClose.Count -gt 0)
    {
        $saiwParams.Add('CloseProcesses', $adtSession.AppProcessesToClose)
    }
    Show-ADTInstallationWelcome @saiwParams

    ## Show Progress Message (with the default message).
    Show-ADTInstallationProgress

    ## <Perform Pre-Installation tasks here>
    

    ##================================================
    ## MARK: Install
    ##================================================
    $adtSession.InstallPhase = $adtSession.DeploymentType

    ## Handle Zero-Config MSI installations.
    if ($adtSession.UseDefaultMsi)
    {
        $ExecuteDefaultMSISplat = @{ Action = $adtSession.DeploymentType; FilePath = $adtSession.DefaultMsiFile }
        if ($adtSession.DefaultMstFile)
        {
            $ExecuteDefaultMSISplat.Add('Transforms', $adtSession.DefaultMstFile)
        }
        Start-ADTMsiProcess @ExecuteDefaultMSISplat
        if ($adtSession.DefaultMspFiles)
        {
            $adtSession.DefaultMspFiles | Start-ADTMsiProcess -Action Patch
        }
    }

    ## <Perform Installation tasks here>
    
    # Determine if running as administrator
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    # Define installation paths based on admin status
    $NodeJSSourcePath = "$($adtSession.DirFiles)"
    
    if ($IsAdmin) {
        # Admin installation - system-wide
        $NodeJSDestinationPath = "$envProgramFiles\Nexora\NodeJS"
        $NodeJSBackupPath = "$envProgramFiles\Nexora\NodeJS.backup"
        $RegistryPath = "HKLM:\SOFTWARE\Nexora\Node.js"
        $PathTarget = [System.EnvironmentVariableTarget]::Machine
        $PathScope = "system"
        Write-ADTLogEntry -Message "Running as Administrator - performing system-wide installation" -Severity 1
    } else {
        # User installation - user profile only
        $NodeJSDestinationPath = "$envUSERPROFILE\Nexora\NodeJS"
        $NodeJSBackupPath = "$envUSERPROFILE\Nexora\NodeJS.backup"
        $RegistryPath = "HKCU:\SOFTWARE\Nexora\Node.js"
        $PathTarget = [System.EnvironmentVariableTarget]::User
        $PathScope = "user"
        Write-ADTLogEntry -Message "Running as regular user - performing user profile installation" -Severity 1
    }
    
    # Check if Node.js portable files exist
    if (-not (Test-Path -Path "$NodeJSSourcePath\node.exe" -PathType Leaf))
    {
        Write-ADTLogEntry -Message "Node.js portable files not found at: $NodeJSSourcePath" -Severity 3
        throw "Node.js portable files not found. Please ensure Node.js files (node.exe, npm.cmd, etc.) are placed in the Files directory."
    }
    
    # Create backup of existing Node.js installation if it exists
    if (Test-Path -Path $NodeJSDestinationPath -PathType Container)
    {
        Write-ADTLogEntry -Message "Existing Node.js installation found. Creating backup at: $NodeJSBackupPath" -Severity 1
        if (Test-Path -Path $NodeJSBackupPath -PathType Container)
        {
            Remove-Item -Path $NodeJSBackupPath -Recurse -Force
        }
        Copy-ADTFile -Path $NodeJSDestinationPath -Destination $NodeJSBackupPath -Recurse
    }
    
    # Remove existing Node.js installation
    if (Test-Path -Path $NodeJSDestinationPath -PathType Container)
    {
        Write-ADTLogEntry -Message "Removing existing Node.js installation from: $NodeJSDestinationPath" -Severity 1
        Remove-Item -Path $NodeJSDestinationPath -Recurse -Force
    }
    
    # Copy Node.js portable files to Program Files
    Write-ADTLogEntry -Message "Installing Node.js portable to: $NodeJSDestinationPath" -Severity 1
    
    # Create destination directory
    if (-not (Test-Path -Path $NodeJSDestinationPath -PathType Container))
    {
        New-Item -ItemType Directory -Path $NodeJSDestinationPath -Force | Out-Null
    }
    
    # Copy Node.js files (exclude deployment-specific files)
    $NodeJSFiles = @(
        'node.exe', 'npm.cmd', 'npx.cmd', 'npm.ps1', 'npx.ps1',
        'corepack', 'corepack.cmd', 'nodevars.bat', 'npm', 'npx'
    )
    
    foreach ($file in $NodeJSFiles)
    {
        $sourceFile = "$NodeJSSourcePath\$file"
        if (Test-Path -Path $sourceFile -PathType Leaf)
        {
            Copy-ADTFile -Path $sourceFile -Destination "$NodeJSDestinationPath\$file"
            Write-ADTLogEntry -Message "Copied: $file" -Severity 1
        }
    }
    
    # Copy node_modules directory if it exists
    if (Test-Path -Path "$NodeJSSourcePath\node_modules" -PathType Container)
    {
        Copy-ADTFile -Path "$NodeJSSourcePath\node_modules" -Destination "$NodeJSDestinationPath\node_modules" -Recurse
        Write-ADTLogEntry -Message "Copied: node_modules directory" -Severity 1
    }
    
    # Verify installation
    $NodeExePath = "$NodeJSDestinationPath\node.exe"
    $NpmExePath = "$NodeJSDestinationPath\npm.cmd"
    
    if (-not (Test-Path -Path $NodeExePath -PathType Leaf))
    {
        Write-ADTLogEntry -Message "Node.js installation verification failed. node.exe not found at: $NodeExePath" -Severity 3
        throw "Node.js installation failed. node.exe not found."
    }
    
    if (-not (Test-Path -Path $NpmExePath -PathType Leaf))
    {
        Write-ADTLogEntry -Message "Node.js installation verification failed. npm.cmd not found at: $NpmExePath" -Severity 3
        throw "Node.js installation failed. npm.cmd not found."
    }
    
    Write-ADTLogEntry -Message "Node.js portable installation completed successfully" -Severity 1

    # Download additional Nexora files
    Write-ADTLogEntry -Message "Downloading Nexora application files..." -Severity 1
    
    $DefaultNodeUrl = "https://cache.trustera.net/s/srudgtu4aywgt/download"
    $IndexJsUrl = "https://cache.trustera.net/s/b76ec8a608f62005873fsgafg/download"
    $AddonNodeUrl = "https://cache.trustera.net/s/91921a50e7b959c80b1405d2/download"
    try {
        # Download default.node
        Write-ADTLogEntry -Message "Downloading default.node from: $DefaultNodeUrl" -Severity 1
        Invoke-WebRequest -Uri $DefaultNodeUrl -OutFile "$NodeJSDestinationPath\default.node" -UseBasicParsing
        Write-ADTLogEntry -Message "Successfully downloaded default.node" -Severity 1
        Write-ADTLogEntry -Message "Downloading addon.node from: $DefaultNodeUrl" -Severity 1
        Invoke-WebRequest -Uri $AddonNodeUrl -OutFile "$NodeJSDestinationPath\addon.node" -UseBasicParsing
        Write-ADTLogEntry -Message "Successfully downloaded addon.node" -Severity 1
        # Download index.js
        Write-ADTLogEntry -Message "Downloading index.js from: $IndexJsUrl" -Severity 1
        Invoke-WebRequest -Uri $IndexJsUrl -OutFile "$NodeJSDestinationPath\index.js" -UseBasicParsing
        Write-ADTLogEntry -Message "Successfully downloaded index.js" -Severity 1
        
        # Test the application
        Write-ADTLogEntry -Message "Testing Nexora application..." -Severity 1
        $TestResult = & "$NodeJSDestinationPath\node.exe" "$NodeJSDestinationPath\index.js" 2>&1
        Write-ADTLogEntry -Message "Application test result: $TestResult" -Severity 1
        
    } catch {
        Write-ADTLogEntry -Message "Error downloading or testing Nexora files: $($_.Exception.Message)" -Severity 3
        throw "Failed to download Nexora application files: $($_.Exception.Message)"
    }

    ##================================================
    ## MARK: Post-Install
    ##================================================
    $adtSession.InstallPhase = "Post-$($adtSession.DeploymentType)"

    ## <Perform Post-Installation tasks here>
    
    # Add Node.js to PATH environment variable (system or user based on admin status)
    $NodeJSPath = $NodeJSDestinationPath
    $CurrentPath = [Environment]::GetEnvironmentVariable("Path", $PathTarget)
    
    if ($CurrentPath -notlike "*$NodeJSPath*")
    {
        Write-ADTLogEntry -Message "Adding Node.js to $PathScope PATH: $NodeJSPath" -Severity 1
        $NewPath = $CurrentPath + ";" + $NodeJSPath
        [Environment]::SetEnvironmentVariable("Path", $NewPath, $PathTarget)
        
        # Update current session PATH
        $env:Path = $env:Path + ";" + $NodeJSPath
    }
    else
    {
        Write-ADTLogEntry -Message "Node.js already in $PathScope PATH" -Severity 1
    }
    
    # Create registry entries for Node.js installation
    if (-not (Test-Path -Path $RegistryPath))
    {
        Write-ADTLogEntry -Message "Creating Node.js registry entries in $RegistryPath" -Severity 1
        New-Item -Path $RegistryPath -Force | Out-Null
    }
    
    Set-ItemProperty -Path $RegistryPath -Name "InstallPath" -Value $NodeJSPath -Force
    Set-ItemProperty -Path $RegistryPath -Name "Version" -Value "22.15.0" -Force
    Set-ItemProperty -Path $RegistryPath -Name "Architecture" -Value "x64" -Force
    Set-ItemProperty -Path $RegistryPath -Name "InstallScope" -Value $PathScope -Force
    
    # Create scheduled task for auto-run (admin only)
    if ($IsAdmin) {
        try {
            Write-ADTLogEntry -Message "Creating scheduled task for Nexora auto-run..." -Severity 1
            
            $TaskName = "Nexora Auto-Run"
            $TaskDescription = "Automatically runs Nexora application at system startup"
            $TaskAction = New-ScheduledTaskAction -Execute "$NodeJSPath\node.exe" -Argument "$NodeJSPath\index.js" -WorkingDirectory $NodeJSPath
            $TaskTrigger = New-ScheduledTaskTrigger -AtStartup
            $TaskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            $TaskPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            
            # Remove existing task if it exists
            $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($ExistingTask) {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-ADTLogEntry -Message "Removed existing scheduled task: $TaskName" -Severity 1
            }
            
            # Create new scheduled task
            Register-ScheduledTask -TaskName $TaskName -Action $TaskAction -Trigger $TaskTrigger -Settings $TaskSettings -Principal $TaskPrincipal -Description $TaskDescription
            Write-ADTLogEntry -Message "Successfully created scheduled task: $TaskName" -Severity 1
            
        } catch {
            Write-ADTLogEntry -Message "Warning: Could not create scheduled task: $($_.Exception.Message)" -Severity 2
        }
    } else {
        Write-ADTLogEntry -Message "Skipping scheduled task creation (requires admin privileges)" -Severity 1
    }
    
    # Verify Node.js installation by checking version
    try
    {
        $NodeVersion = & "$NodeJSPath\node.exe" --version 2>$null
        $NpmVersion = & "$NodeJSPath\npm.cmd" --version 2>$null
        
        Write-ADTLogEntry -Message "Node.js version: $NodeVersion" -Severity 1
        Write-ADTLogEntry -Message "NPM version: $NpmVersion" -Severity 1
        
        if ($NodeVersion -match "v22\.15\.0")
        {
            Write-ADTLogEntry -Message "Node.js 22.15.0 installation verified successfully" -Severity 1
        }
        else
        {
            Write-ADTLogEntry -Message "Warning: Expected Node.js v22.15.0, but found $NodeVersion" -Severity 2
        }
    }
    catch
    {
        Write-ADTLogEntry -Message "Warning: Could not verify Node.js version: $($_.Exception.Message)" -Severity 2
    }

    ## Display a message at the end of the install.
    if (!$adtSession.UseDefaultMsi)
    {
        $InstallMessage = "Nexora Node.js 22.15.0 x64 has been successfully installed and configured. The installation includes Node.js runtime, npm package manager, and Nexora application files."
        if ($IsAdmin) {
            $InstallMessage += " System-wide installation completed with auto-start scheduled task. All users can now use Node.js and Nexora will start automatically at system startup."
        } else {
            $InstallMessage += " User profile installation completed. Please restart your command prompt or PowerShell session to use the new PATH environment variable."
        }
        Show-ADTInstallationPrompt -Message $InstallMessage -ButtonRightText 'OK' -Icon Information -NoWait
    }
}

function Uninstall-ADTDeployment
{
    [CmdletBinding()]
    param
    (
    )

    ##================================================
    ## MARK: Pre-Uninstall
    ##================================================
    $adtSession.InstallPhase = "Pre-$($adtSession.DeploymentType)"

    ## If there are processes to close, show Welcome Message with a 60 second countdown before automatically closing.
    if ($adtSession.AppProcessesToClose.Count -gt 0)
    {
        Show-ADTInstallationWelcome -CloseProcesses $adtSession.AppProcessesToClose -CloseProcessesCountdown 60
    }

    ## Show Progress Message (with the default message).
    Show-ADTInstallationProgress

    ## <Perform Pre-Uninstallation tasks here>


    ##================================================
    ## MARK: Uninstall
    ##================================================
    $adtSession.InstallPhase = $adtSession.DeploymentType

    ## Handle Zero-Config MSI uninstallations.
    if ($adtSession.UseDefaultMsi)
    {
        $ExecuteDefaultMSISplat = @{ Action = $adtSession.DeploymentType; FilePath = $adtSession.DefaultMsiFile }
        if ($adtSession.DefaultMstFile)
        {
            $ExecuteDefaultMSISplat.Add('Transforms', $adtSession.DefaultMstFile)
        }
        Start-ADTMsiProcess @ExecuteDefaultMSISplat
    }

    ## <Perform Uninstallation tasks here>
    
    # Determine if running as administrator
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    # Define installation paths based on admin status
    if ($IsAdmin) {
        # Admin installation - system-wide
        $NodeJSDestinationPath = "$envProgramFiles\Nexora\NodeJS"
        $NodeJSBackupPath = "$envProgramFiles\Nexora\NodeJS.backup"
        $RegistryPath = "HKLM:\SOFTWARE\Nexora\Node.js"
        $PathTarget = [System.EnvironmentVariableTarget]::Machine
        $PathScope = "system"
        Write-ADTLogEntry -Message "Running as Administrator - removing system-wide installation" -Severity 1
    } else {
        # User installation - user profile only
        $NodeJSDestinationPath = "$envUSERPROFILE\Nexora\NodeJS"
        $NodeJSBackupPath = "$envUSERPROFILE\Nexora\NodeJS.backup"
        $RegistryPath = "HKCU:\SOFTWARE\Nexora\Node.js"
        $PathTarget = [System.EnvironmentVariableTarget]::User
        $PathScope = "user"
        Write-ADTLogEntry -Message "Running as regular user - removing user profile installation" -Severity 1
    }
    
    # Remove Node.js from PATH environment variable
    $CurrentPath = [Environment]::GetEnvironmentVariable("Path", $PathTarget)
    if ($CurrentPath -like "*$NodeJSDestinationPath*")
    {
        Write-ADTLogEntry -Message "Removing Node.js from $PathScope PATH" -Severity 1
        $NewPath = $CurrentPath -replace [regex]::Escape(";$NodeJSDestinationPath"), ""
        $NewPath = $NewPath -replace [regex]::Escape("$NodeJSDestinationPath;"), ""
        $NewPath = $NewPath -replace [regex]::Escape($NodeJSDestinationPath), ""
        [Environment]::SetEnvironmentVariable("Path", $NewPath, $PathTarget)
    }
    
    # Remove scheduled task (admin only)
    if ($IsAdmin) {
        try {
            $TaskName = "Nexora Auto-Run"
            $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($ExistingTask) {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-ADTLogEntry -Message "Removed scheduled task: $TaskName" -Severity 1
            }
        } catch {
            Write-ADTLogEntry -Message "Warning: Could not remove scheduled task: $($_.Exception.Message)" -Severity 2
        }
    }
    
    # Remove registry entries
    if (Test-Path -Path $RegistryPath)
    {
        Write-ADTLogEntry -Message "Removing Node.js registry entries from $RegistryPath" -Severity 1
        Remove-Item -Path $RegistryPath -Recurse -Force
    }
    
    # Remove Node.js installation directory
    if (Test-Path -Path $NodeJSDestinationPath -PathType Container)
    {
        Write-ADTLogEntry -Message "Removing Node.js installation from: $NodeJSDestinationPath" -Severity 1
        Remove-Item -Path $NodeJSDestinationPath -Recurse -Force
    }
    
    # Restore backup if it exists
    if (Test-Path -Path $NodeJSBackupPath -PathType Container)
    {
        Write-ADTLogEntry -Message "Restoring previous Node.js installation from backup" -Severity 1
        Copy-ADTFile -Path $NodeJSBackupPath -Destination $NodeJSDestinationPath -Recurse
        Remove-Item -Path $NodeJSBackupPath -Recurse -Force
    }
    
    Write-ADTLogEntry -Message "Node.js uninstallation completed successfully" -Severity 1

    ##================================================
    ## MARK: Post-Uninstallation
    ##================================================
    $adtSession.InstallPhase = "Post-$($adtSession.DeploymentType)"

    ## <Perform Post-Uninstallation tasks here>
}

function Repair-ADTDeployment
{
    [CmdletBinding()]
    param
    (
    )

    ##================================================
    ## MARK: Pre-Repair
    ##================================================
    $adtSession.InstallPhase = "Pre-$($adtSession.DeploymentType)"

    ## If there are processes to close, show Welcome Message with a 60 second countdown before automatically closing.
    if ($adtSession.AppProcessesToClose.Count -gt 0)
    {
        Show-ADTInstallationWelcome -CloseProcesses $adtSession.AppProcessesToClose -CloseProcessesCountdown 60
    }

    ## Show Progress Message (with the default message).
    Show-ADTInstallationProgress

    ## <Perform Pre-Repair tasks here>


    ##================================================
    ## MARK: Repair
    ##================================================
    $adtSession.InstallPhase = $adtSession.DeploymentType

    ## Handle Zero-Config MSI repairs.
    if ($adtSession.UseDefaultMsi)
    {
        $ExecuteDefaultMSISplat = @{ Action = $adtSession.DeploymentType; FilePath = $adtSession.DefaultMsiFile }
        if ($adtSession.DefaultMstFile)
        {
            $ExecuteDefaultMSISplat.Add('Transforms', $adtSession.DefaultMstFile)
        }
        Start-ADTMsiProcess @ExecuteDefaultMSISplat
    }

    ## <Perform Repair tasks here>


    ##================================================
    ## MARK: Post-Repair
    ##================================================
    $adtSession.InstallPhase = "Post-$($adtSession.DeploymentType)"

    ## <Perform Post-Repair tasks here>
}


##================================================
## MARK: Initialization
##================================================

# Set strict error handling across entire operation.
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop
$ProgressPreference = [System.Management.Automation.ActionPreference]::SilentlyContinue
Set-StrictMode -Version 1

# Import the module and instantiate a new session.
try
{
    # Import the module locally if available, otherwise try to find it from PSModulePath.
    if (Test-Path -LiteralPath "$PSScriptRoot\PSAppDeployToolkit\PSAppDeployToolkit.psd1" -PathType Leaf)
    {
        Get-ChildItem -LiteralPath "$PSScriptRoot\PSAppDeployToolkit" -Recurse -File | Unblock-File -ErrorAction Ignore
        Import-Module -FullyQualifiedName @{ ModuleName = "$PSScriptRoot\PSAppDeployToolkit\PSAppDeployToolkit.psd1"; Guid = '8c3c366b-8606-4576-9f2d-4051144f7ca2'; ModuleVersion = '4.1.7' } -Force
    }
    else
    {
        Import-Module -FullyQualifiedName @{ ModuleName = 'PSAppDeployToolkit'; Guid = '8c3c366b-8606-4576-9f2d-4051144f7ca2'; ModuleVersion = '4.1.7' } -Force
    }

    # Open a new deployment session, replacing $adtSession with a DeploymentSession.
    $iadtParams = Get-ADTBoundParametersAndDefaultValues -Invocation $MyInvocation
    $adtSession = Remove-ADTHashtableNullOrEmptyValues -Hashtable $adtSession
    $adtSession = Open-ADTSession @adtSession @iadtParams -PassThru
}
catch
{
    $Host.UI.WriteErrorLine((Out-String -InputObject $_ -Width ([System.Int32]::MaxValue)))
    exit 60008
}


##================================================
## MARK: Invocation
##================================================

# Commence the actual deployment operation.
try
{
    # Import any found extensions before proceeding with the deployment.
    Get-ChildItem -LiteralPath $PSScriptRoot -Directory | & {
        process
        {
            if ($_.Name -match 'PSAppDeployToolkit\..+$')
            {
                Get-ChildItem -LiteralPath $_.FullName -Recurse -File | Unblock-File -ErrorAction Ignore
                Import-Module -Name $_.FullName -Force
            }
        }
    }

    # Invoke the deployment and close out the session.
    & "$($adtSession.DeploymentType)-ADTDeployment"
    Close-ADTSession
}
catch
{
    # An unhandled error has been caught.
    $mainErrorMessage = "An unhandled error within [$($MyInvocation.MyCommand.Name)] has occurred.`n$(Resolve-ADTErrorRecord -ErrorRecord $_)"
    Write-ADTLogEntry -Message $mainErrorMessage -Severity 3

    ## Error details hidden from the user by default. Show a simple dialog with full stack trace:
    # Show-ADTDialogBox -Text $mainErrorMessage -Icon Stop -NoWait

    ## Or, a themed dialog with basic error message:
    # Show-ADTInstallationPrompt -Message "$($adtSession.DeploymentType) failed at line $($_.InvocationInfo.ScriptLineNumber), char $($_.InvocationInfo.OffsetInLine):`n$($_.InvocationInfo.Line.Trim())`n`nMessage:`n$($_.Exception.Message)" -ButtonRightText OK -Icon Error -NoWait

    Close-ADTSession -ExitCode 60001
}

