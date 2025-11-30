"""
Advanced Installer Project (.aip) Manager
Handles reading, modifying, and saving AIP files (XML format)
"""
import xml.etree.ElementTree as ET
import os
import shutil
from typing import Optional, Dict, Any
from pathlib import Path


class AIPManager:
    """Manages Advanced Installer Project files."""

    def __init__(self, aip_file_path: str):
        """
        Initialize AIP Manager.

        Args:
            aip_file_path: Path to the .aip file
        """
        self.aip_file_path = Path(aip_file_path)
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.backup_path: Optional[Path] = None

        if not self.aip_file_path.exists():
            raise FileNotFoundError(f"AIP file not found: {aip_file_path}")

        self._load_project()

    def _load_project(self):
        """Load the AIP XML file."""
        try:
            self.tree = ET.parse(self.aip_file_path)
            self.root = self.tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse AIP file: {e}")

    def create_backup(self) -> str:
        """
        Create a backup of the original AIP file.

        Returns:
            Path to the backup file
        """
        backup_path = self.aip_file_path.with_suffix('.aip.backup')
        shutil.copy2(self.aip_file_path, backup_path)
        self.backup_path = backup_path
        return str(backup_path)

    def get_property(self, property_name: str) -> Optional[str]:
        """
        Get a property value from the AIP file.

        Args:
            property_name: Name of the property (e.g., 'ProductName', 'Manufacturer')

        Returns:
            Property value or None if not found
        """
        # Find the property in the XML
        for row in self.root.findall(".//ROW[@Property='" + property_name + "']"):
            return row.get('Value')
        return None

    def set_property(self, property_name: str, value: str) -> bool:
        """
        Set a property value in the AIP file.

        Args:
            property_name: Name of the property
            value: New value for the property

        Returns:
            True if property was found and updated, False otherwise
        """
        for row in self.root.findall(".//ROW[@Property='" + property_name + "']"):
            row.set('Value', value)
            return True
        return False

    def update_project_info(self, product_name: Optional[str] = None,
                          manufacturer: Optional[str] = None,
                          version: Optional[str] = None) -> Dict[str, bool]:
        """
        Update project information.

        Args:
            product_name: New product name
            manufacturer: New manufacturer name
            version: New version string

        Returns:
            Dictionary with update status for each field
        """
        results = {}

        if product_name is not None:
            results['ProductName'] = self.set_property('ProductName', product_name)
            # Also update AI_PRODUCTNAME_ARP
            self.set_property('AI_PRODUCTNAME_ARP', f'[|{product_name}]')

        if manufacturer is not None:
            results['Manufacturer'] = self.set_property('Manufacturer', manufacturer)

        if version is not None:
            results['ProductVersion'] = self.set_property('ProductVersion', version)

        return results

    def update_icon(self, icon_bmp_path: str) -> bool:
        """
        Update the application icon reference in the AIP file.

        Args:
            icon_bmp_path: Path to the new .bmp icon file

        Returns:
            True if icon was updated successfully
        """
        icon_name = os.path.basename(icon_bmp_path)

        # Update AppLogoIcon property
        for row in self.root.findall(".//ROW[@Property='AppLogoIcon']"):
            row.set('MultiBuildValue', f'DefaultBuild:{icon_name}')
            return True

        return False

    def save(self, output_path: Optional[str] = None):
        """
        Save the modified AIP file.

        Args:
            output_path: Optional path to save to (defaults to original file)
        """
        if output_path is None:
            output_path = self.aip_file_path

        # Ensure proper XML declaration and formatting
        self.tree.write(
            output_path,
            encoding='UTF-8',
            xml_declaration=True,
            method='xml'
        )

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get current project information.

        Returns:
            Dictionary with project details
        """
        return {
            'ProductName': self.get_property('ProductName'),
            'Manufacturer': self.get_property('Manufacturer'),
            'ProductVersion': self.get_property('ProductVersion'),
            'UpgradeCode': self.get_property('UpgradeCode'),
            'ProductCode': self.get_property('ProductCode'),
        }

    def restore_from_backup(self):
        """Restore the AIP file from backup."""
        if self.backup_path and self.backup_path.exists():
            shutil.copy2(self.backup_path, self.aip_file_path)
            self._load_project()
        else:
            raise FileNotFoundError("No backup file found")
