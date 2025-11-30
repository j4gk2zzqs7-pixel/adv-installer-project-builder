"""
Setup script for Advanced Installer Project Builder
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='adv-installer-project-builder',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='GUI tool for managing Advanced Installer projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/adv-installer-project-builder',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.8',
    install_requires=[
        'PyQt5>=5.15.0',
        'Pillow>=9.0.0',
        'pywin32>=305; platform_system=="Windows"',
    ],
    entry_points={
        'console_scripts': [
            'aip-builder=gui.main_window:main',
        ],
    },
    include_package_data=True,
)
