# 🎮 Arcade Station Example Setup

## Table of Contents
- [Multi-Monitor Laptop Scenario](#multi-monitor-laptop-scenario)
- [Multi-Monitor Laptop Installation Walkthrough](#multi-monitor-laptop-installation-walkthrough)
- [A Basic Example Workflow with Arcade Station](#a-basic-example-workflow-with-arcade-station)

## 💻 Multi-Monitor Laptop Scenario

In this example, I'm demonstrating a **portable multi-monitor setup** using a Surface Laptop Studio connected to two external displays. This configuration allows me to:
- Run Arcade Station as the front-end interface
- Manage and launch ITGmania (a rhythm game) and Megatouch Maxx Crown (a touchscreen arcade game)
- Display game banners and song information on a secondary monitor using the dynamic marquee feature

**Why a laptop setup?** This demonstrates Arcade Station's flexibility - you don't need dedicated arcade hardware to create an excellent gaming experience. A laptop with external monitors provides:
- Portability for setting up temporary arcade stations
- Multi-monitor support for dynamic marquee displays
- Full functionality without permanent hardware installation

**Important:** Arcade Station works with virtually any hardware configuration - from laptops to dedicated cabinets to home PCs. This example shows just one approach, but you can adapt it to your specific needs, games, and hardware. Whether you're building a full-size MAME cabinet, a rhythm game station, or just want to organize your PC games, the same core functionality applies.

## 🔧 Multi-Monitor Laptop Installation Walkthrough

I'm standing in front of my laptop, logged in as the local Administrator, and have downloaded the latest version of Arcade Station.
It is a Windows-based PC, currently running Windows 11.

1. I've disabled UAC.

   <img src="../assets/images/example/generic/uac.png" width="60%">

2. I'll launch the installer and select `Next`.

   <img src="../assets/images/example/laptop/10.png" width="70%">

3. I'll choose an install location. By default, it wants to install in your user profile. I'm okay with this and will select `Next`. You'll then see the files copying to the location.

   <img src="../assets/images/example/laptop/20.png" width="70%">

   <img src="../assets/images/example/laptop/30.png" width="40%">

4. We're notified about the different types of games to configure. I'll leave the checkbox checked as I do want to configure my game, Megatouch Maxx, and select `Next`.

   <img src=../assets/images/example/laptop/40.png width="70%">

5. I'm asked if I want to use ITGmania. I do, so I'll leave it and select `Next`.
- The installer detected that I have it installed in the default location and is referencing it automatically
- It is set to use a default bundled picture for ITGmania's banner
- It has an option to use the dynamic marquee module which will show songs that I pick on my 2nd display when I pick them, which I'll leave checked

   <img src="../assets/images/example/laptop/50.png" width="70%">

6. I'm asked if I have any binary-based games to configure, which I do (Megatouch Maxx).
- I'll type Megatouch for the name
- I'll select browse and pick the .exe used to open my game
- I'll pick my banner image (the art for the game) that'll show up on the 2nd display. When I click Browse, I see a set of bundled art (which includes Megatouch - otherwise, I'd pick from my PC.)
- I don't have any other games to configure (which I'd do by selecting `Add Another Game`) so I'll select `Next` once done.

   <img src="../assets/images/example/laptop/60.png" width="70%">
   <img src="../assets/images/example/laptop/61.png" width="70%">
   <img src="../assets/images/example/laptop/62.png" width="70%">
   <img src="../assets/images/example/laptop/63.png" width="70%">

7. I'm asked if I want to setup any MAME games. I don't right now, so I'll select `Next`.
- But if I did, I'd check the box, input my `mame.exe` path and `mame.ini` path, then `Add Another MAME-Based Game`, filling it out similarly to how we did the binaries (with the addition of ROMs and save states). 

   <img src="../assets/images/example/laptop/70.png" width="70%">

8. I'm asked to setup key bindings and processes to kill - very important.
- In the `Key Bindings` tab, there are a set of default key bindings to do things like reset us back to the menu, close Arcade Station, and even start streaming if you'd like.
- If you have any custom scripts or apps you want to run with a button press, you can add them here.
- The main one for me are `Reset back to menu` (which closes the games and brings you back) which will get triggered if I click `Ctrl + Spacebar`. 
- I'm happy with these bindings for now, so I'll leave them - but I can add, edit, or remove as needed.

   <img src="../assets/images/example/laptop/80.png" width="70%">

9. Near the top, there's a `Process Management` tab. This is the list of processes to close when resetting back to the menu or exiting Arcade Station. 
- Since I'm adding Megatouch, I need to add the processes it launches to make sure they get closed.
- I added the list to the top and selected `Next`, leaving everything else.

   <img src="../assets/images/example/laptop/81.png" width="70%">
   <img src="../assets/images/example/laptop/82.png" width="70%">

10. I'm asked about setting up my display. This is for a dynamic marquee, or a "billboard" of sorts that shows the art for the game you pick.
- I click `Show Monitor Numbers` which shows a little number on each of my display, so I know which is identified as what for the system.
- I want it on my right screen (or `Monitor 1` for Arcade Station's sake), so I'll select it.
- I can choose the background color, since the dynamic marquee supports transparent .png files. I'm happy with `Black` so I'll leave it.
- I can also change the default menu image here if I want for when we're in the menu. I'm happy with the default, so I'll leave it checked and will select `Next`.

   <img src="../assets/images/example/laptop/90.png" width="70%">
   <img src="../assets/images/example/laptop/91.png" width="70%">

11. I'm asked about setting up Kiosk Mode, which would turn my computer into a purpose built station (when you turn it on, it'll auto-login and start arcade station - nothing else). Since this is just my portable machine, I won't. But if I were to, I'd check the box to `Enable Kiosk Mode` and input the credentials to automatically logon with. I'll select `Next`.

    <img src="../assets/images/example/laptop/100.png" width="70%">

12. I'm asked about utilities to setup:
- There's a light reset program option, which lets you pick your light controller if you want to reset them between game selections
- There's a VPN client setting, which lets you pick your VPN client and configuration file for autoconnecting when the system turns on
- There's a streaming setting, so that you can pick your streaming program like OBS to have it auto-started on a button press from the key bindings earlier
- By default, we install an audio app that is used to show volume controls in kiosk mode whenever we use it.
- We also give an option to save screenshots to a folder, which will map to a button press from the key bindings earlier
- I'll leave this all as default and select `Next`. 

   <img src="../assets/images/example/laptop/110.png" width="70%">

13. I'll be shown my summary, which will include all of the settings I picked. When ready, I'll select `Finish` and will receive a confirmation dialog, prompting me to launch it for the first time if I setup kiosk mode for any security prompts.

    <img src="../assets/images/example/laptop/120.png" width="70%">

    <img src="../assets/images/example/laptop/121.png" width="35%">

14. My install directory will open and I'll get a final confirmation box. Arcade Station is installed!

    <img src="../assets/images/example/laptop/130.png" width="70%">

    <img src="../assets/images/example/laptop/131.png" width="35%">

## 🎲 A Basic Example Workflow with Arcade Station

1. I'll right-click `launch_arcade_station.bat` and run it as administrator to start Arcade Station. If I set kiosk mode up, after this, I'd reboot.

2. Arcade Station will launch, showing the menu on my main screen and my `dynamic marquee` on my 2nd monitor (`Monitor 1` from the setup).
- We see ITGmania and Megatouch, just as you'd expect.
- I want to play some Megatouch, so I'll select it either by clicking or by using the arrow key and pressing `Enter`.

   <img src="../assets/images/example/laptop/200.jpg" width="70%">

3. After launching Megatouch, it kicks off the program we set, and boots into the game. It's quite fun.
- The dynamic marquee changed to the banner image for Megatouch set in the installer.
- Once I'm done, I'll use the reset to menu key binding (by default, `Ctrl + Spacebar`) which will close all programs (including the processes we added for Megatouch), closing the game and getting us back to the menu.

   <img src="../assets/images/example/laptop/210.jpg" width="70%">

   <img src="../assets/images/example/laptop/221.jpg" width="70%">

4. Once I'm done, I'll use the reset to menu key binding (by default, `Ctrl + Spacebar`) which will close all programs (including the processes we added for Megatouch), closing the game and getting us back to the menu.

   <img src="../assets/images/example/laptop/200.jpg" width="70%">

5. Now I'd like to play ITGmania, so I'll do the same thing - pick the entry and launch it.
- The dynamic marquee changed to the banner image for ITGmania and boots into the game.

   <img src="../assets/images/example/laptop/230.jpg" width="70%">

6. I'm going to play the song Kiss Me Red, classic song.
- Because we enabled the Simply Love dynamic marquee module, the banner changes to the song art for Kiss Me Red.
- Once the song ends and we go back to the song selection menu, the ITGmania banner gets set back.

   <img src="../assets/images/example/laptop/240.jpg" width="70%">
   <img src="../assets/images/example/laptop/250.jpg" width="70%">

7. I've had a great time today, and now that I'm done, I want to close Arcade Station. I do that with the default key binding of (`Ctrl + F10`.)