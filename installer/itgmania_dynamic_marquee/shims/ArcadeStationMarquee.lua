-- ArcadeStationMarquee.lua
-- Module for Arcade Station marquee integration with ITGMania
-- This displays song banners on a secondary display when songs are selected/played

-- Create a local table to return at the end
local t = {}

-- Put the log file next to this module in the Modules directory for simplicity
local LOG_FILE_PATH = "Themes/Simply Love/Modules/ArcadeStationMarquee.log"

-- Debug mode - set to true to output more details
local DEBUG = true

-- Track states to better handle transitions
local currentScreen = ""
local songSelected = false
local lastSelectedSong = nil
local firstSelectionDone = false

-----------------------------------------------------------------------------------------
-- Debug logging function
-----------------------------------------------------------------------------------------
local function DebugLog(message)
    if DEBUG then
        Trace("ArcadeStationMarquee DEBUG: " .. tostring(message))
    end
end

-----------------------------------------------------------------------------------------
-- Determine the ITGMania root directory dynamically
-----------------------------------------------------------------------------------------
local function GetITGManiaRoot()
    -- In ITGMania/StepMania, we can use FILEMAN to get paths
    -- This will get us the absolute path to the current theme's directory
    local themePath = THEME:GetCurrentThemeDirectory()
    
    -- Remove "Themes/Simply Love/" from the end to get the ITGMania root
    -- This works regardless of where ITGMania is installed
    local rootPath = themePath:gsub("Themes/Simply Love/$", ""):gsub("Themes\\Simply Love\\$", "")
    
    -- Ensure the path has consistent forward slashes
    rootPath = rootPath:gsub("\\", "/")
    
    Trace("ArcadeStationMarquee: Detected ITGMania root: " .. rootPath)
    return rootPath
end

-- Store the root path
local ITGManiaRoot = GetITGManiaRoot()
DebugLog("ITGManiaRoot: " .. ITGManiaRoot)

-----------------------------------------------------------------------------------------
-- Utility: detect if a path is already absolute (on Windows)
-----------------------------------------------------------------------------------------
local function IsAbsolutePath(path)
    -- Check if it starts with "<DriveLetter>:/"
    -- e.g. C:/ or D:/ or a UNC path starting with double backslashes
    if path:match("^%a:%/") or path:match("^\\\\") then
        return true
    end
    return false
end

-----------------------------------------------------------------------------------------
-- Force a path to absolute by prepending ITGManiaRoot if it isn't already absolute
-----------------------------------------------------------------------------------------
local function ForceAbsolutePath(relPath)
    if not relPath or relPath == "" then
        return ""
    end

    if not IsAbsolutePath(relPath) then
        -- If it looks like "/Songs/In The Groove/Bend Your Mind/Bend Your Mind-bn.png"
        -- prepend the root path
        --
        -- We also handle the case where relPath might start with a slash or not.
        -- e.g. ITGManiaRoot + relPath => C:/Games/ITGmania/Songs/...
        return ITGManiaRoot .. relPath
    end
    return relPath
end

-----------------------------------------------------------------------------------------
-- Writes song information to the log file - Optimized for performance
-----------------------------------------------------------------------------------------
local function WriteSongInfoToFile(song)
    if not song then
        Trace("ArcadeStationMarquee: No song provided")
        return
    end
    
    -- Don't rewrite if it's the exact same song (object comparison)
    -- But DO allow writing even if songSelected=true if it's a different song
    if songSelected and lastSelectedSong == song then
        DebugLog("Skipping duplicate write for the same song")
        return
    end
    
    local mainTitle  = song:GetDisplayMainTitle() or "UnknownTitle"
    local pack       = song:GetGroupName()        or "UnknownPack"

    -- StepMania might return relative or absolute paths:
    local relSongDir   = song:GetSongDir()       or ""
    local relBanner    = song:GetBannerPath()    or ""
    local relChartPath = song:GetSongFilePath()  or ""  -- .sm or .ssc
    local relMusicPath = song:GetMusicPath()     or ""  -- .ogg/.mp3

    -- Force them all to absolute
    local absSongDir   = ForceAbsolutePath(relSongDir)
    local absBanner    = ForceAbsolutePath(relBanner)
    local absChartPath = ForceAbsolutePath(relChartPath)
    local absMusicPath = ForceAbsolutePath(relMusicPath)

    -- Pre-format string to minimize file write time
    local output = string.format([[
Event: Chosen
Pack: %s
SongTitle: %s

SongDir:   %s
Banner:    %s
ChartFile: %s
MusicFile: %s
]], pack, mainTitle, absSongDir, absBanner, absChartPath, absMusicPath)

    -- Open, write, close as quickly as possible
    local f = RageFileUtil.CreateRageFile()
    if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
        f:Write(output)
        f:Close()
        Trace("ArcadeStationMarquee: Wrote song info for " .. mainTitle)
    else
        Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
    end
    f:destroy()
    
    -- Mark as selected to avoid duplicate writes of the SAME song
    songSelected = true
    lastSelectedSong = song
    firstSelectionDone = true
