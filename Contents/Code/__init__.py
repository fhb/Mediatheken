# -*- coding: utf-8 -*-
import re, random
from PMS import *



####################################################################################################
NAME = "Mediatheken"
PLUGIN_PREFIX     = "/video/mediatheken"

THUMB	                = "icon-default2.png"
ART                     = "art-default.png"


CACHE_INTERVAL              = 3600
DEBUG                       = True

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "Mediatheken",THUMB, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  #HTTP.CacheTime = 3600
  MediaContainer.art        =R(ART)
  MediaContainer.title1 = NAME
  DirectoryItem.thumb       =R(THUMB)


####################################################################################################
def MainMenu():
	dir = MediaContainer(mediaType='items')
	encoded = unicode('http://appdrive.net/mediathek/adapter/?api_v=plesk-plugin-1.0&query=anne+will', 'utf-8')
	content = JSON.ObjectFromURL(encoded, values=None, headers={}, cacheTime=None)
	#dir.Append(Function(DirectoryItem(All,"Alle Sendungen")))
	
	dir.Append(Function(DirectoryItem(AlleSendungen,"Anne Will", thumb=content['image']), kanal="Anne Will", minlength=20))
	dir.Append(Function(DirectoryItem(AlleSendungen,"ARD Mittagsmagazin", thumb=None), kanal="ARD Mittagsmagazin", minlength=20))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Hart aber fair", thumb=None), kanal="Hart aber fair", minlength=20))
	dir.Append(Function(DirectoryItem(Kategorien,"Sendungen nach Kategorien", thumb=None)))
	
	return dir
	return MessageContainer("No items available", "There are no items available.")
####################################################################################################
def Kategorien(sender):
	dir = MediaContainer(mediaType='items')
	dir.title2="Kategorien"
	dir.Append(Function(DirectoryItem(AlleSendungen,"Aktuell", thumb=None), kanal="Aktuell", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Talkshow", thumb=None), kanal="Talkshow", minlength=20))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Dokumentation", thumb=None), kanal="Dokumentation", minlength=10))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Comedy/Kaberett", thumb=None), kanal="Comedy", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Kinder", thumb=None), kanal="Kinder", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Krimi", thumb=None), kanal="Krimi", minlength=15))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Magazin/Ratgeber", thumb=None), kanal="Magazin", minlength=5))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Nachrichten", thumb=None), kanal="Nachrichten", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Serie", thumb=None), kanal="Serie", minlength=15))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Show", thumb=None), kanal="Show", minlength=10))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Spielfilm", thumb=None), kanal="Film", minlength=30))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Wissen", thumb=None), kanal="Wissen", minlength=0))
	return dir
####################################################################################################

