from xbmcswift2 import Plugin
import xbmc,xbmcaddon,xbmcvfs
import os, sys, subprocess
from subprocess import Popen
import json
import re
import xml.etree.ElementTree as etree


plugin = Plugin()



def log(v):
    xbmc.log(re.sub(',',',\n',repr(v)))

@plugin.route('/listxml')
def listxml():
    addon = xbmcaddon.Addon()
    profile = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')

    xml_file = os.path.join(profile, 'mame.xml')
    err_file = os.path.join(profile, "stderr.txt")
    json_file = os.path.join(profile, "mame.json")

    exe = plugin.get_setting('exe')
    (path,mame) = os.path.split(exe)
    #with open(xml_file,"wb") as out, open(err_file,"wb") as err:
    #    subprocess.Popen([mame, '-listxml'],shell=True, stdout=out,stderr=err,cwd=path)
  
    with open(xml_file,"rb") as in_file:
        list = []
        for event, elem in etree.iterparse(in_file):
            if event == 'end':
                if elem.tag == 'game':
                    game = elem
                    a = game.attrib
                    info = {}                   
                    info['name'] = a['name']
                    log(info['name'])
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
        
                
@plugin.route('/default')
def default():
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
    plugin.set_content('movies')
    sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items

#@plugin.route('/filter', name='filter_options', options={'clone': 'false', 'year_start' : '0', 'year_end' : '9999', 'name' : '', 'players' : '', 'manufacturer': '', 'rom' : ''})
#def filter(clone, year_start, year_end, name, players, manufacturer, rom):
#@plugin.route('/filter', name='filter_options', options={'clone': 'false'})
@plugin.route('/filter/<clone>/<start>/<end>/<name>/<exclude>/<rom>/<manufacturer>/<players>')
def filter(clone,start,end,name,exclude,rom,manufacturer,players):

    addon = xbmcaddon.Addon()
    profile = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    json_file = os.path.join(profile, "mame.json")
    xbmc.log(json_file)
    #xbmc.log(start)
    #xbmc.log(end)
    exe = plugin.get_setting('exe')
    (path,mame) = os.path.split(exe)
    with open(json_file, 'r') as infile:
        list = json.load(infile)
    
    #log(len(list))

    #sorted_games = sorted(games, key=lambda game: game[1])    
    
    keepers = []
    for l in list:
        keep = True
        if l['cloneof']:
            label = "[COLOR orange]%s[/COLOR] - [COLOR green]%s[/COLOR] - %s [B]%s[/B] [I]%s[/I]" % (l['description'], l['year'], l['name'], l['cloneof'], l['manufacturer'] )
        else:
            label = "[COLOR yellow][B]%s[/B][/COLOR] - [COLOR green]%s[/COLOR] - %s [B]%s[/B] [I]%s[/I]" % (l['description'], l['year'], l['name'], l['cloneof'], l['manufacturer'] )
        if l['cloneof'] != "" and clone == 'false':
            keep = False
        
        #year = int(re.sub('\?','0',l['year']))
        year = l['year']
        if '?' in year:
            year = 0
        else:
            year = int(year)
        #log(year)
        if year < int(start) or year > int(end):
            keep = False
        
        if name != '?':
            #log(name)
            if not re.search(name, l['description'],re.I):
                keep = False
                
        if exclude != '?':
            #log(exclude)
            if re.search(exclude, l['description'],re.I):
                keep = False
                
        if rom != '?':
            #log(name)
            if not re.search(rom, l['name'],re.I):
                keep = False
                
        if manufacturer != '?':
            #log(manufacturer)
            if not re.search(manufacturer, l['manufacturer'],re.I):
                keep = False
                
        if players != '?':
            #log(manufacturer)
            if not re.search(players, l['players'],re.I):
                keep = False

        if keep:
            l['label'] = label
            keepers.append(l)
            #games.append((label, l['name']))
    #log(len(keepers))
    out_keepers = []
    for l in keepers:
        l['sortname'] = l['name']
        if l['cloneof'] == '':
            l['cloneof'] = l['name']
            l['sortname'] = ''
        out_keepers.append(l)
    #log(out_keepers)
    #log(len(out_keepers))
    sorted_list = sorted(out_keepers, key = lambda x: (x['cloneof'], x['sortname']))
    #log(sorted_list)
    
    games = []
    for l in sorted_list:
        games.append((l['label'], l['name']))
    
    #sorted_games = sorted(games, key=lambda game: game[1])                

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
    #log(items)
    #plugin.set_content('movies')
    #sorted_items = sorted(items, key=lambda item: item['label'])
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
    clones = clones
    if manufacturer == '':
        manufacturer = '?'
    if players == '':
        players = '?'
    else:
        players = str(players)
        
    items = [
    {
        'label': filter,
        'path': plugin.url_for('filter' , clone=clones, start=start, end=end, name=name, exclude=exclude, rom=rom, manufacturer=manufacturer, players=players),

    } ,  
    {
        'label': "All",
        'path': plugin.url_for('filter' , clone='true', start=0, end=9999, name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    } ,    
    
    {
        'label': "No Clones",
        'path': plugin.url_for('filter', clone='false', start=1, end=1979, name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    } ,
    {
        'label': "Clones",
        'path': plugin.url_for('filter', clone='true', start=1, end=1979, name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
    {
        'label': "Invaders",
        'path': plugin.url_for('filter', clone='false', start=1, end=1979, name='invaders', exclude='?', rom='?', manufacturer='?', players='?'),

    }, 
    {
        'label': "inv rom",
        'path': plugin.url_for('filter', clone='true', start=1, end=1979, name='?', exclude='?', rom='inv', manufacturer='?', players='?'),

    },     {
        'label': "Golden",
        'path': plugin.url_for('filter', clone='false', start=1977, end=1982, name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
        {
        'label': "1980",
        'path': plugin.url_for('filter', clone='true', start=1980, end=1980, name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
    {
        'label': "Pre 1980",
        'path': plugin.url_for('filter', clone='true', start=1, end=1979, name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
    {
        'label': "Unknown Year",
        'path': plugin.url_for('filter', clone='false', start=0, end=0, name='?', exclude='?', rom='?',manufacturer='?', players='?'),

    },    ]

    sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items

@plugin.route('/play/<rom>/')
def play(rom):
    exe = plugin.get_setting('exe')
    roms = plugin.get_setting('roms')
    # Normally we would use label to parse a specific web page, in this case we are just
    # using it for a new list item label to show how URL parsing works.
    items = [
        {'label': rom},
    ]
    #subprocess.call(["c:\emulators\mame\mame.exe", "amidar"])
    #subprocess.Popen(['mame', 'amidar'], cwd='c:\\emulators\\mame')
    #return items
    #from subprocess import Popen, PIPE, STDOUT
    #handle = Popen(['mame.exe', 'amidar' ], shell=True, stdout=PIPE, stderr=STDOUT, stdin=PIPE, cwd=r'C:\emulators\mame')
    (path,mame) = os.path.split(exe)
    handle = Popen([mame, rom, '-rompath', roms], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,cwd=path)
    xbmc.log(handle.stdout.readline().strip())
    
if __name__ == '__main__':
    plugin.run()
