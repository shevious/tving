# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import os
import json
import re
import pickle
from io import open


DEFAULT_PARAM = '&screenCode=CSSD0100&networkCode=CSND0900&osCode=CSOD0900&teleCode=CSCD0900&apiKey=1e7952d0917d6aab1f0293a063697610'
QUALITYS = {'FHD':'stream50', 'HD':'stream40', 'SD':'stream30'}
QUALITYS_STRING = ['FHD', 'HD', 'SD']
MENU_LIST = [
	'LIVE:인기 LIVE:',
	'LIVE:TV 채널:&channelType=CPCS0100',
	'LIVE:TVING TV:&channelType=CPCS0300',
	'VOD::&free=all&lastFrequency=y', 
	'VOD:무료 :&free=y&multiCategoryCode=PCA%2CPCD%2CPCG%2CPCZ%2CPCN%2CPCF%2CPCC%2CPCAN%2CPCE%2CPCI%2CPCJ%2CPCK%2CPCH%2CPCPOS&lastFrequency=y',
	'VOD:드라마 :&free=all&multiCategoryCode=PCA&lastFrequency=y',
	'VOD:예능/뮤직 :&free=all&multiCategoryCode=PCD%2CPCG%2CPCZ&lastFrequency=y',
	'VOD:스타일/푸드 :&free=all&multiCategoryCode=PCN%2CPCF&lastFrequency=y',
	'VOD:키즈/애니메이션 :&free=all&multiCategoryCode=PCC%2CPCAN&lastFrequency=y',
	'VOD:e스포츠 :&free=all&multiCategoryCode=PCE&lastFrequency=y',
	'VOD:교양 :&free=all&multiCategoryCode=PCI%2CPCJ%2CPCK%2CPCH&lastFrequency=y',
	'VOD:해외TV :&free=all&multiCategoryCode=PCPOS&lastFrequency=y',
	'VOD:웹드라마 :&free=all&multiCategoryCode=PCWD&lastFrequency=y']
VOD_GENRE = ['최신:&order=broadDate', '인기:&order=viewDay']

VERSION = '0.3.1'

######################################## 
# KODI & PLEX
######################################## 
import os
try:
	import xbmc, xbmcaddon
	profile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
	LOCAL_PROGRAM_LIST = xbmc.translatePath(os.path.join( profile, 'programlist.txt'))
	LOGINDATA = xbmc.translatePath(os.path.join( profile, 'login.dat'))
except:
	pass

try:
	LOCAL_PROGRAM_LIST = os.path.join( os.getcwd(), 'programlist.txt')
	LOGINDATA = os.path.join( os.getcwd(), 'login.dat')
except:
	pass

def LOG(str):
	try :
		import xbmc, xbmcaddon
		try:
			xbmc.log("[%s-%s]: %s" %(xbmcaddon.Addon().getAddonInfo('id'), xbmcaddon.Addon().getAddonInfo('version'), str), level=xbmc.LOGNOTICE)
			log_message = str.encode('utf-8', 'ignore')
		except:
			log_message = 'TVING Exception'
		xbmc.log("[%s-%s]: %s" %(xbmcaddon.Addon().getAddonInfo('id'), xbmcaddon.Addon().getAddonInfo('version'), log_message), level=xbmc.LOGNOTICE)
		return
	except:
		pass

	try:
		Log(str)
		return
	except:
		pass


def GetSetting(type):
	try:
		import xbmc, xbmcaddon
		ret = xbmcaddon.Addon().getSetting(type)
		return ret
	except:
		pass

	try:
		ret = Prefs[type]
		return ret
	except:
		pass

######################################## 
# REAL URL
######################################## 
import urllib2
PROXY_URL = 'http://soju6jan.synology.me/tving/tving.php?c=%s&q=%s&l=%s'

def GetBroadURL(code, quality ):
	try:
		#login2 = login['t'].split('=')[1] if login is not None and 't' in login else ''
		login2 = urllib.unquote(GetSetting('token')).decode('utf8')
		url =  PROXY_URL % (code, quality, login2)
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		return response.read().strip()
	except Exception as e:
		LOG('GetBroadURL exception!!!')
	return


######################################## 
# LOGIC
######################################## 
def GetMenu():
	list = []
	for item in MENU_LIST:
		if item.startswith('LIVE'): list.append(item)
		else:
			tmp = item.split(':')
			list.append(tmp[0]+':'+tmp[1]+VOD_GENRE[0].split(':')[0]+':'+tmp[2]+VOD_GENRE[0].split(':')[1]);
			list.append(tmp[0]+':'+tmp[1]+VOD_GENRE[1].split(':')[0]+':'+tmp[2]+VOD_GENRE[1].split(':')[1]);
	return list

def DoStartLoginCheckWithToken():
	ret = 'Version : %s ' % VERSION
	if GetSetting('token'):
		ret += '(토큰 있음)'
	else:
		ret += '(토큰 없음)'
	return ret



def DoStartLoginCheck(id, pw, login_type, use_local_logindata):
	if id == '' : id = None
	if pw == '' : pw = None
	message = '['
	if id is None or pw is None:
		message += '아이디/암호 정보가 없습니다.'
	else:
		status = GetLoginStatus()
		if status == 'NOT_LOGIN_FILE' or status == 'LOGIN_FAIL' or use_local_logindata == False or use_local_logindata == 'false':
			isLogin = DoLogin(id, pw, login_type)
			status = GetLoginStatus()
			if status == 'SUCCESS': 
				message += '로그인 정보를 저장했습니다. '
				if str(use_local_logindata): message += '저장된 정보로 로그인합니다.'
				else: message += '매번 로그인합니다.'
			elif status == 'LOGIN_FAIL': message += '로그인에 실패하였습니다.'
		elif status == 'SUCCESS': message += '저장된 로그인 정보가 있습니다.' 
		elif status == 'LOGIN_FAIL': message += '로그인 파일은 있으나 유효하지 않습니다'
	message += ']'
	return message


