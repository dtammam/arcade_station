2024-02-16:
- To-do:
    - Seemingly must manually change theme for Pegasus to Pegasus Grid Micro: `2025-01-26T13:08:33 [i] Theme set to `Pegasus Grid Micro` (`C:/Repositories/arcade_station/src/pegasus-fe/themes/micro/`)`
    - Headers for games are initially found here: `C:\Repositories\arcade_station\src\pegasus-fe\themes\micro\assets\logos`
    - In `C:\Repositories\arcade-station\src\pegasus-fe\config\settings.txt` we must rewrite and pass in theme post-install -> `general.theme: c:/Repositories/arcade-station/src/pegasus-fe/themes/micro/`

- Open questions:
    - What is `rb`: with open(config_path, 'rb') as file:
    - Why did you use class in the first place?
    - Why __main__
    - In Pegasus, the assets that are used by themes. Is there a way to relative path them or they must be in a sub \assets\ folder?
        Real Pegasus bin location: \src\pegasus-fe\pegasus-fe_windows.exe
        Real file location: \src\pegasus-fe\config\metafiles\assets\extreme-nonproclarity.png
        Desired location: \src\assets\banners\extreme-nonproclarity.png (different dir than Pegasus) 