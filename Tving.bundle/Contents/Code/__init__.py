from tving import *
NAME = 'TVING'
PREFIX = '/video/tving'
ICON = 'icon-default.jpg'

####################################################################################################
def Start():
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = 0

####################################################################################################
@handler(PREFIX, NAME, thumb=ICON)
def MainMenu():
	oc = ObjectContainer()
	try:
		oc.add(DirectoryObject(key = Callback(Menu, title=unicode('LIVE'), type='LIVE'), title = unicode('LIVE')))
		oc.add(DirectoryObject(key = Callback(Menu, title=unicode('다시보기'), type='VOD'), title = unicode('다시보기')))
		oc.add(DirectoryObject(key = Callback(ContentList,  type='WATCHED', title=unicode('Watched'), param=''), title = unicode('Watched')))
		message = DoStartLoginCheck(Prefs['id'], Prefs['pw'], Prefs['login_type'])
		#message = DoStartLoginCheckWithToken()
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	except Exception as e:
		Log('<<<Exception>>> MainMenu: %s' % e)
	return oc

####################################################################################################
@route(PREFIX + '/Menu')
def Menu(title, type):
	oc = ObjectContainer()
	for item in GetMenu():
		tmp = item.split(':')
		if type == tmp[0]:
			oc.add(DirectoryObject(key = Callback(ContentList, type=tmp[0], title=unicode(tmp[1]), param=tmp[2], pageNo='1'), title = unicode(tmp[1])))
	return oc

####################################################################################################
@route(PREFIX + '/ContentList')
def ContentList(type, title, param, pageNo='1', mode='program'):
	LOG('ContentList::: type:%s title:%s param:%s pageNo:%s mode:%s' % (type, title, param, pageNo, mode))
	title3 = title
	if pageNo != '1': title3 += ' ' + pageNo + '페이지'
	oc = ObjectContainer(title2 = unicode(title3))
	try:
		has_more, items = GetList(type, param, pageNo)
		for item in items:
			if type == 'LIVE':
				title2 = item['channel_title']
				if item['free'] == False: title2 = '[시청불가] ' + title2
				oc.add(DirectoryObject(
					key = Callback(Quality, title=title2, type=type, code=item['live_code'], summary =item['episode_title'], thumb=item['img'], save_code = item['live_code'], save_title = item['channel_title'], save_image = item['img']),
					title = unicode(title2),
					summary = unicode(item['episode_title']),
					thumb = item['img'],
				))
			elif type == 'VOD':
				title2 = ''
				if item['free'] == 'Y': title2 = '[무료] ' + title2
				if mode == 'program':
					title2 += item['program_title']
					next_param = '&free=all&order=frequencyDesc&programCode=%s' % item['program_code']
					oc.add(DirectoryObject(
						key = Callback(ContentList, type=type, title=title2, param=next_param, mode='episode'),
						title = unicode(title2),
						summary = unicode(item['program_summary']),
						thumb = item['program_image']
					))
				else:
					title2 += item['episode_title']
					oc.add(DirectoryObject(
						key = Callback(Quality, title=title2, type=type, code=item['episode_code'], summary=item['episode_summary'], thumb=item['episode_image'], save_code = item['program_code'], save_title = item['program_title'], save_image = item['program_image']),
						title = unicode(title2),
						summary = unicode(item['episode_summary']),
						thumb = item['episode_image']
					))
			elif type == 'WATCHED':
				if item['type'] == 'LIVE':
					oc.add(DirectoryObject(
						key = Callback(Quality, title=item['title'], type=item['type'], code=item['code'], summary =item['title'], thumb=item['img'], save_code = item['code'], save_title = item['title'], save_image = item['img']),
						title = unicode(item['title']),
						summary = unicode(item['title']),
						thumb = item['img'],
					))
				else:
					next_param = '&free=all&order=frequencyDesc&programCode=%s' % item['code']
					oc.add(DirectoryObject(
						key = Callback(ContentList, type=item['type'], title=item['title'], param=next_param, mode='episode'),
						title = unicode(item['title']),
						summary = unicode(item['title']),
						thumb = item['img']
					))
				
				

		if pageNo != '1':
			oc.add(DirectoryObject(
				key = Callback(ContentList, type=type, title=title, param=param, pageNo=str(int(pageNo)-1), mode=mode),
				title = unicode('<< 이전 페이지')
			))
		if has_more == 'Y':
			oc.add(DirectoryObject(
				key = Callback(ContentList, type=type, title=title, param=param, pageNo=str(int(pageNo)+1), mode=mode),
				title = unicode('다음 페이지 >>')
			))
	except Exception as e:
		Log('<<<Exception>>> ContentList: %s' % e)
	if len(oc) == 0:
		message = 'Empty'
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc

####################################################################################################
@route(PREFIX + '/Quality')
def Quality(title, type, code, summary, thumb, save_code, save_title, save_image):
	oc = ObjectContainer(title2 = unicode(title))
	message = 'Empty'
	try:

		for quality in QUALITYS_STRING:
			url = GetURL(code, QUALITYS[quality],Prefs['id'], Prefs['pw'], Prefs['login_type'])
			title2 = title + ' [' + quality + ']'
			if url is not None:
				if url.endswith('PREVIEW'): title2 = '[미리보기] ' + title2
				if url is not None:
					#if Prefs['url_show'] == True: summary2 = summary + '\n' + url
					#summary = summary + '\n' + url
					oc.add(
						CreateVideoClipObject(
							url = url,
							title = unicode(title2),
							thumb = thumb,
							art = R('art-default.png'),
							summary = unicode(summary),
							type=type, save_code=save_code, 
							save_title=save_title, save_image=save_image,
							include_container = False
						)
					)
			else: 
				message = '시청불가'
				break
	except Exception as e:
		Log('<<<Exception>>> Quality: %s' % e)
	if len(oc) == 0:
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc


####################################################################################################
@route(PREFIX + '/CreateVideoClipObject', include_container = bool)
def CreateVideoClipObject(url, title, thumb, art, summary, type, save_code, save_title, save_image, 
                          optimized_for_streaming = True,
                          include_container = False, *args, **kwargs):

    vco = VideoClipObject(
        key = Callback(CreateVideoClipObject,
		url = url, title = title, thumb = thumb, art = art, summary = summary,
		type=type, save_code=save_code, save_title=save_title, save_image=save_image,
		optimized_for_streaming = optimized_for_streaming,
		include_container = True),
        rating_key = url,
        title = title,
        thumb = thumb,
        art = art,
        summary = summary,
        items = [
            MediaObject(
                parts = [
                    PartObject(
                        key = HTTPLiveStreamURL(Callback(PlayVideo, url = url, type=type, code=save_code, title=save_title, img=save_image))
                    )
                ],
                optimized_for_streaming = optimized_for_streaming,
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects = [vco])
    else:
        return vco


####################################################################################################
@indirect
@route(PREFIX + '/PlayVideo.m3u8')
def PlayVideo(url, type, code, title, img):
	try:
		Log('PLAYVIDEO:%s' % url)
		data = '|'.join([type, code, title.encode('utf-8'), img])
		SaveWatchedList(data)
	except Exception as e:
		Log('<<<Exception>>> PlayVideo: %s' % e)
	return IndirectResponse(VideoClipObject, key = url)



####################################################################################################
@route(PREFIX + '/label')
def Label(message):
	oc = ObjectContainer(title2 = unicode(message))
	oc.add(DirectoryObject(key = Callback(Label, message=message),title = unicode(message)))
	return oc
