"""
PowerShell Script Parser and Editor
Extracts and modifies configurable parameters in PS1 scripts
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ScriptParameter:
    """Represents a configurable parameter in the script."""
    name: str
    value: str
    line_number: int
    parameter_type: str  # 'string', 'number', 'array', 'boolean', 'url'
    section: str  # 'variables', 'install', 'post-install', etc.


@dataclass
class ScriptSection:
    """Represents a section/phase in the script."""
    name: str
    start_line: int
    end_line: int
    enabled: bool
    description: str


class PS1Parser:
    """Parser for PowerShell deployment scripts."""

    def __init__(self, script_content: str):
        """
        Initialize parser with script content.

        Args:
            script_content: Full content of the PS1 script
        """
        self.content = script_content
        self.lines = script_content.split('\n')
        self.parameters: List[ScriptParameter] = []
        self.sections: List[ScriptSection] = []
        self.urls: List[ScriptParameter] = []

    def parse(self):
        """Parse the script and extract all configurable parameters."""
        self._parse_session_variables()
        self._parse_urls()
        self._parse_sections()

    def _parse_session_variables(self):
        """Extract variables from $adtSession hashtable."""
        in_session_block = False

        for i, line in enumerate(self.lines):
            # Detect start of $adtSession block
            if re.match(r'^\$adtSession\s*=\s*@\{', line):
                in_session_block = True
                continue

            # Detect end of hashtable
            if in_session_block and line.strip() == '}':
                in_session_block = False
                continue

            # Parse parameters within the block
            if in_session_block:
                param = self._parse_variable_line(line, i, 'variables')
                if param:
                    self.parameters.append(param)

    def _parse_variable_line(self, line: str, line_number: int, section: str) -> Optional[ScriptParameter]:
        """Parse a single variable assignment line."""
        # Match patterns like: AppVendor = 'NexoraDev'
        string_match = re.match(r'\s*(\w+)\s*=\s*[\'"]([^\'"]*)[\'"]', line)
        if string_match:
            name, value = string_match.groups()
            return ScriptParameter(
                name=name,
                value=value,
                line_number=line_number,
                parameter_type='string',
                section=section
            )

        # Match numbers: AppSuccessExitCodes = @(0)
        number_match = re.match(r'\s*(\w+)\s*=\s*(\d+)', line)
        if number_match:
            name, value = number_match.groups()
            return ScriptParameter(
                name=name,
                value=value,
                line_number=line_number,
                parameter_type='number',
                section=section
            )

        # Match arrays: AppProcessesToClose = @('node', 'npm')
        array_match = re.match(r'\s*(\w+)\s*=\s*@\((.*?)\)', line)
        if array_match:
            name, value = array_match.groups()
            return ScriptParameter(
                name=name,
                value=value,
                line_number=line_number,
                parameter_type='array',
                section=section
            )

        # Match boolean: RequireAdmin = $false
        bool_match = re.match(r'\s*(\w+)\s*=\s*\$(true|false)', line, re.IGNORECASE)
        if bool_match:
            name, value = bool_match.groups()
            return ScriptParameter(
                name=name,
                value=value,
                line_number=line_number,
                parameter_type='boolean',
                section=section
            )

        return None

    def _parse_urls(self):
        """Extract all URLs from the script."""
        url_pattern = re.compile(r'(\$\w+)\s*=\s*[\'"]((https?://|ftp://)[^\'"]+)[\'"]')

        for i, line in enumerate(self.lines):
            match = url_pattern.search(line)
            if match:
                var_name = match.group(1)
                url = match.group(2)

                param = ScriptParameter(
                    name=var_name,
                    value=url,
                    line_number=i,
                    parameter_type='url',
                    section='install'
                )
                self.urls.append(param)
                self.parameters.append(param)

    def _parse_sections(self):
        """Parse deployment sections/phases."""
        section_patterns = [
            (r'##\s*MARK:\s*Pre-Install', 'Pre-Install', 'Предварительная установка'),
            (r'##\s*MARK:\s*Install\s*$', 'Install', 'Основная установка'),
            (r'##\s*MARK:\s*Post-Install', 'Post-Install', 'Завершение установки'),
            (r'##\s*MARK:\s*Pre-Uninstall', 'Pre-Uninstall', 'Подготовка к удалению'),
            (r'##\s*MARK:\s*Uninstall\s*$', 'Uninstall', 'Удаление'),
            (r'##\s*MARK:\s*Post-Uninstall', 'Post-Uninstall', 'Завершение удаления'),
        ]

        for pattern, name, description in section_patterns:
            matches = [(i, line) for i, line in enumerate(self.lines) if re.search(pattern, line)]

            for i, line in matches:
                # Find the end of this section (next ## MARK or end of function)
                end_line = self._find_section_end(i)

                # Check if section is enabled (not commented out)
                enabled = self._is_section_enabled(i, end_line)

                section = ScriptSection(
                    name=name,
                    start_line=i,
                    end_line=end_line,
                    enabled=enabled,
                    description=description
                )
                self.sections.append(section)

    def _find_section_end(self, start_line: int) -> int:
        """Find the end line of a section."""
        # Look for next ## MARK or end of function
        for i in range(start_line + 1, len(self.lines)):
            line = self.lines[i]
            if re.search(r'##\s*MARK:', line):
                return i - 1
            if line.strip().startswith('}') and i > start_line + 5:
                # Likely end of function, but check context
                return i

        return len(self.lines) - 1

    def _is_section_enabled(self, start_line: int, end_line: int) -> bool:
        """Check if a section is enabled (not commented out)."""
        # Check if majority of lines in section are not commented
        commented_count = 0
        total_count = 0

        for i in range(start_line, min(end_line, start_line + 10)):
            line = self.lines[i].strip()
            if line and not line.startswith('##'):
                total_count += 1
                if line.startswith('#'):
                    commented_count += 1

        if total_count == 0:
            return True

        return commented_count < total_count / 2

    def update_parameter(self, param_name: str, new_value: str) -> bool:
        """
        Update a parameter value.

        Args:
            param_name: Name of the parameter to update
            new_value: New value for the parameter

        Returns:
            True if parameter was updated
        """
        for param in self.parameters:
            if param.name == param_name or param.name == f'${param_name}':
                line_number = param.line_number
                old_line = self.lines[line_number]

                # Update based on parameter type
                if param.parameter_type == 'string' or param.parameter_type == 'url':
                    # Replace the value between quotes
                    new_line = re.sub(
                        r'([\'"]).*?([\'"])',
                        f"'{new_value}'",
                        old_line,
                        count=1
                    )
                elif param.parameter_type == 'number':
                    new_line = re.sub(
                        r'=\s*\d+',
                        f'= {new_value}',
                        old_line
                    )
                elif param.parameter_type == 'array':
                    new_line = re.sub(
                        r'@\((.*?)\)',
                        f'@({new_value})',
                        old_line
                    )
                elif param.parameter_type == 'boolean':
                    new_line = re.sub(
                        r'\$(true|false)',
                        f'${new_value}',
                        old_line,
                        flags=re.IGNORECASE
                    )
                else:
                    continue

                self.lines[line_number] = new_line
                param.value = new_value
                return True

        return False

    def toggle_section(self, section_name: str, enabled: bool) -> bool:
        """
        Enable or disable a section by commenting/uncommenting.

        Args:
            section_name: Name of the section to toggle
            enabled: True to enable, False to disable

        Returns:
            True if section was toggled
        """
        for section in self.sections:
            if section.name == section_name:
                if enabled and not section.enabled:
                    # Uncomment the section
                    self._uncomment_section(section.start_line, section.end_line)
                    section.enabled = True
                    return True
                elif not enabled and section.enabled:
                    # Comment out the section
                    self._comment_section(section.start_line, section.end_line)
                    section.enabled = False
                    return True

        return False

    def _comment_section(self, start_line: int, end_line: int):
        """Comment out a section."""
        for i in range(start_line, end_line + 1):
            line = self.lines[i]
            # Skip lines that are already comments or MARK comments
            if not line.strip().startswith('#'):
                self.lines[i] = '    # ' + line

    def _uncomment_section(self, start_line: int, end_line: int):
        """Uncomment a section."""
        for i in range(start_line, end_line + 1):
            line = self.lines[i]
            # Remove comment prefix but preserve MARK comments
            if line.strip().startswith('#') and '## MARK:' not in line:
                self.lines[i] = re.sub(r'^\s*#\s?', '', line)

    def get_modified_content(self) -> str:
        """Get the modified script content."""
        return '\n'.join(self.lines)

    def get_parameters_by_section(self, section: str) -> List[ScriptParameter]:
        """Get all parameters for a specific section."""
        return [p for p in self.parameters if p.section == section]

    def get_all_urls(self) -> List[ScriptParameter]:
        """Get all URL parameters."""
        return self.urls

    def find_parameter(self, param_name: str) -> Optional[ScriptParameter]:
        """Find a parameter by name."""
        for param in self.parameters:
            if param.name == param_name or param.name == f'${param_name}':
                return param
        return None
