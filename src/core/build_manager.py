"""
Build Manager Module
Handles building Advanced Installer projects
"""
import subprocess
import os
import winreg
from pathlib import Path
from typing import Optional, Callable


class BuildManager:
    """Manages building of Advanced Installer projects."""

    DEFAULT_INSTALL_PATHS = [
        r"C:\Program Files (x86)\Caphyon\Advanced Installer",
        r"C:\Program Files\Caphyon\Advanced Installer",
    ]

    def __init__(self, advinst_path: Optional[str] = None):
        """
        Initialize Build Manager.

        Args:
            advinst_path: Path to Advanced Installer executable
                         If None, will attempt to auto-detect
        """
        self.advinst_path = advinst_path
        if not self.advinst_path:
            self.advinst_path = self._find_advanced_installer()

    def _find_advanced_installer(self) -> Optional[str]:
        """
        Try to find Advanced Installer installation automatically.

        Returns:
            Path to AdvancedInstaller.com or None if not found
        """
        # Try to find in registry (Windows)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Caphyon\Advanced Installer",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_32KEY
            )
            install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
            winreg.CloseKey(key)

            advinst_exe = os.path.join(install_dir, "bin", "x86", "AdvancedInstaller.com")
            if os.path.exists(advinst_exe):
                return advinst_exe
        except Exception:
            pass

        # Try default installation paths
        for base_path in self.DEFAULT_INSTALL_PATHS:
            # Try to find the latest version
            if os.path.exists(base_path):
                for version_dir in sorted(os.listdir(base_path), reverse=True):
                    advinst_exe = os.path.join(
                        base_path,
                        version_dir,
                        "bin",
                        "x86",
                        "AdvancedInstaller.com"
                    )
                    if os.path.exists(advinst_exe):
                        return advinst_exe

        return None

    def is_advanced_installer_available(self) -> bool:
        """
        Check if Advanced Installer is available.

        Returns:
            True if Advanced Installer executable is found
        """
        return self.advinst_path is not None and os.path.exists(self.advinst_path)

    def set_advanced_installer_path(self, path: str):
        """
        Manually set the path to Advanced Installer.

        Args:
            path: Path to AdvancedInstaller.com

        Raises:
            FileNotFoundError: If the specified file doesn't exist
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Advanced Installer not found at: {path}")

        self.advinst_path = path

    def build_project(self, aip_file: str,
                     output_folder: Optional[str] = None,
                     build_name: str = "DefaultBuild",
                     callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Build an Advanced Installer project.

        Args:
            aip_file: Path to the .aip file
            output_folder: Optional output folder for the build
            build_name: Name of the build configuration (default: "DefaultBuild")
            callback: Optional callback function for output messages

        Returns:
            True if build succeeded, False otherwise

        Raises:
            FileNotFoundError: If AIP file or Advanced Installer not found
            RuntimeError: If Advanced Installer is not available
        """
        if not os.path.exists(aip_file):
            raise FileNotFoundError(f"AIP file not found: {aip_file}")

        if not self.is_advanced_installer_available():
            raise RuntimeError(
                "Advanced Installer not found. Please set the path manually using "
                "set_advanced_installer_path()"
            )

        # Build command
        cmd = [
            self.advinst_path,
            "/rebuild",
            aip_file
        ]

        if output_folder:
            cmd.extend(["/out", output_folder])

        if build_name:
            cmd.extend(["/build", build_name])

        # Execute build
        try:
            if callback:
                callback(f"Starting build: {' '.join(cmd)}\n")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Stream output
            for line in process.stdout:
                if callback:
                    callback(line)

            # Wait for completion
            return_code = process.wait()

            # Check for errors
            if return_code != 0:
                stderr = process.stderr.read()
                if callback:
                    callback(f"\nBuild failed with return code {return_code}\n")
                    callback(f"Error: {stderr}\n")
                return False

            if callback:
                callback("\nBuild completed successfully!\n")

            return True

        except Exception as e:
            if callback:
                callback(f"\nException during build: {str(e)}\n")
            return False

    def get_build_info(self, aip_file: str) -> dict:
        """
        Get information about available builds in a project.

        Args:
            aip_file: Path to the .aip file

        Returns:
            Dictionary with build information
        """
        # This is a simplified version - actual implementation would parse the AIP file
        # to get all build configurations
        return {
            'default_build': 'DefaultBuild',
            'aip_file': aip_file,
            'advinst_available': self.is_advanced_installer_available(),
            'advinst_path': self.advinst_path
        }
