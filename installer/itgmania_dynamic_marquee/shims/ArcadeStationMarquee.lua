-- ArcadeStationMarquee.lua
-- Module for Arcade Station marquee integration with ITGMania
-- This displays song banners on a secondary display when songs are selected/played

-- Create a local table to return at the end
local t = {}

-- Put the log file next to this module in the Modules directory for simplicity
local LOG_FILE_PATH = "Themes/Simply Love/Modules/ArcadeStationMarquee.log"

-- Debug mode - set to true to output more details
local DEBUG = true

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
    DebugLog("WriteSongInfoToFile called")
    
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

    DebugLog("Absolute banner path: " .. absBanner)
    DebugLog("Attempting to open: " .. ITGManiaRoot .. LOG_FILE_PATH)

    local f = RageFileUtil.CreateRageFile()
    local fullLogPath = ITGManiaRoot .. LOG_FILE_PATH
    if not f:Open(fullLogPath, 2) then  -- 2 = write mode
        -- Try the non-absolute path as a fallback
        if not f:Open(LOG_FILE_PATH, 2) then
            Trace("WARNING: Failed to open file at either: " .. fullLogPath .. " OR " .. LOG_FILE_PATH)
            f:destroy()
            return
        end
    end

    DebugLog("Successfully opened file. Writing data...")
    f:Write(output)
    f:Close()
    f:destroy()
    DebugLog("Successfully wrote to log file")
end

-----------------------------------------------------------------------------------------
-- Writes fallback banner information when a song ends
-----------------------------------------------------------------------------------------
local function WriteFallbackBannerToFile(fallbackPath)
    DebugLog("WriteFallbackBannerToFile called with path: " .. tostring(fallbackPath))
    
    local output = "Event: SongEnd\nBanner: " .. fallbackPath .. "\n"

    local f = RageFileUtil.CreateRageFile()
    local fullLogPath = ITGManiaRoot .. LOG_FILE_PATH
    if not f:Open(fullLogPath, 2) then  -- 2 = write mode
        -- Try the non-absolute path as a fallback
        if not f:Open(LOG_FILE_PATH, 2) then
            Trace("ArcadeStationMarquee: WARNING - Failed to open file at either: " .. fullLogPath .. " OR " .. LOG_FILE_PATH)
            f:destroy()
            return
        end
    end
    
    DebugLog("Successfully opened fallback file. Writing data...")
    f:Write(output)
    f:Close()
    f:destroy()
    DebugLog("Successfully wrote fallback banner to log file")
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
        Trace("WARNING: Failed to create log file at " .. LOG_FILE_PATH)
    end
    f:destroy()
end

-- Call initialization
InitializeModule()

-- Define the ActorFrame for ScreenSelectMusic
t["ScreenSelectMusic"] = Def.ActorFrame {
    ModuleCommand=function(self)
        Trace("ArcadeStationMarquee: ScreenSelectMusic module loaded")
        
        -- Listen for the SongChosen message
        self:queuecommand("SetupListeners")
    end,
    
    SetupListenersCommand=function(self)
        -- Register for the SongChosen message, which is sent when a song is selected
        MESSAGEMAN:Broadcast("SongChosenMessageCommand")
    end,
    
    SongChosenMessageCommand=function(self)
        local song = GAMESTATE:GetCurrentSong()
        if song then
            Trace("ArcadeStationMarquee: SongChosenMessageCommand fired!")
            Trace("   -> Title: " .. (song:GetDisplayFullTitle() or "???"))
            WriteSongInfoToFile(song)
        else
            Trace("ArcadeStationMarquee: SongChosen fired, but no current song.")
        end
    end
}

-- Define the ActorFrame for ScreenGameplay
t["ScreenGameplay"] = Def.ActorFrame {
    ModuleCommand=function(self)
        Trace("ArcadeStationMarquee: ScreenGameplay module loaded")
        
        -- Listen for when the screen is transitioning out (end of gameplay)
        self:queuecommand("SetupListeners")
    end,
    
    SetupListenersCommand=function(self)
        -- Register for screen transitioning out
        self:addcommand("Off", function(self)
            Trace("ArcadeStationMarquee: OffCommand triggered, reverting marquee.")
            
            -- Use a fallback banner that's part of the theme
            local fallbackBanner = ITGManiaRoot .. "Themes/Simply Love/Graphics/ScreenTitleMenu logo.png"
            WriteFallbackBannerToFile(fallbackBanner)
        end)
    end
}

-- Return the module table
return t 