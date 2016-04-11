from xbmcswift2 import Plugin
import xbmc
import os, sys, subprocess
from subprocess import Popen
import json
import re

plugin = Plugin()



def log(v):
    xbmc.log(re.sub(',',',\n',repr(v)))

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
    #xbmc.log(clone)
    #xbmc.log(start)
    #xbmc.log(end)
    exe = plugin.get_setting('exe')
    (path,mame) = os.path.split(exe)
    with open(os.path.join(path,'mame.json'), 'r') as infile:
        list = json.load(infile)
    
    log(len(list))

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
            year = -1
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
    log(len(keepers))
    out_keepers = []
    for l in keepers:
        if l['cloneof'] == '':
            l['cloneof'] = l['name']
            l['name'] = ''
        out_keepers.append(l)
    #log(out_keepers)
    log(len(out_keepers))
    sorted_list = sorted(out_keepers, key = lambda x: (x['cloneof'], x['name']))
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
    plugin.set_content('movies')
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
        start = '-2'
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
        'path': plugin.url_for('filter' , clone='true', start='-2', end='9999', name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    } ,    
    
    {
        'label': "No Clones",
        'path': plugin.url_for('filter', clone='false', start='-2', end='9999', name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    } ,
    {
        'label': "Clones",
        'path': plugin.url_for('filter', clone='true', start='-2', end='9999', name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
    {
        'label': "Invaders",
        'path': plugin.url_for('filter', clone='false', start='-2', end='9999', name='invaders', exclude='?', rom='?', manufacturer='?', players='?'),

    }, 
    {
        'label': "inv rom",
        'path': plugin.url_for('filter', clone='true', start='-2', end='9999', name='?', exclude='?', rom='inv', manufacturer='?', players='?'),

    },     {
        'label': "Golden",
        'path': plugin.url_for('filter', clone='false', start='1977', end='1982', name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
        {
        'label': "1980",
        'path': plugin.url_for('filter', clone='true', start='1980', end='1980', name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
    {
        'label': "Pre 1980",
        'path': plugin.url_for('filter', clone='true', start='0', end='1979', name='?', exclude='?', rom='?', manufacturer='?', players='?'),

    },
    {
        'label': "Unknown Year",
        'path': plugin.url_for('filter', clone='false', start='-2', end='0', name='?', exclude='?', rom='?',manufacturer='?', players='?'),

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
    handle = Popen([exe, rom, '-rompath', roms], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,cwd=path)
    xbmc.log(handle.stdout.readline().strip())
    
if __name__ == '__main__':
    plugin.run()
