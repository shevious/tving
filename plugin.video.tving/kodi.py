# -*- coding: utf-8 -*-
import os
import urllib
import xbmcplugin, xbmcgui, xbmcaddon
from urlparse import parse_qs

__addon__ = xbmcaddon.Addon()
__language__  = __addon__.getLocalizedString
sys.path.append(os.path.join( xbmc.translatePath( __addon__.getAddonInfo('path') ), 'resources', 'lib' ))
from tving import *

def Main():
	#login_type = 'CJONE'
	#if __addon__.getSetting('login_type') == 1: login_type = 'TVING'
	#message = DoStartLoginCheck(__addon__.getSetting('id'), __addon__.getSetting('pw'), login_type, __addon__.getSetting('use_local_logindata'))
	message = DoStartLoginCheckWithToken()
	addDir('LIVE', None, None, True, 'Menu', 'LIVE', None, None)
	addDir('다시보기', None, None, True, 'Menu', 'VOD', None, None)
	addDir('Watched', None, None, True, 'ContentList', 'WATCHED::', None, 1)
	addDir(message, None, None, True, None, None, None, None)
	
	#if GetLoginStatus() is not 'SUCCESS':
	#	dialog = xbmcgui.Dialog()
	#	ret = dialog.yesno(__addon__.getAddonInfo('name'), __language__(30201).encode('utf8'), __language__(30202).encode('utf8'))
	#	if ret == True:
	#		__addon__.openSettings()
	#		sys.exit()
	#else: 
	#	addon_noti( message )
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def Menu(p):
	for item in GetMenu():
		tmp = item.split(':')
		if p['param'] == tmp[0]:
			addDir(tmp[1], None, None, True, 'ContentList', item, 'program', 1)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def ContentList(p):
	tmp = p['param'].split(':')
	type = tmp[0]
	title = tmp[1]
	param = tmp[2]
	pageNo = p['pageNo']
	mode = p['param2']
	has_more, items = GetList(type, param, pageNo)
	for item in items:
		if type == 'LIVE':
			title2 = item['channel_title']
			if item['free'] == False: title2 = '[' + __language__(30001)+ '] ' + title2
			infoLabels = {"mediatype":"episode","label":item['channel_title'] ,"title":item['channel_title'],"plot":item['episode_title']}
			save_param = '|'.join( [tmp[0], item['live_code'], urllib.quote(item['channel_title'].encode('utf-8')), item['img'] ])
			addDir(title2, item['img'], infoLabels, False, 'PlayVideo', item['live_code'], save_param, None)
		elif type == 'VOD':
			title2 = ''
			if item['free'] == 'Y': title2 = '[' + __language__(30002)+ '] ' + title2
			if mode == 'program':
				title2 += item['program_title']
				tving_param = 'VOD:TITLE:&free=all&order=frequencyDesc&programCode=%s' % item['program_code']
				infoLabels = {"mediatype":"episode","label":item['program_title'], "title":title2, "plot":item['program_summary']}
				addDir(title2, item['program_image'], infoLabels, True, 'ContentList', tving_param, 'Episode', 1)
			else:
				title2 += item['episode_title']
				infoLabels = {"mediatype":"episode","label":title2, "title":title2,"plot":item['episode_summary']}
				next_param = '|'.join( [tmp[0], item['program_code'], urllib.quote(item['program_title'].encode('utf-8')), item['program_image'] ])
				addDir(title2, item['episode_image'], infoLabels, False, 'PlayVideo', item['episode_code'], next_param, None)
		elif type == 'WATCHED':
			if item['type'] == 'LIVE':
				infoLabels = {"mediatype":"episode","label":item['title'] ,"title":item['title'],"plot":item['title']}
				save_param = '|'.join( [item['type'], item['code'], urllib.quote(item['title'].encode('utf-8')), item['img'] ])
				addDir(item['title'], item['img'], infoLabels, False, 'PlayVideo', item['code'], save_param, None)
			else:
				next_param = '&free=all&order=frequencyDesc&programCode=%s' % item['code']
				tving_param = 'VOD:TITLE:&free=all&order=frequencyDesc&programCode=%s' % item['code']
				infoLabels = {"mediatype":"episode","label":item['title'], "title":item['title'], "plot":item['title']}
				addDir(item['title'], item['img'], infoLabels, True, 'ContentList', tving_param, 'Episode', 1)
	if pageNo != '1':
		addDir('<< ' + __language__(30003).encode('utf8'), None, None, True, 'ContentList', p['param'], p['param2'], str(int(pageNo)-1))

	if has_more == 'Y':
		addDir(__language__(30004).encode('utf8') + ' >>', None, None, True, 'ContentList', p['param'], p['param2'], str(int(pageNo)+1))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	

def PlayVideo( p ):
	quality = GetQuality()
	if quality is None: return

	code = p['param']
	url = GetURL(code, QUALITYS[quality])
	if url is None:
		addon_noti( __language__(30001).encode('utf8') )
		return
	if url.find('PREVIEW') != -1:
		addon_noti( __language__(30005).encode('utf8') )

	tmps = p['param2'].split('|')
	data = '|'.join([tmps[0], tmps[1], urllib.unquote(tmps[2].encode('utf-8')), tmps[3]])
	SaveWatchedList(data)
	item = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


def GetQuality():
	#isManualQuality = __addon__.getSetting('manual_quality')
	isManualQuality = GetSetting('manual_quality')
	quality = None
	if (isManualQuality == 'true'):
		choose_idx = xbmcgui.Dialog().select('Quality'.encode('utf-8'), QUALITYS_STRING)
		if choose_idx > -1: quality = QUALITYS_STRING[choose_idx]
		else: quality = None
		quality
	else:
		#selected_quality = __addon__.getSetting('selected_quality')
		selected_quality = GetSetting('selected_quality')
		quality =  QUALITYS_STRING[int(selected_quality)]
	return quality


#########################
def addDir(title, img, infoLabels, isFolder, mode, param, param2, pageNo):
	params = {'mode': mode, 'param':param, 'param2':param2, 'pageNo':pageNo}
	url = '%s?%s' %(sys.argv[0], urllib.urlencode(params))
	listitem = xbmcgui.ListItem(title, thumbnailImage=img)
	if infoLabels: listitem.setInfo(type="Video", infoLabels=infoLabels)
	if not isFolder: listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, isFolder)

def addon_noti(sting):
	try:
		dialog = xbmcgui.Dialog()
		dialog.notification(__addon__.getAddonInfo('name'), sting)
	except:
		LOG('addonException: addon_noti')

def get_params():
	p = parse_qs(sys.argv[2][1:])
	for i in p.keys():
		p[i] = p[i][0]
	return p


params = get_params()
try:
	mode = params['mode']
except:
	mode = None
if mode == None: Main()
elif mode == 'Menu': Menu(params)
elif mode == 'ContentList': ContentList(params)
elif mode == 'PlayVideo': PlayVideo(params)
else: LOG('NOT FUNCTION!!')