def AlleSendungen(sender, kanal, minlength):
	
	dir = MediaContainer(mediaType='items')
	dir.title2=kanal
	extractdir = MediaContainer(mediaType='items')
	encoded='http://appdrive.net/mediathek/adapter/?api_v=plesk-plugin-1.0&query='+String.Quote(kanal, usePlus=True)
	encoded = unicode(encoded, 'utf-8')
	content = JSON.ObjectFromURL(encoded, values=None, headers={}, cacheTime=None)
	extractexists=False
	if "fullEpisodeLength" in content:
		minlength=int(content['fullEpisodeLength'])
	else:
		minlength=int(minlength)
	numberofitems=len(content['items'])
	countfulllength=0
	countextract=0
	for i in range(len(content['items'])):
		durationstring=content['items'][i]['duration']
		if durationstring != "":
			if durationstring.count(":")==2:
				durationinhours=int(content['items'][i]['duration'][0:durationstring.find(":")])
				durationinminutes=int(content['items'][i]['duration'][durationstring.find(":")+1:durationstring[0:durationstring.find(":")].find(":")-2])
			else:
				durationinhours=0
				durationinminutes=int(content['items'][i]['duration'][0:durationstring.find(":")])
			durationinseconds=int(content['items'][i]['duration'][-2:])
			duration=durationinhours*3600000+durationinminutes*60000+durationinseconds*1000
		else:
			duration=None
		
		title=content['items'][i]['title']
		thumbnail=content['items'][i]['thumbnailLarge']
		timestamp=content['items'][i]['timestamp'][:-6]
		summary=content['items'][i]['description']
		summary=summary.encode('utf-8')
		datum=content['items'][i]['date']
		provider=date=content['items'][i]['provider']
		downloadParam=content['items'][i]['downloadParam']
		url=""
		clip=""
		webvideo=False
		quicktime=False
		if ("quicktime" in content['items'][i]) and (content['items'][i]['quicktime'] !=""):
			url=content['items'][i]['quicktime']
			quicktime=True
		elif downloadParam.find("www.videoportal.sf.tv") != -1:
				url=content['items'][i]['url']
				webvideo=True
		else:
			if downloadParam.find("--playpath") ==-1:
				clip=downloadParam[downloadParam.find("-r")+3:downloadParam.find("--")-1].strip('"')
				if clip.find("swr.fcod")>-1:
					url=clip
					clip=clip.partition("/")[2].partition("/")[2].partition("/")[2].partition("/")[2].partition("/")[2]
					url=url.replace(clip,"")  
				
				if clip.find("vod")>-1:
					url=clip[0:clip.find("vod")+3].strip('"')
					if clip.find(".mp4")>-1:
						clip="mp4:"+clip[clip.find("vod")+4:-4]
					elif clip.find(".flv")>-1:
						clip=clip[clip.find("vod")+4:-4]
				if clip.find("ard/tv")>-1:
					url=clip[1:clip.find("ard/tv")-1].strip('"')
					clip=clip[clip.find("ard/tv"):-1].strip('"')
				
			
				
			elif downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1].find("mp4:")==-1 and downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1].find(".mp4")==1:
				clip=downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1]
				url=downloadParam[downloadParam.find("--tcUrl")+8:downloadParam.find("--app")-1]
			
			else:		
				clip=downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1]
				url=downloadParam[downloadParam.find("--tcUrl")+8:downloadParam.find("--app")-1]
			##Polizeiruf-Fix (?sen.....)		
			if clip.find("?")>-1:
				clip=clip[0:clip.find("?")]
			clip=clip.encode('utf-8')
			clip=String.Quote(clip, usePlus=True)
			url=url.encode('utf-8')
			url=String.Quote(url, usePlus=True)
		if datum=="":
			datum="Unbekannt"
		if duration >= minlength*60000 or duration==None:
			if duration==None:
				durationstring="??"
			countfulllength=countfulllength+1
			Log("Dauer '"+durationstring+"'")
			Log(title+" - #"+str(i+1)+"/"+str(numberofitems))
			
			if quicktime:
				dir.Append(VideoItem(url,title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary, duration=duration, thumb=thumbnail))
				#dir.Append(Function(VideoItem(url,title=title)))

				Log("Quicktime-VideoItem "+str(VideoItem(url,title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary, duration=duration, thumb=thumbnail)))
			elif webvideo:
				dir.Append(WebVideoItem(url, title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary,thumb=thumbnail, art=None))
				Log("Webvideo "+url)
			else:
				Log("Url-String '"+url+"'")
				Log("Clip-String "+clip)
				dir.Append(RTMPVideoItem(url, clip, width=1280, height=720, live=False, title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary, duration=duration, thumb=thumbnail))
			Log ("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		
		else:
			extractexists=True
			countextract=countextract+1
			Log("Dauer '"+durationstring+"'")
			Log(title+" - #"+str(i+1)+"/"+str(numberofitems))
			Log("Url-String '"+url+"'")
			if quicktime:
				##Quicktime-Stream(RTSP) verfügbar:
				extractdir.Append(VideoItem(url,title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary, duration=duration, thumb=thumbnail))
				Log("Quicktime-VideoItem "+str(VideoItem(url,title=title, subtitle=datum+" "+durationstring, summary=provider+" - "+summary, duration=duration, thumb=thumbnail)))
			elif webvideo:
				dir.Append(WebVideoItem(url, title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary,thumb=thumbnail, art=None))
				Log("Webvideo "+url)
			else:
				##Nur Flash-Stream (RTMP) verfügbar:
				Log("Clip-String "+clip)
				extractdir.Append(RTMPVideoItem(url, clip, width=1280, height=720, live=False, title=title, subtitle=datum+" - Dauer: "+durationstring, summary=provider+" - "+summary, duration=duration, thumb=thumbnail))
			Log ("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

	Log("######################  Ingesamt "+str(countfulllength)+" Sendungen   ######################")
	Log("######################  Ingesamt "+str(countextract)+" Ausschnitte  ######################")
	if extractexists==True:
		dir.Append(Function(DirectoryItem(Extracts, "Ausschnitte", duration=None, summary="Alle Videos, die kürzer als "+str(minlength)+" Minuten sind."), dir=extractdir))
	
	#dir=dir.Sort("datum")
	return dir
####################################################################################################

####################################################################################################
def Extracts(sender, dir):
	
	dir=dir
	return dir

####################################################################################################
