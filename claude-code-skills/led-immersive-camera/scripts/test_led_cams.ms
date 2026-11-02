-- Regression test for led_cams.ms. Run headless (never in the user's open scene):
--   "C:\Program Files\Autodesk\3ds Max 2025\3dsmaxbatch.exe" test_led_cams.ms -listenerlog out.txt
-- Background (2026-11-02): web-made v1 moved camera C toward the target wall instead of back from it.
resetMaxFile #noPrompt
fileIn ((getFilenamePath (getThisScriptFilename())) + "led_cams.ms")
(
    local fails = #()
    local back = Box name:"wall_back" width:10000 length:200 height:4000 pos:[0, 3900, 0]
    local left = Box name:"wall_left" width:200 length:8000 height:4000 pos:[-4900, 0, 0]
    local right = Box name:"wall_right" width:200 length:8000 height:4000 pos:[4900, 0, 0]
    local cams = ::buildLEDCams #(back, left, right) openSide:"front"
    if cams == undefined or cams.count != 3 then append fails "cameras not created" else
    (
        for c in cams do
        (
            if classOf c != VRayPhysicalCamera do append fails (c.name + " not VRayPhysicalCamera")
            local p = c.pos
            if p.x < -5000 or p.x > 5000 or p.y < -4000 or p.y > 4000 do append fails (c.name + " outside room " + p as string)
        )
        local a = cams[1]
        if abs(a.pos.z - 1500) > 1 do append fails "A eye height not 1500"
        if a.focal_length != 20.0 do append fails "A focal not 20"
        local c = cams[3]
        if abs(c.pos.z - 1200) > 1 do append fails "C height not 1200"
        if (4000 - c.pos.y) <= 4000 do append fails ("C not behind room center, dist to target wall = " + (4000 - c.pos.y) as string)
        if c.target.pos.z <= c.pos.z do append fails "C not tilted up"
        local cams2 = ::buildLEDCams #(back, left, right) openSide:"front"
        if (for o in objects where matchPattern o.name pattern:"LEDCam_*" collect o).count != 6 do append fails "rerun not idempotent (expect 3 cams + 3 targets)"
    )
    if fails.count == 0 then format "LEDCAM_TEST_OK\n" else for f in fails do format "LEDCAM_TEST_FAIL %\n" f
)
quitMax #noPrompt
