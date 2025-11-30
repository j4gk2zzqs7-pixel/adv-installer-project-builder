#!/usr/bin/env python3
"""
Quick test script for PS1 Parser
"""
from src.utils.ps1_parser import PS1Parser

# Test with the example script
script_path = 'Invoke-AppDeployToolkit.ps1'

print("Testing PS1 Parser...")
print("=" * 60)

try:
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = PS1Parser(content)
    parser.parse()

    print(f"\n✓ Successfully parsed {script_path}")
    print(f"  Found {len(parser.parameters)} parameters")
    print(f"  Found {len(parser.urls)} URLs")
    print(f"  Found {len(parser.sections)} sections")

    print("\n--- Session Variables ---")
    session_vars = [p for p in parser.parameters if p.section == 'variables' and p.parameter_type != 'url']
    for param in session_vars[:5]:  # Show first 5
        print(f"  {param.name} = {param.value} ({param.parameter_type})")
    if len(session_vars) > 5:
        print(f"  ... and {len(session_vars) - 5} more")

    print("\n--- URLs ---")
    for url in parser.urls:
        print(f"  {url.name} = {url.value}")

    print("\n--- Sections ---")
    for section in parser.sections:
        status = "✓ Enabled" if section.enabled else "✗ Disabled"
        print(f"  [{status}] {section.name} - {section.description}")

    print("\n--- Testing Parameter Update ---")
    test_param = "AppVendor"
    old_value = parser.find_parameter(test_param).value if parser.find_parameter(test_param) else "N/A"
    print(f"  Current {test_param}: {old_value}")

    if parser.update_parameter(test_param, "TestVendor"):
        new_value = parser.find_parameter(test_param).value
        print(f"  ✓ Updated {test_param} to: {new_value}")
    else:
        print(f"  ✗ Failed to update {test_param}")

    print("\n✓ All tests passed!")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
