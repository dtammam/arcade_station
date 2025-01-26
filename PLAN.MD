# Plan

## arcade-station Overview
arcade-station is a front-end interface for managing and interacting with the games you love.
![Demo Collage](assets/images/readme/demo-collage.jpg)

## Motivation
The motivation behind this project is a desire to recreate the [ddr-picker](https://github.com/dtammam/ddr-picker) project from scratch so that the larger rhythm-game community can easily use it for any of their needs. This has been a passion project since I first saw [evan clue's version](https://github.com/evanclue/ddr-picker) - it inspired me to make it my own by refactoring it in PowerShell and by adding tons of new features. Now, I'm off to do it again - by the end, it'll provide the best of the ddr-picker experience while having a seamless install experience for those not technically savvy.

## Language(s)
- The primary language that will be used for this project will be Python:
    - It's compatible with Windows, Linux and Mac
    - It's got a rich set of libraries that will allow me to extend functionality
    - It's a tried and true, battle-tested language
    - Getting more hands-on, real-world experience with Python is a personal skill development
- If any lower-level interactions are needed, I will sparingly opt for the built-in OS' scripting language (PowerShell and Bash).

## Analyze Existing Code
Application Dependencies:
| Application | Purpose | Windows | Linux | Mac |
|------------|---------|---------|-------|-----|
| pegasus-fe | Frontend interface for displaying the games | 🪟 | 🐧 | 🍏 |
| MAME | Emulator for arcade games | 🪟 | 🐧 | 🍏 |
| ITGMania | Dance game simulator for the project (core version without songs) | 🪟 | 🐧 | 🍏 |
| Irfanview | Programmatically launchable image viewer (needs cross-platform alternative) | 🪟 | ❌ | ❌ |
| AudioSwitcher | OSD for volume when `explorer.exe` isn't the shell (needs cross-platform alternative) | 🪟 | ❌ | ❌ |
| Spicy Launchers | Software for managing overall experience | 🪟 | ❌ | ❌ |
| OBS Studio | Free and open source software for video recording and live streaming | 🪟 | 🐧 | 🍏 |
| Litboard Support (`mame2lit.exe`, `LightsTest.exe`) | Enables clean resetting of litboard lights | 🪟 | 🐧 | ❌ |
| iCloud | Apple sync client for photo uploads (considering alternative cloud solutions) | 🪟 | ❌ | 🍏 |

File Dependencies:
- assets: Locally stored .png files for game icons.
- Grid Micro theme for Pegasus: Specific theme supporting the optimized frontend's design.

System Dependencies:
- Local administrative privileges
- Ability to auto-logon
- Ability to modify the default shell

## Plan the Transition Strategy
### Phase 1: Core logic and skeleton in Python
1. Migrate and refactor the `CoreFunctions.psm1` module. Really knock out the base library that will be used by this project
2. Recreate all base PowerShell scripts in Python for the core functionality (killing Pegasus, launching games, taking pics)
3. Recreate the listener AutoIt scripts in Python and add to startup
This phase is complete when all initial functionality with all Windows dependencies are working.

### Phase 2: Novel cross-platform solution implementations
4. Implement cross-platform solutions for elements without native cross-platform support
This phase is complete when all functionality with all dependencies are solved for and functionality has been proven on Windows, Linux and Mac.

### Phase 3: User installer creation
5. Create an installer
This phase is complete when a user can take the installer, run it on their Windows/Linux/Mac machine and have a functional arcade-station setup.

### Phase 4: Ongoing optionality
6. Create additional support for flexible options (File sync clients, multiple versions of the game, extended options for streaming, etc.)

## Implement Translation
*To be determined*

## Thorough Testing and Validation
- Windows will be tested on my personal cabinet along with beta testers in the community.
- Linux will betested on virtual machines. I will start with [TJ's ITG System Image](https://docs.google.com/document/d/1_lO2ddaYogve08u7CsjC6OojXy36ZfGgo7VCRVkLJhU/edit?tab=t.0#heading=h.f4jo4mmoacz4)

## Code Maintenance and Documentation
- Code will be created in alignment with Python best practices.
- Code will be modular and functionalized.
- Code will be created only when needed. If an existing library exists, it will be preferred.
- Inputs will be fed by configuration files to allow easy, code-agnostic value population.
- Docstrings will be meaningful and will have meaningful examples.
- Contributions will be allowed and encouraged after the project is beyond Phase

## Reflect on the Process
*To be done as the project progresses*

## Stakeholder Communication
Updates will be shared with the [DDR + ITG Players](https://www.facebook.com/groups/565890830137096/) and [Private Dance Games Arcade Owner (ITG, DDR, PIU, TechnoMotion)](https://www.facebook.com/groups/180601838781725) Facebook groups as the project progresses.

## Manage Risks and Setbacks
*To be determined*