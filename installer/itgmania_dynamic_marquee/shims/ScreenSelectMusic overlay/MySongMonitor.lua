-----------------------------------------------------------------------------------------
-- CONFIG: point this to your own ITGMania or StepMania install directory
-----------------------------------------------------------------------------------------
local SMRoot = "C:/Games/ITGmania"

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
-- Force a path to absolute by prepending SMRoot if it isn't already absolute
-----------------------------------------------------------------------------------------
local function ForceAbsolutePath(relPath)
    if not relPath or relPath == "" then
        return ""
    end

    if not IsAbsolutePath(relPath) then
        -- If it looks like "/Songs/In The Groove/Bend Your Mind/Bend Your Mind-bn.png"
        -- prepend "C:/Games/ITGmania" (or whatever SMRoot is)
        --
        -- We also handle the case where relPath might start with a slash or not.
        -- e.g. SMRoot + relPath => C:/Games/ITGmania/Songs/...
        return SMRoot .. relPath
    end
    return relPath
end

-----------------------------------------------------------------------------------------
-- Writes all paths to an output file, converting them to absolute if needed
-----------------------------------------------------------------------------------------
local function WriteSongInfoToFile(song)
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

    -- We'll store this in StepMania's "/Save/CurrentSongInfo.txt",
    -- which typically expands to something like:
    --   C:/Users/<User>/AppData/Roaming/ITGMania/Save/CurrentSongInfo.txt
    local filePath = "/Save/CurrentSongInfo.log"

    Trace("MySongMonitor: Attempting to open: " .. filePath)

    local f = RageFileUtil.CreateRageFile()
    if not f:Open(filePath, 2) then
        Trace("WARNING: Failed to open file: " .. filePath)
        f:destroy()
        return
    end

    Trace("MySongMonitor: Successfully opened file. Writing data...")
    f:Write(output)
    f:Close()
    f:destroy()
end

-----------------------------------------------------------------------------------------
-- Return an ActorFrame that writes to the file on SongChosen (once you press Start)
-----------------------------------------------------------------------------------------
return Def.ActorFrame{

    InitCommand=function(self)
        Trace("MySongMonitor.lua: ActorFrame loaded successfully.")
    end,

    SongChosenMessageCommand=function(self)
        local song = GAMESTATE:GetCurrentSong()
        if song then
            Trace("MySongMonitor: SongChosenMessageCommand fired!")
            Trace("   -> Title: " .. (song:GetDisplayFullTitle() or "???"))
            WriteSongInfoToFile(song)
        else
            Trace("MySongMonitor: SongChosen fired, but no current song.")
        end
    end
}
