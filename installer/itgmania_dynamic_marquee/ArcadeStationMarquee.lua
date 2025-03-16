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

-- Create the log file during initialization
local function InitializeModule()
    Trace("ArcadeStationMarquee: Initializing module...")
    
    -- Create an initial log file with our specific image path
    local songSelectImage = "C:\\Users\\dean\\AppData\\Roaming\\ITGmania\\Themes\\Simply Love\\Modules\\simply-love.png"
    
    local f = RageFileUtil.CreateRageFile()
    if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
        f:Write("Event: Init\nBanner: " .. songSelectImage .. "\n")
        f:Close()
        Trace("ArcadeStationMarquee: Created log file with initial image path")
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
        
        -- Write specific image path to log file for song selection screen
        local songSelectImage = "C:\\Users\\dean\\AppData\\Roaming\\ITGmania\\Themes\\Simply Love\\Modules\\simply-love.png"
        
        -- Open, write, close as quickly as possible
        local f = RageFileUtil.CreateRageFile()
        if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
            f:Write("Event: ScreenSelectMusic\nBanner: " .. songSelectImage .. "\n")
            f:Close()
            Trace("ArcadeStationMarquee: Wrote song selection screen image path to log")
        else
            Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
        end
        f:destroy()
        
        -- Mark that we've been to the song selection screen
        firstSelectionDone = true
    end,
    
    ModuleCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenSelectMusic ModuleCommand")
        
        -- Also write the image path in ModuleCommand to ensure it's shown
        local songSelectImage = "C:\\Users\\dean\\AppData\\Roaming\\ITGmania\\Themes\\Simply Love\\Modules\\simply-love.png"
        
        -- Open, write, close as quickly as possible
        local f = RageFileUtil.CreateRageFile()
        if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
            f:Write("Event: ScreenSelectMusic\nBanner: " .. songSelectImage .. "\n")
            f:Close()
            Trace("ArcadeStationMarquee: Wrote song selection screen image path to log (ModuleCommand)")
        else
            Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
        end
        f:destroy()
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
        
        -- Write specific image path to log file when song ends
        local songSelectImage = "C:\\Users\\dean\\AppData\\Roaming\\ITGmania\\Themes\\Simply Love\\Modules\\simply-love.png"
        
        -- Open, write, close as quickly as possible
        local f = RageFileUtil.CreateRageFile()
        if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
            f:Write("Event: SongEnd\nBanner: " .. songSelectImage .. "\n")
            f:Close()
            Trace("ArcadeStationMarquee: Wrote song end image path to log")
        else
            Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
        end
        f:destroy()
        
        -- Explicitly reset the selection state
        songSelected = false
        lastSelectedSong = nil
    end
}

-- Define the ActorFrame for ScreenEvaluation
t["ScreenEvaluation"] = Def.Actor {
    BeginCommand = function(self)
        currentScreen = "ScreenEvaluation"
        Trace("ArcadeStationMarquee: ScreenEvaluation BeginCommand")
        
        -- Write specific image path to log file for evaluation screen
        local songSelectImage = "C:\\Users\\dean\\AppData\\Roaming\\ITGmania\\Themes\\Simply Love\\Modules\\simply-love.png"
        
        -- Open, write, close as quickly as possible
        local f = RageFileUtil.CreateRageFile()
        if f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
            f:Write("Event: ScreenEvaluation\nBanner: " .. songSelectImage .. "\n")
            f:Close()
            Trace("ArcadeStationMarquee: Wrote evaluation screen image path to log")
        else
            Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
        end
        f:destroy()
        
        -- Reset selection state
        songSelected = false
        lastSelectedSong = nil
    end
}

-- Return the module table
return t 