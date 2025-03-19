"""
Setup script for the Arcade Station Installer
"""
from setuptools import setup, find_packages

setup(
    name="arcade-station-installer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pillow",  # For image handling
    ],
    entry_points={
        "console_scripts": [
            "arcade-station-installer=arcade_station_installer.main:main",
        ],
    },
    author="Arcade Station Team",
    author_email="info@arcadestation.example.com",
    description="Installer for Arcade Station game launcher",
    keywords="arcade, games, installer",
    python_requires=">=3.12.9",
) 