end

-----------------------------------------------------------------------------------------
-- Writes fallback banner information when appropriate
-----------------------------------------------------------------------------------------
local function WriteFallbackBannerToFile(fallbackPath)
    -- Skip writing fallback in various circumstances
    if currentScreen == "ScreenGameplay" then
        -- Never override with fallback during gameplay
        return
    end
    
    -- Allow fallback on first entry to ScreenSelectMusic
    if currentScreen == "ScreenSelectMusic" and firstSelectionDone and songSelected then
        -- Don't show fallback if we have a selected song in song select screen
        return
    end

    local output = "Event: SongEnd\nBanner: " .. fallbackPath .. "\n"

    local f = RageFileUtil.CreateRageFile()
    if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
        f:Write(output)
        f:Close()
        Trace("ArcadeStationMarquee: Wrote fallback banner info")
    else
        Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
    end
    f:destroy()
    
    -- We've shown fallback, so reset the selection state
    -- but ONLY reset if we're not in ScreenSelectMusic OR this is first time
    if currentScreen ~= "ScreenSelectMusic" or not firstSelectionDone then
        songSelected = false
        lastSelectedSong = nil
    end
end

-- Create the log file during initialization
local function InitializeModule()
    Trace("ArcadeStationMarquee: Initializing module...")
    
    -- Create an empty log file if it doesn't exist yet
    local f = RageFileUtil.CreateRageFile()
    if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
        f:Write("Event: Init\nStatus: Ready\n")
        f:Close()
        Trace("ArcadeStationMarquee: Created log file at " .. LOG_FILE_PATH)
    else
        Trace("ArcadeStationMarquee: WARNING - Failed to create log file at " .. LOG_FILE_PATH)
    end
    f:destroy()
end

-- Call initialization
InitializeModule()

-- Define the ActorFrame for ScreenSelectMusic
t["ScreenSelectMusic"] = Def.Actor {
    BeginCommand = function(self)
        -- Track that we're on the song selection screen
        currentScreen = "ScreenSelectMusic"
        Trace("ArcadeStationMarquee: ScreenSelectMusic BeginCommand")
    end,
    
    ModuleCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenSelectMusic ModuleCommand")
        
        -- Only reset and show fallback on first entry to song selection
        if not firstSelectionDone then
            -- Write the default/empty state when entering song selection
            local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
            WriteFallbackBannerToFile(fallbackBanner)
        end
    end,
    
    -- This is specifically for when a song is selected
    ChosenCommand = function(self)
        Trace("ArcadeStationMarquee: ChosenCommand triggered")
        
        local song = GAMESTATE:GetCurrentSong()
        if song then
            -- Immediately write song info - highest priority
            Trace("ArcadeStationMarquee: Song chosen - " .. song:GetDisplayMainTitle())
            WriteSongInfoToFile(song)
        end
    end,
    
    -- Alternative catch for Start button press
    StartButtonMessageCommand = function(self)
        Trace("ArcadeStationMarquee: Start button pressed")
        
        local song = GAMESTATE:GetCurrentSong()
        if song then
            Trace("ArcadeStationMarquee: Start button for song - " .. song:GetDisplayMainTitle())
            WriteSongInfoToFile(song)
        end
    end,
    
    -- Handle when song is changing (hover)
    CurrentSongChangedMessageCommand = function(self)
        -- Store the song for reference, but don't write to log on hover
        local song = GAMESTATE:GetCurrentSong()
        if song then
            DebugLog("Song changed/hover: " .. song:GetDisplayMainTitle())
        end
    end
}

-- Define the ActorFrame for ScreenGameplay
t["ScreenGameplay"] = Def.Actor {
    BeginCommand = function(self)
        currentScreen = "ScreenGameplay"
        Trace("ArcadeStationMarquee: ScreenGameplay BeginCommand")
    end,
    
    ModuleCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay ModuleCommand")
        
        -- Make sure song info is written when gameplay actually starts
        local song = GAMESTATE:GetCurrentSong()
        if song then
            Trace("ArcadeStationMarquee: Gameplay screen - writing song info")
            WriteSongInfoToFile(song)
        end
    end,
    
    OffCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay OffCommand - song ended")
        
        -- Use a fallback banner when leaving gameplay
        local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end
}

-- Return the module table
return t 