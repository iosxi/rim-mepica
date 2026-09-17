Scriptname SKI_ConfigBase extends SKI_QuestBase
{Compile-time stub generated from SKI_ConfigBase.pex - not shipped with the mod.}

Int Property OPTION_TYPE_INPUT
    Int Function Get()
        return 0
    EndFunction
EndProperty
String Property CurrentPage
    String Function Get()
        return ""
    EndFunction
EndProperty
Int Property OPTION_TYPE_KEYMAP
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property LEFT_TO_RIGHT
    Int Function Get()
        return 0
    EndFunction
EndProperty
String Property MENU_ROOT
    String Function Get()
        return ""
    EndFunction
EndProperty
Int Property OPTION_FLAG_WITH_UNMAP
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property TOP_TO_BOTTOM
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_TYPE_HEADER
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_TYPE_EMPTY
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property STATE_RESET
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_TYPE_TOGGLE
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_FLAG_DISABLED
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property STATE_COLOR
    Int Function Get()
        return 0
    EndFunction
EndProperty
String[] Property Pages Auto
Int Property OPTION_TYPE_MENU
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property STATE_SLIDER
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_TYPE_TEXT
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_FLAG_HIDDEN
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property STATE_MENU
    Int Function Get()
        return 0
    EndFunction
EndProperty
String Property JOURNAL_MENU
    String Function Get()
        return ""
    EndFunction
EndProperty
Int Property OPTION_TYPE_SLIDER
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property OPTION_FLAG_NONE
    Int Function Get()
        return 0
    EndFunction
EndProperty
String Property ModName Auto
Int Property OPTION_TYPE_COLOR
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property STATE_DEFAULT
    Int Function Get()
        return 0
    EndFunction
EndProperty
Int Property STATE_INPUT
    Int Function Get()
        return 0
    EndFunction
EndProperty

Function SetCursorPosition(Int a_position)
EndFunction

Function SetSliderValue(Float a_value)
EndFunction

Int Function AddSliderOption(String a_text, Float a_value, String a_formatString, Int a_flags)
    return 0
EndFunction

Function SetOptionFlagsST(Int a_flags, Bool a_noUpdate, String a_stateName)
EndFunction

Event OnInputAcceptST(String a_input)
EndEvent

Int Function AddToggleOption(String a_text, Bool a_checked, Int a_flags)
    return 0
EndFunction

Function AddSliderOptionST(String a_stateName, String a_text, Float a_value, String a_formatString, Int a_flags)
EndFunction

Event OnConfigInit()
EndEvent

Function SetTitleText(String a_text)
EndFunction

Function SelectOption(Int a_index)
EndFunction

Event OnOptionColorAccept(Int a_option, Int a_color)
EndEvent

Function SetCursorFillMode(Int a_fillMode)
EndFunction

Event OnOptionDefault(Int a_option)
EndEvent

Event OnDefaultST()
EndEvent

Function Error(String a_msg)
EndFunction

Event OnOptionHighlight(Int a_option)
EndEvent

Function AddInputOptionST(String a_stateName, String a_text, String a_value, Int a_flags)
EndFunction

Function RequestSliderDialogData(Int a_index)
EndFunction

Function RemapKey(Int a_index, Int a_keyCode, String a_conflictControl, String a_conflictName)
EndFunction

Function HighlightOption(Int a_index)
EndFunction

Function ResetOption(Int a_index)
EndFunction

Event OnOptionColorOpen(Int a_option)
EndEvent

Function AddColorOptionST(String a_stateName, String a_text, Int a_color, Int a_flags)
EndFunction

Event OnConfigRegister()
EndEvent

Event OnOptionSelect(Int a_option)
EndEvent

Int Function GetStateOptionIndex(String a_stateName)
    return 0
EndFunction

Function CloseConfig()
EndFunction

Int Function AddEmptyOption()
    return 0
EndFunction

Event OnSliderAcceptST(Float a_value)
EndEvent

Function AddToggleOptionST(String a_stateName, String a_text, Bool a_checked, Int a_flags)
EndFunction

Function SetInputDialogStartText(String a_text)
EndFunction

Event OnPageReset(String a_page)
EndEvent

Event OnOptionMenuOpen(Int a_option)
EndEvent

Function SetSliderDialogInterval(Float a_value)
EndFunction

Event OnConfigManagerReady(String a_eventName, String a_strArg, Float a_numArg, Form a_sender)
EndEvent

Function SetSliderOptionValue(Int a_option, Float a_value, String a_formatString, Bool a_noUpdate)
EndFunction

Function SetOptionStrValue(Int a_index, String a_strValue, Bool a_noUpdate)
EndFunction

Int Function AddKeyMapOption(String a_text, Int a_keyCode, Int a_flags)
    return 0
EndFunction

Event OnVersionUpdate(Int a_version)
EndEvent

Function SetOptionValues(Int a_index, String a_strValue, Float a_numValue, Bool a_noUpdate)
EndFunction

Function SetTextOptionValueST(String a_value, Bool a_noUpdate, String a_stateName)
EndFunction

Function SetToggleOptionValueST(Bool a_checked, Bool a_noUpdate, String a_stateName)
EndFunction

Function AddTextOptionST(String a_stateName, String a_text, String a_value, Int a_flags)
EndFunction

Function RequestColorDialogData(Int a_index)
EndFunction

Function RequestMenuDialogData(Int a_index)
EndFunction

