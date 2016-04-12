from xbmcswift2 import Plugin
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import os, sys, subprocess
from subprocess import Popen
import json
import re
import time
import xml.etree.ElementTree as etree


plugin = Plugin()


def log(v):
    xbmc.log(re.sub(',',',\n',repr(v)))

    
@plugin.route('/listxml')
def listxml():
    dialog = xbmcgui.Dialog()
    
    exe = plugin.get_setting('exe')
    if exe == "":
        dialog.notification("MAME: mame.exe not found!", "Set mame.exe, press OK and try again.")
        return

    dialog.notification('MAME: Generating game list.', 'This takes a long long time!')
    addon = xbmcaddon.Addon()
    profile = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')

    xml_file = os.path.join(profile, 'mame.xml')
    err_file = os.path.join(profile, "stderr.txt")
    json_file = os.path.join(profile, "mame.json")
    

    (path,mame) = os.path.split(exe)
    with open(xml_file,"wb") as out, open(err_file,"wb") as err:
        p = subprocess.Popen([mame, '-listxml'],shell=True, stdout=out,stderr=err,cwd=path)
        count = 0
        while p.poll() is None:
            dialog.notification('MAME: Extracting game information.', 'This takes a long time.%s' % ('.' * (count % 3) ))
            count = count + 1
            time.sleep(1)

    dialog.notification('MAME: Generating game list.','processing games...')
    with open(xml_file,"rb") as in_file:
        list = []
        then = time.time()
        for event, elem in etree.iterparse(in_file):
            if event == 'end':
                if elem.tag == 'game':
                    game = elem
                    a = game.attrib
                    info = {}                   
                    info['name'] = a['name']

                    now = time.time()
                    diff = now - then
                    if diff > 1:
                        then = now
                        dialog.notification('MAME: Extracting game information.', '%s'  % (info['name']))

                    info['cloneof'] = ''
                    if 'cloneof' in a:
                        info['cloneof'] = a['cloneof']
                    info['isbios'] = ''
                    if 'isbios' in a:
                        info['isbios'] = a['isbios']                        
                    info['isdevice'] = ''
                    if 'isdevice' in a:
                        info['isdevice'] = a['isdevice']
                    info['ismechanical'] = ''
                    if 'ismechanical' in a:
                        info['ismechanical'] = a['ismechanical']                        
                    info['year'] = ''
                    y = game.find('year')
                    if y is not None:
                        info['year'] = y.text
                    info['manufacturer'] = ''
                    m = game.find('manufacturer')
                    if m is not None:
                        info['manufacturer'] = m.text                    
                    info['description'] = ''
                    d = game.find('description')
                    if d is not None:
                        info['description'] = d.text
                    info['status'] = ''
                    d = game.find('driver')
                    if d is not None:
                        d = d.attrib    
                        if 'status' in d:
                            info['status'] = d['status']
                    info['players'] = ''
                    i = game.find('input')
                    if i is not None:
                        i = i.attrib
                        if 'players' in i:
                            info['players'] = i['players']
                    if info['isbios'] == '' and info['isdevice'] == '' and info['ismechanical'] == '' and info['status'] != 'preliminary' :
                        list.append(info)
                        
                    elem.clear()
                    
        with open(json_file, 'wb') as outfile:
            json.dump(list, outfile)
            
        dialog.notification('MAME:','Finished extracting game information!')
        
        
        
@plugin.route('/missing')
def missing():
    dialog = xbmcgui.Dialog()

    roms = plugin.get_setting('roms')
    if roms == "":
        dialog.notification("MAME: roms path not entered!", "Set roms, press OK and try again.")
        return
    
    dialog.notification('MAME: Checking for missing roms.', 'Starting...')
    addon = xbmcaddon.Addon()
    profile = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    

    found_roms = []
    for file in os.listdir(roms):
        if file.endswith(".zip"):
            print(file)
            found_roms.append(file[:-4])
    
    json_file = os.path.join(profile, "mame.json")
    with open(json_file, 'r') as infile:
        list = json.load(infile)
        
    found_list = []
    for l in list:
        if l["name"] in found_roms:
            found_list.append(l)
            
    found_json_file = os.path.join(profile, "found.json")
    with open(found_json_file, 'wb') as outfile:
        json.dump(found_list, outfile)
        
    dialog.notification('MAME: Checking for missing roms.', 'Finished!')


