"""
PowerShell Script Editor Module
Handles editing and version management of PowerShell scripts
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from .ps1_parser import PS1Parser, ScriptParameter, ScriptSection


class PowerShellEditor:
    """Manages PowerShell script editing and versioning."""

    def __init__(self, script_path: str):
        """
        Initialize PowerShell Editor.

        Args:
            script_path: Path to the PowerShell script

        Raises:
            FileNotFoundError: If script file doesn't exist
        """
        self.script_path = Path(script_path)

        if not self.script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        self.versions_dir = self.script_path.parent / ".versions" / self.script_path.stem
        self.versions_dir.mkdir(parents=True, exist_ok=True)

        self.parser: Optional[PS1Parser] = None
        self._load_parser()

    def read_script(self) -> str:
        """
        Read the current script content.

        Returns:
            Script content as string
        """
        with open(self.script_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_script(self, content: str, create_backup: bool = True) -> str:
        """
        Write content to the script file.

        Args:
            content: New script content
            create_backup: Whether to create a backup before writing

        Returns:
            Path to the backup file if created, empty string otherwise
        """
        backup_path = ""

        if create_backup:
            backup_path = self.create_version("auto_backup")

        with open(self.script_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

        return backup_path

    def create_version(self, version_name: Optional[str] = None) -> str:
        """
        Create a versioned copy of the script.

        Args:
            version_name: Optional name for the version

        Returns:
            Path to the created version file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if version_name:
            version_filename = f"{self.script_path.stem}_{version_name}_{timestamp}.ps1"
        else:
            version_filename = f"{self.script_path.stem}_{timestamp}.ps1"

        version_path = self.versions_dir / version_filename

        shutil.copy2(self.script_path, version_path)

        return str(version_path)

    def list_versions(self) -> List[dict]:
        """
        List all available versions of the script.

        Returns:
            List of dictionaries with version information
        """
        versions = []

        if not self.versions_dir.exists():
            return versions

        for version_file in sorted(self.versions_dir.glob("*.ps1"), reverse=True):
            stat = version_file.stat()
            versions.append({
                'name': version_file.name,
                'path': str(version_file),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime)
            })

        return versions

    def restore_version(self, version_path: str, create_backup: bool = True) -> bool:
        """
        Restore a specific version of the script.

        Args:
            version_path: Path to the version to restore
            create_backup: Whether to create a backup before restoring

        Returns:
            True if restoration was successful

        Raises:
            FileNotFoundError: If version file doesn't exist
        """
        version_file = Path(version_path)

        if not version_file.exists():
            raise FileNotFoundError(f"Version file not found: {version_path}")

        if create_backup:
            self.create_version("before_restore")

        shutil.copy2(version_file, self.script_path)

        return True

    def delete_version(self, version_path: str) -> bool:
        """
        Delete a specific version.

        Args:
            version_path: Path to the version to delete

        Returns:
            True if deletion was successful
        """
        version_file = Path(version_path)

        if version_file.exists():
            version_file.unlink()
            return True

        return False

    def find_and_replace(self, find_text: str, replace_text: str,
                        case_sensitive: bool = True,
                        create_backup: bool = True) -> int:
        """
        Find and replace text in the script.

        Args:
            find_text: Text to find
            replace_text: Text to replace with
            case_sensitive: Whether search is case-sensitive
            create_backup: Whether to create a backup before replacing

        Returns:
            Number of replacements made
        """
        content = self.read_script()

        if case_sensitive:
            count = content.count(find_text)
            new_content = content.replace(find_text, replace_text)
        else:
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(find_text), re.IGNORECASE)
            count = len(pattern.findall(content))
            new_content = pattern.sub(replace_text, content)

        if count > 0:
            self.write_script(new_content, create_backup=create_backup)

        return count

    def get_script_info(self) -> dict:
        """
        Get information about the script.

        Returns:
            Dictionary with script information
        """
        stat = self.script_path.stat()

        return {
            'name': self.script_path.name,
            'path': str(self.script_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'versions_count': len(self.list_versions()),
            'versions_dir': str(self.versions_dir)
        }

    def cleanup_old_versions(self, keep_count: int = 10) -> int:
        """
        Clean up old versions, keeping only the most recent ones.

        Args:
            keep_count: Number of versions to keep

        Returns:
            Number of versions deleted
        """
        versions = self.list_versions()

        if len(versions) <= keep_count:
            return 0

        deleted_count = 0
        for version in versions[keep_count:]:
            if self.delete_version(version['path']):
                deleted_count += 1

        return deleted_count

    def _load_parser(self):
        """Load the parser with current script content."""
        content = self.read_script()
        self.parser = PS1Parser(content)
        self.parser.parse()

    def get_parameters(self) -> List[ScriptParameter]:
        """
        Get all configurable parameters from the script.

        Returns:
            List of ScriptParameter objects
        """
        if not self.parser:
            self._load_parser()
        return self.parser.parameters

    def get_sections(self) -> List[ScriptSection]:
        """
        Get all sections/phases from the script.

        Returns:
            List of ScriptSection objects
        """
        if not self.parser:
            self._load_parser()
        return self.parser.sections

    def get_urls(self) -> List[ScriptParameter]:
        """
        Get all URL parameters from the script.

        Returns:
            List of URL ScriptParameter objects
        """
        if not self.parser:
            self._load_parser()
        return self.parser.get_all_urls()

    def update_parameter(self, param_name: str, new_value: str, create_backup: bool = True) -> bool:
        """
        Update a specific parameter value.

        Args:
            param_name: Name of the parameter to update
            new_value: New value for the parameter
            create_backup: Whether to create a backup before updating

        Returns:
            True if parameter was updated successfully
        """
        if not self.parser:
            self._load_parser()

        if self.parser.update_parameter(param_name, new_value):
            modified_content = self.parser.get_modified_content()
            self.write_script(modified_content, create_backup=create_backup)
            self._load_parser()  # Reload parser with updated content
            return True

        return False

    def toggle_section(self, section_name: str, enabled: bool, create_backup: bool = True) -> bool:
        """
        Enable or disable a deployment section.

        Args:
            section_name: Name of the section to toggle
            enabled: True to enable, False to disable
            create_backup: Whether to create a backup before toggling

        Returns:
            True if section was toggled successfully
        """
        if not self.parser:
            self._load_parser()

        if self.parser.toggle_section(section_name, enabled):
            modified_content = self.parser.get_modified_content()
            self.write_script(modified_content, create_backup=create_backup)
            self._load_parser()  # Reload parser with updated content
            return True

        return False

    def batch_update_parameters(self, updates: dict, create_backup: bool = True) -> dict:
        """
        Update multiple parameters at once.

        Args:
            updates: Dictionary of {param_name: new_value}
            create_backup: Whether to create a backup before updating

        Returns:
            Dictionary of {param_name: success_bool}
        """
        if not self.parser:
            self._load_parser()

        results = {}
        modified = False

        for param_name, new_value in updates.items():
            if self.parser.update_parameter(param_name, new_value):
                results[param_name] = True
                modified = True
            else:
                results[param_name] = False

        if modified:
            modified_content = self.parser.get_modified_content()
            self.write_script(modified_content, create_backup=create_backup)
            self._load_parser()  # Reload parser with updated content

        return results