Function SetOptionFlags(Int a_option, Int a_flags, Bool a_noUpdate)
EndFunction

Function SetInputText(String a_text)
EndFunction

Function SetMenuDialogDefaultIndex(Int a_value)
EndFunction

Event OnInputOpenST()
EndEvent

Function SetPage(String a_page, Int a_index)
EndFunction

Function AddKeyMapOptionST(String a_stateName, String a_text, Int a_keyCode, Int a_flags)
EndFunction

Function OpenConfig()
EndFunction

Function SetInfoText(String a_text)
EndFunction

Bool Function ShowMessage(String a_message, Bool a_withCancel, String a_acceptLabel, String a_cancelLabel)
    return false
EndFunction

Event OnConfigManagerReset(String a_eventName, String a_strArg, Float a_numArg, Form a_sender)
EndEvent

Function SetColorDialogDefaultColor(Int a_color)
EndFunction

Event OnColorOpenST()
EndEvent

Function SetColorDialogStartColor(Int a_color)
EndFunction

Function SetMenuDialogOptions(String[] a_options)
EndFunction

Function SetSliderOptionValueST(Float a_value, String a_formatString, Bool a_noUpdate, String a_stateName)
EndFunction

Function AddOptionST(String a_stateName, Int a_optionType, String a_text, String a_strValue, Float a_numValue, Int a_flags)
EndFunction

Event OnSelectST()
EndEvent

Function SetSliderDialogStartValue(Float a_value)
EndFunction

Int Function AddHeaderOption(String a_text, Int a_flags)
    return 0
EndFunction

Event OnGameReload()
EndEvent

Function SetTextOptionValue(Int a_option, String a_value, Bool a_noUpdate)
EndFunction

Function SetSliderDialogDefaultValue(Float a_value)
EndFunction

Event OnOptionSliderAccept(Int a_option, Float a_value)
EndEvent

Function SetMenuDialogStartIndex(Int a_value)
EndFunction

Function SetInputOptionValueST(String a_value, Bool a_noUpdate, String a_stateName)
EndFunction

Event OnSliderOpenST()
EndEvent

Function SetKeyMapOptionValueST(Int a_keyCode, Bool a_noUpdate, String a_stateName)
EndFunction

Function SetColorOptionValueST(Int a_color, Bool a_noUpdate, String a_stateName)
EndFunction

Function SetMenuOptionValue(Int a_option, String a_value, Bool a_noUpdate)
EndFunction

Function SetMenuOptionValueST(String a_value, Bool a_noUpdate, String a_stateName)
EndFunction

Int Function AddMenuOption(String a_text, String a_value, Int a_flags)
    return 0
EndFunction

Function ForcePageReset()
EndFunction

Function SetOptionNumValue(Int a_index, Float a_numValue, Bool a_noUpdate)
EndFunction

Event OnMenuOpenST()
EndEvent

Function SetInputOptionValue(Int a_option, String a_value, Bool a_noUpdate)
EndFunction

Event OnKeyMapChangeST(Int a_keyCode, String a_conflictControl, String a_conflictName)
EndEvent

Function SetKeyMapOptionValue(Int a_option, Int a_keyCode, Bool a_noUpdate)
EndFunction

Function SetColorOptionValue(Int a_option, Int a_color, Bool a_noUpdate)
EndFunction

Function LoadCustomContent(String a_source, Float a_x, Float a_y)
EndFunction

Function SetToggleOptionValue(Int a_option, Bool a_checked, Bool a_noUpdate)
EndFunction

Int Function AddInputOption(String a_text, String a_value, Int a_flags)
    return 0
EndFunction

Event OnOptionKeyMapChange(Int a_option, Int a_keyCode, String a_conflictControl, String a_conflictName)
EndEvent

Function WriteOptionBuffers()
EndFunction

Function ClearOptionBuffers()
EndFunction

Int Function AddTextOption(String a_text, String a_value, Int a_flags)
    return 0
EndFunction

Function SetColorValue(Int a_color)
EndFunction

Event OnOptionInputAccept(Int a_option, String a_input)
EndEvent

Function RequestInputDialogData(Int a_index)
EndFunction

Event OnInit()
EndEvent

Event OnConfigOpen()
EndEvent

Event OnOptionSliderOpen(Int a_option)
EndEvent

Event OnOptionMenuAccept(Int a_option, Int a_index)
EndEvent

Event OnHighlightST()
EndEvent

Event OnColorAcceptST(Int a_color)
EndEvent

Int Function AddOption(Int a_optionType, String a_text, String a_strValue, Float a_numValue, Int a_flags)
    return 0
EndFunction

String Function GetCustomControl(Int a_keyCode)
    return ""
EndFunction

Int Function GetVersion()
    return 0
EndFunction

Event OnMessageDialogClose(String a_eventName, String a_strArg, Float a_numArg, Form a_sender)
EndEvent

Int Function AddColorOption(String a_text, Int a_color, Int a_flags)
    return 0
EndFunction

Function SetMenuIndex(Int a_index)
EndFunction

Event OnConfigClose()
EndEvent

Event OnMenuAcceptST(Int a_index)
EndEvent

Function SetSliderDialogRange(Float a_minValue, Float a_maxValue)
EndFunction

Event OnOptionInputOpen(Int a_option)
EndEvent

Function AddMenuOptionST(String a_stateName, String a_text, String a_value, Int a_flags)
EndFunction

Function UnloadCustomContent()
EndFunction

