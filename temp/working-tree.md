arcade-station/
├── src/
│   ├── arcade_station/            # Primary Python package
│   │   ├── __init__.py
│   │   ├── core/                  # Core Python logic
│   │   ├── installer/             # Installer logic
│   │   ├── listeners/             # Event listeners
│   │   └── __main__.py            # Entry point
│   ├── pegasus_fe/                # Pegasus FE binary and configurations
│   │   ├── pegasus-fe             # Compiled Pegasus FE binary
│   │   ├── config/                # Configuration files for Pegasus FE
│   │   │   ├── settings.conf      # Example config file for Pegasus FE
│   │   │   ├── game_library.conf  # Game library paths
│   │   │   └── README.md          # Documentation on configs
│   │   ├── themes/                # Pegasus FE themes (symlink or copy of `pegasus-themes`)
│   │   │   ├── micro/             # Example theme
│   │   │   │   ├── .meta/         # Metadata for the theme
│   │   │   │   ├── assets/        # Theme-specific assets
│   │   │   │   │   └── logos/
│   │   │   │   └── theme_config.toml
│   │   │   └── alternate_theme/
│   │   └── README.md              # Explains Pegasus FE usage in the project
├── pegasus-themes/                # Pegasus FE themes (for external reference/customization)
│   └── micro/
│       ├── .meta/                 # Metadata for the theme
│       ├── assets/                # Theme assets
│       └── theme_config.toml
├── assets/                        # General project assets
│   └── images/
├── config/                        # Project configuration files
│   ├── default_config.toml        # Default project-wide config
│   └── metadata.json              # Metadata for the project
├── games/                         # Game-related files
├── tests/                         # Unit and integration tests
├── scripts/                       # Utility and maintenance scripts
├── temp/                          # Centralized temp directory for cache/logs
├── LICENSE                        # License file
├── README.md                      # Project documentation
└── setup.py                       # Installation script
