-----------------------------------------------------------------------------------------
-- MySongEndMonitor.lua
-- Called from ScreenGameplay overlay to revert marquee banner once the song ends.
-----------------------------------------------------------------------------------------

local function WriteFallbackBannerToFile(fallbackPath)
    -- We'll write the fallback banner line out to /Save/CurrentSongInfo.log
    local output = "Event: SongEnd\nBanner: " .. fallbackPath .. "\n"

    local filePath = "/Save/CurrentSongInfo.log"
    local f = RageFileUtil.CreateRageFile()

    if not f:Open(filePath, 2) then  -- 2 = write mode
        Trace("MySongEndMonitor: WARNING - Failed to open file: " .. filePath)
        f:destroy()
        return
    end

    f:Write(output)
    f:Close()
    f:destroy()

    Trace("MySongEndMonitor: Wrote fallback banner to log: " .. fallbackPath)
end

return Def.ActorFrame{
    -- This command is triggered once the screen begins to transition out (end of gameplay).
    OffCommand=function(self)
        Trace("MySongEndMonitor.lua: OffCommand triggered, reverting marquee.")
        
        -- Provide your fallback path:
        local fallbackBanner = "C:/pegasus/assets/simply-love.png"
        WriteFallbackBannerToFile(fallbackBanner)
    end
}
