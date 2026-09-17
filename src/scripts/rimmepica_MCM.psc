Scriptname rimmepica_MCM extends SKI_ConfigBase
{rim-mepica: every few seconds, stop the undead eye glow effects that the game
sometimes leaves playing on the player - the glowing ball that floats beside
the player's eyes.}

; ----------------------------------------------------------------------------
; Why this happens
;
; Draugr, dragon priests and necromancer skeletons get their glowing eyes from
; an ability whose script does  EyeGlowFX.Play(caster, -1)  - an effect with no
; end time, stopped only when that creature dies. Now and then the engine hands
; that script the player as the caster, so the glow is played on the player
; instead and stays there for good. It is attached where the creature's eyes
; would be, which is why it hangs next to the player's eyes rather than on
; them.
;
; Stopping an effect that is not playing does nothing, so the fix is simply to
; call Stop() on every such effect at regular intervals.
; ----------------------------------------------------------------------------

; ----------------------------------------------------------------------------
; Settings. Auto properties live in the save game, so each save keeps its own
; numbers and they survive a reload without any extra bookkeeping.
; ----------------------------------------------------------------------------
bool  Property Enabled  = true Auto Hidden
float Property Interval = 10.0 Auto Hidden

; ----------------------------------------------------------------------------
; Tuning constants
; ----------------------------------------------------------------------------
float  INTERVAL_DEFAULT = 10.0
float  INTERVAL_MIN     = 1.0
float  INTERVAL_MAX     = 60.0
float  INTERVAL_STEP    = 1.0
string INTERVAL_FORMAT  = "{0} sec"

; ----------------------------------------------------------------------------
; Runtime state (not settings)
; ----------------------------------------------------------------------------
VisualEffect[] _effects            ; resolved on every load; None until then

int _oidEnabled
int _oidInterval
int _oidClearNow

int Function GetVersion()
    return 1
EndFunction

; ----------------------------------------------------------------------------
; Lifecycle
; ----------------------------------------------------------------------------

; Runs once, when SkyUI first registers this menu.
Event OnConfigInit()
    ModName = "rim-mepica"
    Pages = new string[1]
    Pages[0] = "$rimmepica_page_general"
EndEvent

Event OnInit()
    parent.OnInit()
    Restart()
EndEvent

; Reached through the PlayerRef alias (SKI_PlayerLoadGameAlias) every time a
; save is loaded. Papyrus update registrations do not reliably survive a load,
; so the timer is started again from here.
Event OnGameReload()
    parent.OnGameReload()
    Restart()
EndEvent

Function Restart()
    ResolveEffects()
    If Enabled
        ; Clear straight away: a save made while glowing loads glowing.
        ClearGlow()
        RegisterForSingleUpdate(Interval)
    Else
        UnregisterForUpdate()
    EndIf
EndFunction

; ----------------------------------------------------------------------------
; The effects
;
; Looked up by form ID rather than held in script properties, so the plugin
; needs no property data. Every one of these is played with an infinite
; duration by a creature ability script (DraugrFXScript, FxDraugrMagicScript,
; DragonPriestActorScript, FXSkeletonNecroScript, FXMG07DogScript,
; DLC1SoulCairnCreatureFX). None of them is ever meant to be on the player.
; ----------------------------------------------------------------------------
Function ResolveEffects()
    _effects = new VisualEffect[7]
    _effects[0] = Game.GetFormFromFile(0x000A8527, "Skyrim.esm") as VisualEffect    ; FXDraugrFemaleEyeEffect
    _effects[1] = Game.GetFormFromFile(0x000ABEE8, "Skyrim.esm") as VisualEffect    ; FXDraugrMaleEyeEffect
    _effects[2] = Game.GetFormFromFile(0x000AA856, "Skyrim.esm") as VisualEffect    ; FXDragonPreistEyeGlowEffect
    _effects[3] = Game.GetFormFromFile(0x000EB87A, "Skyrim.esm") as VisualEffect    ; FXSkeletonNecroEyeGlowEffect
    _effects[4] = Game.GetFormFromFile(0x000EBE9E, "Skyrim.esm") as VisualEffect    ; FXSkeletonNecroPriestEyeGlowEffect
    _effects[5] = Game.GetFormFromFile(0x000F9065, "Skyrim.esm") as VisualEffect    ; FXMG07DogEyeGlowEffect
    _effects[6] = Game.GetFormFromFile(0x00006AF4, "Dawnguard.esm") as VisualEffect ; DLC1SoulCairnFXSkeletonNecroEyeGlowEffect
EndFunction

Function ClearGlow()
    Actor player = Game.GetPlayer()
    If player == none || _effects == none
        Return
    EndIf
    int i = 0
    While i < _effects.Length
        If _effects[i] != none
            _effects[i].Stop(player)
        EndIf
        i += 1
    EndWhile
EndFunction

; ----------------------------------------------------------------------------
; The timer
; ----------------------------------------------------------------------------
Event OnUpdate()
    If !Enabled
        Return
    EndIf
    ClearGlow()
    RegisterForSingleUpdate(Interval)
EndEvent

Function SetEnabled(bool abEnabled)
    Enabled = abEnabled
    Restart()
EndFunction

; ----------------------------------------------------------------------------
; Menu
; ----------------------------------------------------------------------------
Event OnPageReset(string a_page)
    SetCursorFillMode(TOP_TO_BOTTOM)

    AddHeaderOption("$rimmepica_header_main", OPTION_FLAG_NONE)
    _oidEnabled = AddToggleOption("$rimmepica_enabled", Enabled, OPTION_FLAG_NONE)

    int sliderFlags = OPTION_FLAG_NONE
    If !Enabled
        sliderFlags = OPTION_FLAG_DISABLED
    EndIf
    _oidInterval = AddSliderOption("$rimmepica_interval", Interval, INTERVAL_FORMAT, sliderFlags)

    AddEmptyOption()

    AddHeaderOption("$rimmepica_header_manual", OPTION_FLAG_NONE)
    _oidClearNow = AddTextOption("$rimmepica_clear_now", "", OPTION_FLAG_NONE)
EndEvent

Event OnOptionHighlight(int a_option)
    If a_option == _oidEnabled
        SetInfoText("$rimmepica_enabled_info")
    ElseIf a_option == _oidInterval
        SetInfoText("$rimmepica_interval_info")
    ElseIf a_option == _oidClearNow
        SetInfoText("$rimmepica_clear_now_info")
    EndIf
EndEvent

Event OnOptionSelect(int a_option)
    If a_option == _oidEnabled
        SetEnabled(!Enabled)
        SetToggleOptionValue(a_option, Enabled, false)
        ForcePageReset()            ; the slider greys out with the toggle
    ElseIf a_option == _oidClearNow
        If _effects == none
            ResolveEffects()
        EndIf
        ClearGlow()
        ShowMessage("$rimmepica_cleared", false, "$rimmepica_ok", "")
    EndIf
EndEvent

Event OnOptionSliderOpen(int a_option)
    If a_option == _oidInterval
        SetSliderDialogDefaultValue(INTERVAL_DEFAULT)
        SetSliderDialogRange(INTERVAL_MIN, INTERVAL_MAX)
        SetSliderDialogInterval(INTERVAL_STEP)
        SetSliderDialogStartValue(Interval)
    EndIf
EndEvent

Event OnOptionSliderAccept(int a_option, float a_value)
    If a_option == _oidInterval
        Interval = a_value
        SetSliderOptionValue(a_option, a_value, INTERVAL_FORMAT, false)
        Restart()                   ; pick up the new interval now, not next tick
    EndIf
EndEvent

Event OnOptionDefault(int a_option)
    If a_option == _oidEnabled
        SetEnabled(true)
        SetToggleOptionValue(a_option, Enabled, false)
        ForcePageReset()
    ElseIf a_option == _oidInterval
        Interval = INTERVAL_DEFAULT
        SetSliderOptionValue(a_option, Interval, INTERVAL_FORMAT, false)
        Restart()
    EndIf
EndEvent
