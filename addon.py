import xbmc
from xml.dom import minidom
import xbmcaddon
import xbmcgui
import os
import time
import xbmcvfs
import sys

if sys.version > '3':
    xbmc.translatePath = xbmcvfs.translatePath

Addon = xbmcaddon.Addon('script.audio.delayconfig')
t = 1000

#_OSD_DELAY_CONTROL_ID = -73
_OSD_DELAY_CONTROL_ID = -74  # AeonMQ8
_OSD_DELAY_CONTROL_ID2 = 11 # probably the delay selection bar?

def get_argdict():
	argd = {}
	for i in range(1, len(sys.argv)):
		tok = sys.argv[i].split('=')
		argd[tok[0]] = tok[i]
	return argd


def calc_num_steps(current, requested):
    requested = requested / 1000.0

    current = round(float(current), 3)
    xbmc.log('calc_num_steps - current: {}, requested: {}'.format(current, requested), xbmc.LOGINFO)

    return int(((float(requested) * 1000000) - (float(current) * 1000000)) / 25000)


def show_delay_info(delay, device=None):
    line1 = Addon.getSetting('line1')
    line2 = Addon.getSetting('line2')

    if float(delay) > 0:
        n = Addon.getLocalizedString(30021)
    if float(delay) < 0:
        n = Addon.getLocalizedString(30022)
    if float(delay) == 0:
        n = Addon.getLocalizedString(30023)
    if float(delay) == -0.000000:
        sources = "0.000000"

    if device is None:
        device = ""

    lines = [format(float(delay), '.3f') + n, device, '', t]

    xbmcgui.Dialog().notification(*lines)


def wait_for_mtime_change(filepath, refmtime):
    while True:
        curmtime = os.path.getmtime(filepath)
        if curmtime != refmtime:
            return
        time.sleep(0.01)

def set_delay_value(requested_delay_value):
    guisettings_path = xbmc.translatePath('special://profile/guisettings.xml')
    time1 = os.path.getmtime(guisettings_path)

    xbmc.log("########## 4", xbmc.LOGINFO)

    xbmc.executebuiltin('ActivateWindow(osdaudiosettings)')
    xbmc.executebuiltin('SetFocus({})'.format(_OSD_DELAY_CONTROL_ID))
    xbmc.log("########## 5", xbmc.LOGINFO)
    xbmc.executebuiltin("Action(select)")
    xbmc.executebuiltin('SetFocus({})'.format(_OSD_DELAY_CONTROL_ID2))
    xbmc.executebuiltin("Action(select)", wait=True)

    wait_for_mtime_change(guisettings_path, time1)

    sourcesXML = minidom.parse(xbmc.translatePath('special://profile/guisettings.xml'))
    sources = sourcesXML.getElementsByTagName('audiodelay')[0].firstChild.nodeValue

    numSteps = calc_num_steps(sources, requested_delay_value)

    xbmc.log('numSteps: {}'.format(numSteps), xbmc.LOGINFO)

    for _ in range(abs(numSteps)):
        if numSteps > 0.0:
            xbmc.executebuiltin("Action(AudioDelayPlus)")
        else:
            xbmc.executebuiltin("Action(AudioDelayMinus)")

    time3 = os.path.getmtime(guisettings_path)
    xbmc.executebuiltin('SetFocus({})'.format(_OSD_DELAY_CONTROL_ID))
    xbmc.executebuiltin("Action(select)")
    xbmc.executebuiltin('SetFocus({})'.format(_OSD_DELAY_CONTROL_ID2))
    xbmc.executebuiltin("Action(select)", wait=True)
    time.sleep(1.0)
    xbmc.executebuiltin("Action(close)", wait=True)

    wait_for_mtime_change(guisettings_path, time3)
    
    show_delay_info(requested_delay_value)


def main():
    xbmc.log("########## 1", xbmc.LOGINFO)

    if (xbmc.getCondVisibility('Player.HasMedia') == False):
        xbmcgui.Dialog().notification("",Addon.getLocalizedString(30015), "",t)
        return

    xbmc.log("########## 2", xbmc.LOGINFO)

    argsd = get_argdict()

    if 'delay' not in argsd:
        xbmc.log("Necessary parameter 'delay' not found", xbmc.LOGERROR)
        return

    try:
        requested_delay_value = int(argsd['delay'])
    except ValueError:
        xbmc.log("Cannot convert 'delay' parameter to integer: {}".format(argsd['delay']), xbmc.LOGERROR)
        return

    xbmc.log("########## 3", xbmc.LOGINFO)

    set_delay_value(requested_delay_value)

main()
