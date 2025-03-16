-- ArcadeStationMarquee.lua
-- Module for Arcade Station marquee integration with ITGMania
-- This displays song banners on a secondary display when songs are selected/played

-- Create a local table to return at the end
local t = {}

-- Put the log file next to this module in the Modules directory for simplicity
local LOG_FILE_PATH = "Themes/Simply Love/Modules/ArcadeStationMarquee.log"

-- Debug mode - set to true to output more details
local DEBUG = true

-- Track screen changes to detect when songs end
local currentScreen = ""
local songSelected = false
local lastSelectedSong = nil

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
-- Writes song information to the log file
-----------------------------------------------------------------------------------------
local function WriteSongInfoToFile(song)
    if not song then
        Trace("ArcadeStationMarquee: No song provided")
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

    local output = string.format([[
Event: Chosen
Pack: %s
SongTitle: %s

SongDir:   %s
Banner:    %s
ChartFile: %s
MusicFile: %s
]], pack, mainTitle, absSongDir, absBanner, absChartPath, absMusicPath)

    local f = RageFileUtil.CreateRageFile()
    if not f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
        Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
        f:destroy()
        return
    end

    f:Write(output)
    f:Close()
    f:destroy()
    
    Trace("ArcadeStationMarquee: Wrote song info for " .. mainTitle)
end

-----------------------------------------------------------------------------------------
-- Writes fallback banner information when a song ends
-----------------------------------------------------------------------------------------
local function WriteFallbackBannerToFile(fallbackPath)
    local output = "Event: SongEnd\nBanner: " .. fallbackPath .. "\n"

    local f = RageFileUtil.CreateRageFile()
    if not f:Open(LOG_FILE_PATH, 2) then  -- 2 = write mode
        Trace("ArcadeStationMarquee: WARNING - Failed to open file: " .. LOG_FILE_PATH)
        f:destroy()
        return
    end
    
    f:Write(output)
    f:Close()
    f:destroy()
    
    Trace("ArcadeStationMarquee: Wrote fallback banner info")
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
    ModuleCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenSelectMusic ModuleCommand")
        
        -- Write the default/empty state when entering song selection
        local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end,
    
    ChosenCommand = function(self)
        -- This gets triggered when a song is actually selected
        Trace("ArcadeStationMarquee: ScreenSelectMusic ChosenCommand")
        local song = GAMESTATE:GetCurrentSong()
        if song then
            WriteSongInfoToFile(song)
        end
    end
}

-- Define the ActorFrame for ScreenGameplay
t["ScreenGameplay"] = Def.Actor {
    ModuleCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay ModuleCommand")
        
        -- Write the song info when gameplay starts
        local song = GAMESTATE:GetCurrentSong()
        if song then
            WriteSongInfoToFile(song)
        end
    end,
    
    OffCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay OffCommand - reverting to default banner")
        
        -- Use a fallback banner that's part of the theme
        local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end
}

-- Additional hook for song ending
t["ScreenGameplay"] = Def.ActorFrame {
    OnCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay ActorFrame loaded")
    end,
    
    -- These additional hooks help catch song end events that might be missed
    OffCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay ActorFrame OffCommand")
        local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end,
    
    -- This catches when the song is skipped or fails
    CancelCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay CancelCommand")
        local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end
}

-- Add hook for ScreenEvaluation (appears after song)
t["ScreenEvaluation"] = Def.Actor {
    ModuleCommand = function(self)
        Trace("ArcadeStationMarquee: ScreenEvaluation ModuleCommand")
        
        -- When we reach evaluation screen, the song has definitely ended
        local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end
}

-- Add a global screen change monitor to detect transitions
t[#t+1] = Def.ActorFrame {
    OnCommand=function(self)
        self:queuecommand("MonitorScreenChange")
    end,
    
    MonitorScreenChangeCommand=function(self)
        local newScreen = SCREENMAN:GetTopScreen():GetName()
        
        if currentScreen ~= newScreen then
            DebugLog("Screen changed from " .. currentScreen .. " to " .. newScreen)
            
            -- If we transition from ScreenSelectMusic to another screen (like ScreenGameplay)
            -- and we haven't yet logged the song, do it now
            if currentScreen == "ScreenSelectMusic" and lastSelectedSong and not songSelected then
                Trace("ArcadeStationMarquee: Song selected (screen transition) - " .. lastSelectedSong:GetDisplayMainTitle())
                WriteSongInfoToFile(lastSelectedSong)
                songSelected = true
            end
            
            currentScreen = newScreen
        end
        
        -- Queue the next check
        self:sleep(0.1)
        self:queuecommand("MonitorScreenChange")
    end
}

-- Return the module table
return t 