def GetLoginStatus():
	if os.path.isfile(LOGINDATA):
		login_data = GetLoginData()
		if 't' in login_data: return 'SUCCESS'
		else: return 'LOGIN_FAIL'
	else:
		return 'NOT_LOGIN_FILE'


def DoLogin(user_id, user_pw, type ):
	e = 'Log'
	isLogin = False
	try:
		if os.path.isfile(LOGINDATA): os.remove(LOGINDATA)
		loginData = {}
		url = 'https://user.tving.com/user/doLogin.tving'
		if type == 'CJONE': loginType = '10'
		else: loginType = '20'
		params = { 'userId' : user_id,
			   'password' : user_pw,
			   'loginType' : loginType }
		
		postdata = urllib.urlencode( params )
		request = urllib2.Request(url, postdata)
		response = urllib2.urlopen(request)
		cookie = response.info().getheader('Set-Cookie')
		for c in cookie.split(','):
			c = c.strip()
			if c.startswith('cs'): 
				loginData['p'] = c.split('=')[1].split(';')[0].replace('%3D', '=').replace('%3B', '&')
			if c.startswith('_tving_token'):
				loginData['t'] = c.split(';')[0]
			
		file = open(LOGINDATA, 'wb')
		pickle.dump(loginData, file)
		file.close()
		isLogin = True
	except Exception as e:
		LOG('<<<Exception>>> DoLogin: %s' % e)
		credential = 'none'
	return (isLogin, e)


def GetList( type, param, page ):
	has_more = 'N'
	try:
		result = []
		if type == 'WATCHED':
			for line in LoadWatchedList():
				info = {}
				tmp = line.strip().split('|')
				info['type'] = tmp[0]
				info['code'] = tmp[1]
				info['title'] = tmp[2]
				info['img'] = tmp[3]
				result.append(info)
			return 'N', result

		if type == 'LIVE': url = 'http://api.tving.com/v1/media/lives?pageNo=%s&pageSize=20&order=rating&adult=all&free=all&guest=all&scope=all' % page
		else: url = 'http://api.tving.com/v1/media/episodes?pageNo=%s&pageSize=18&adult=all&guest=all&scope=all&personal=N' % page
		if param is not None: url += param
		url += DEFAULT_PARAM			

		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		data = json.load(response, encoding="utf-8")
		
		for item in data["body"]["result"]:
			try:
				info = {}
				if type == 'LIVE':
					info['live_code'] = item["live_code"]
					info['channel_title'] = item['schedule']['channel']['name']['ko']
					info['episode_title'] = ' '
					info['img'] = 'http://image.tving.com/upload/cms/caic/CAIC1900/%s.png' % item["live_code"]
					if item['schedule']['episode'] is not None:
						info['episode_title'] = item['schedule']['episode']['name']['ko']
						if info['channel_title'].startswith('CH.') and len(item['schedule']['episode']['image']) > 0:
							info['img'] = 'http://image.tving.com' + item['schedule']['episode']['image'][0]['url']
					info['free'] = (item['schedule']['broadcast_url'][0]['broad_url1'].find('drm') == -1)
				else:
					info['program_code'] = item["program"]["code"]
					info['program_title'] = item["program"]["name"]["ko"]
					info['program_summary'] = item["program"]["synopsis"]["ko"]
					info['program_image'] = "http://image.tving.com" + item["program"]["image"][0]["url"]
					info['episode_code'] = item["episode"]["code"]
					info['episode_title'] = item["episode"]["name"]["ko"]
					info['episode_summary'] = item["episode"]["synopsis"]["ko"]
					info['episode_image'] = "http://image.tving.com" + item["episode"]["image"][0]["url"]
					info['stream'] = item["stream_support_info"]
					info['free'] = item["episode"]["free_yn"]
				result.append(info)
				#LOG('GetList %s' % info)
			except:
				pass
		has_more = data["body"]["has_more"]
	except Exception as e:
		LOG('<<<Exception>>> GetList: %s' % e)
		result = []
	return has_more, result

def GetURL(code, quality ):
	return GetBroadURL(code, quality)

def LoadWatchedList():
	try:
		f = open(LOCAL_PROGRAM_LIST, 'r', encoding='utf-8')
		result = f.readlines()
		f.close()
		return result
	except Exception as e:
		LOG('<<<Exception>>> LoadWatchedList: %s' % e)
		result = []
	return result

def SaveWatchedList( data ):
	try:
		result = LoadWatchedList()
		with open(LOCAL_PROGRAM_LIST, 'w', encoding='utf-8') as fw:
			#data = unicode(data + '\n')
			data = (data + '\n').decode('utf8')
			fw.write(data)
			num = 1
			for line in result:
				if line.find(data.split('|')[1]) == -1: 
					fw.write(line)
					num += 1
				if num == 100: break
	except Exception as e:
		LOG('<<<Exception>>> SaveWatchedList: %s' % e)
		pass
	return


def GetLoginData():
	try:
		file = open(LOGINDATA, 'rb')
		login = pickle.load(file)
		file.close()
	except Exception, e:
		LOG('<<<Exception>>> GetLoginData: %s' % e)
		login = []
	return login


