2024-02-16:
- Seemingly must manually change theme for Pegasus to Pegasus Grid Micro: `2025-01-26T13:08:33 [i] Theme set to `Pegasus Grid Micro` (`C:/Repositories/arcade-station/src/pegasus-fe/themes/micro/`)`

- Headers for games are initially found here: `C:\Repositories\arcade-station\src\pegasus-fe\themes\micro\assets\logos`

- Question sent to Pegasus Discord:
    ```
    In Pegasus, the assets that are used by themes. Is there a way to relative path them or they must be in a sub \assets\ folder?
    [1:18 PM]DoctorDoofus: Heres's an example. I'd like to know if I can relative path assets.box_front to anywhere else in the project a few directories above this. Or just know that Pegasus MUST have it relative pathed this way:

    game: EXTREME
    file: C:\pegasus\games\ddr573-mame\ddrexproca.exe
    sortBy: e
    launch: {file.path}
    assets.box_front: assets/extreme-nonproclarity.png

    Real Pegasus bin location: \src\pegasus-fe\pegasus-fe_windows.exe
    Real file location: \src\pegasus-fe\config\metafiles\assets\extreme-nonproclarity.png
    Desired location: \src\assets\banners\extreme-nonproclarity.png (different dir than Pegasus) 
    ```