@plugin.route('/filter/<clone>/<start>/<end>/<name>/<exclude>/<rom>/<manufacturer>/<players>/<found>/<timeless>')
def filter(clone,start,end,name,exclude,rom,manufacturer,players,found,timeless):
    dialog = xbmcgui.Dialog()
    
    addon = xbmcaddon.Addon()
    profile = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    if found == 'true':
        json_name = "found.json"
    else:
        json_name = "mame.json"
    json_file = os.path.join(profile, json_name)

    exe = plugin.get_setting('exe')
    if exe == "":
        dialog.notification("MAME: mame.exe not found!", "Set mame.exe in the Settings.")
        return
    
    mame_json_file = os.path.join(profile, "mame.json")
    if not os.path.exists(mame_json_file):
        listxml()
        
    found_json_file = os.path.join(profile, "found.json")
    if not os.path.exists(found_json_file):
        missing()
    
    (path,mame) = os.path.split(exe)
    try:
        with open(json_file, 'r') as infile:
            list = json.load(infile)
    except:
        dialog = xbmcgui.Dialog()
        dialog.notification("Play MAME: Missing File!" ,'Load game list in Settings.')
        return

    keepers = []
    for l in list:
        keep = True

        if l['cloneof'] != "" and clone == 'false':
            keep = False

        year = l['year']
        log(year)
        if year == '':
            year = '?'
            l['year'] = year
        if '?' in year:
            if timeless != 'true':
                keep = False
        else:
            year = int(year)
            if year < int(start) or year > int(end):
                keep = False
        
        if name != '?':
            if not re.search(name, l['description'],re.I):
                keep = False
                
        if exclude != '?':
            if re.search(exclude, l['description'],re.I):
                keep = False
                
        if rom != '?':
            if not re.search(rom, l['name'],re.I):
                keep = False
                
        if manufacturer != '?':
            if not re.search(manufacturer, l['manufacturer'],re.I):
                keep = False
                
        if players != '?':
            if not re.search(players, l['players'],re.I):
                keep = False

        if l['cloneof']:
            label = "[COLOR orange]%s[/COLOR] - [COLOR green]%s[/COLOR] - %s [B]%s[/B] [I]%s[/I]" % (
            l['description'], l['year'], l['name'], l['cloneof'], l['manufacturer'] )
        else:
            label = "[COLOR yellow][B]%s[/B][/COLOR] - [COLOR green]%s[/COLOR] - %s [B]%s[/B] [I]%s[/I]" % (
            l['description'], l['year'], l['name'], l['cloneof'], l['manufacturer'] )
                
        if keep:
            l['label'] = label
            keepers.append(l)
            
        
            
    out_keepers = []
    for l in keepers:
        l['sortname'] = l['name']
        if l['cloneof'] == '':
            l['cloneof'] = l['name']
            l['sortname'] = ''
        out_keepers.append(l)

    sorted_list = sorted(out_keepers, key = lambda x: (x['cloneof'], x['sortname']))
    
    games = []
    for l in sorted_list:
        games.append((l['label'], l['name']))

    snaps = plugin.get_setting('snaps')
    titles = plugin.get_setting('titles')
    cabinets = plugin.get_setting('cabinets')
    marquees = plugin.get_setting('marquees')
    flyers = plugin.get_setting('flyers')
    items = [
        {'label': r[0], 
        'thumbnail': '%s%s.png' % (snaps,r[1]), 
        'icon': '%s%s.png' % (marquees,r[1]), 
        'path': plugin.url_for('play', rom=r[1]),
        'properties' : {
        'fanart_image' : '%s%s.png' % (flyers,r[1]), 
        'banner' : '%s%s.png' % (marquees,r[1]), 
        'clearlogo': '%s%s.png' % (titles,r[1]), 
        'poster': '%s%s.png' % (cabinets,r[1]), 
        }
        } for r in games
    ]
    return items

@plugin.route('/')
def index():
    filter = plugin.get_setting('filter')
    name = plugin.get_setting('name')
    exclude = plugin.get_setting('exclude')
    rom = plugin.get_setting('rom')
    start = plugin.get_setting('start')
    end = plugin.get_setting('end')
    clones = plugin.get_setting('clones')
    manufacturer = plugin.get_setting('manufacturer')
    players = plugin.get_setting('players')
    found = plugin.get_setting('found')
    timeless = plugin.get_setting('timeless')

    clones = clones
    found = found
    if filter == '':
        filter = 'Filter'
    if name == '':
        name = '?'
    if exclude == '':
        exclude = '?'
    if rom == '':
        rom = '?'
    if start == '':
        start = '1'
    if end == '':
        end = '9999'
    timeless = timeless
    if manufacturer == '':
        manufacturer = '?'
    if players == '':
        players = '?'
    else:
        players = str(players)
        
    items = [
    {
        'label': filter,
        'path': plugin.url_for('filter' , clone=clones, start=start, end=end, name=name, exclude=exclude, rom=rom, manufacturer=manufacturer, players=players, found=found, timeless=timeless),

    } ,  
    ]
    sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items

@plugin.route('/play/<rom>/')
def play(rom):
    exe = plugin.get_setting('exe')
    roms = plugin.get_setting('roms')
    (path,mame) = os.path.split(exe)
    handle = Popen([mame, rom, '-rompath', roms], shell=True, cwd=path)

    
if __name__ == '__main__':
    plugin.run()
