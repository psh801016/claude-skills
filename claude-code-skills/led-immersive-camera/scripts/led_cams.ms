-- led_cams.ms : LED immersive room camera presets (A corner diagonal, B wall close, C vertical 9:16)
-- Usage: fileIn @"C:\Users\PSH\.agents\skills\led-immersive-camera\scripts\led_cams.ms"
--        buildLEDCams (selection as array) openSide:"front"   -- "front" = open side at -Y, "back" = +Y
-- Units: mm. Room is taken from the bounding box of the given LED wall objects.
-- 2026-11-02: camera C moved away from the target wall (was moving toward it).

fn LEDCam_getRoomBounds objs =
(
    local bb = #( [1e9,1e9,1e9], [-1e9,-1e9,-1e9] )
    for o in objs do
    (
        local mn = o.min
        local mx = o.max
        if mn.x < bb[1].x do bb[1].x = mn.x
        if mn.y < bb[1].y do bb[1].y = mn.y
        if mn.z < bb[1].z do bb[1].z = mn.z
        if mx.x > bb[2].x do bb[2].x = mx.x
        if mx.y > bb[2].y do bb[2].y = mx.y
        if mx.z > bb[2].z do bb[2].z = mx.z
    )
    bb
)

fn LEDCam_make camName pos tgt focal =
(
    local existing = getNodeByName camName
    if existing != undefined do delete existing
    local cam = VRayPhysicalCamera()
    cam.name = camName
    cam.pos = pos
    cam.targeted = true
    cam.target.pos = tgt
    cam.target.name = camName + ".Target"
    cam.film_width = 36.0
    cam.specify_fov = false
    cam.focal_length = focal
    cam.use_dof = false
    cam.f_number = 8.0
    cam.shutter_speed = 60.0
    cam.ISO = 400.0
    cam.whiteBalance = color 255 255 255
    if isProperty cam #auto_vertical_tilt_correction do cam.auto_vertical_tilt_correction = true
    if isProperty cam #vertical_tilt_correction do cam.vertical_tilt_correction = true
    cam
)

fn buildLEDCams walls openSide:"front" =
(
    if walls.count == 0 do ( messageBox "Select LED wall objects first."; return undefined )
    local bb = LEDCam_getRoomBounds walls
    local mn = bb[1]
    local mx = bb[2]
    local W = mx.x - mn.x
    local D = mx.y - mn.y
    local cx = (mn.x + mx.x) / 2.0
    local cy = (mn.y + mx.y) / 2.0
    local floorZ = mn.z
    local inset = 1800.0
    local eye = floorZ + 1500.0
    local tgtH = floorZ + 1400.0
    local backY = mx.y
    local frontY = mn.y
    local dirSign = -1.0
    if openSide == "back" do ( backY = mn.y; frontY = mx.y; dirSign = 1.0 )

    local posA = [mn.x + inset, backY + dirSign * inset, eye]
    local tgtA = [mx.x - inset * 0.5, frontY - dirSign * inset * 0.3, tgtH]
    local camA = LEDCam_make "LEDCam_A" posA tgtA 20.0

    local posB = [cx + W * 0.15, backY + dirSign * 3000.0, eye]
    local tgtB = [cx - W * 0.17, backY, floorZ + 1450.0]
    local camB = LEDCam_make "LEDCam_B" posB tgtB 18.0

    local posC = [cx, cy + dirSign * D * 0.15, floorZ + 1200.0]
    local tgtC = [cx + W * 0.1, backY, floorZ + 1450.0]
    local camC = LEDCam_make "LEDCam_C" posC tgtC 20.0

    format "Room: W=% D=% H=%\n" W D (mx.z - mn.z)
    format "LEDCAM_OK A B C\n"
    #(camA, camB, camC)
)
