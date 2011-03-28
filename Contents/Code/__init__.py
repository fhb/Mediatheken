# -*- coding: utf-8 -*-

#(c) Felix Bäcker

#Dieses Plugin gewährt euch Zugang zu allen wichtigen deutschen Mediatheken der Öffentlich-Rechtlichen Sender.
#Es basiert auf der freundlicherweise von appdrive.net zur Verfügung gestellten API.


import re, random



####################################################################################################
NAME = "Mediatheken"
PLUGIN_PREFIX     = "/video/mediatheken"

THUMB	                = "icon-default.png"
THUMB_PREFS				= "icon-prefs.png"
ART                     = "art-default.jpg"
ART_EMPTY				= "art-empty.jpg"
FAV_LIST				= "Favoriten"


CACHE_INTERVAL              = 3600
DEBUG                       = True

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "Mediatheken",THUMB, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  #PopulateInitialFavList()

  HTTP.CacheTime = 3600
  MediaContainer.art        =R(ART_EMPTY)
  MediaContainer.title1 	=NAME
  DirectoryItem.thumb       =R(THUMB)


####################################################################################################
def MainMenu():
	dir = MediaContainer(viewGroup='InfoList', mediaType='items', noCache=True)
	dir.Append(Function(DirectoryItem(AlleSendungen,"Aktuell", thumb=None), kanal="Aktuell", minlength=0))
	dir.Append(Function(DirectoryItem(Favoriten,"Favoriten", thumb=None)))

	if Prefs['fav1'] != None and Prefs['fav1'] != "None" and Prefs['fav1'] != ""and Prefs['fav1'] != "none":
		Log(Prefs['fav1'])
		fav1=unicode(Prefs['fav1'], 'utf-8')
		dir.Append(Function(DirectoryItem(AlleSendungen,Prefs['fav1'], thumb=None), kanal=fav1, minlength=0))
	if Prefs['fav2'] != None and Prefs['fav2'] != "None" and Prefs['fav2'] != ""and Prefs['fav2'] != "none":
		Log(Prefs['fav2'])
		fav2=unicode(Prefs['fav2'], 'utf-8')
		dir.Append(Function(DirectoryItem(AlleSendungen,Prefs['fav2'], thumb=None), kanal=fav2, minlength=0))
	if Prefs['fav3'] != None and Prefs['fav3'] != "None" and Prefs['fav3'] != ""and Prefs['fav3'] != "none":
		Log(Prefs['fav3'])
		fav3=unicode(Prefs['fav3'], 'utf-8')
		dir.Append(Function(DirectoryItem(AlleSendungen,Prefs['fav3'], thumb=None), kanal=fav3, minlength=0))
	#dir.Append(Function(DirectoryItem(AlleSendungen,"Anne Will", thumb=content['image']), kanal="Anne Will", minlength=20))
	#dir.Append(Function(DirectoryItem(AlleSendungen,"ARD Mittagsmagazin", thumb=None), kanal="ARD Mittagsmagazin", minlength=20))
	#dir.Append(Function(DirectoryItem(AlleSendungen,"Hart aber fair", thumb=None), kanal="Hart aber fair", minlength=20))

	dir.Append(Function(DirectoryItem(Kategorien,"Kategorien", thumb=None)))
	dir.Append(Function(DirectoryItem(MoeglicheFavoriten,"Alle Kanäle", thumb=None)))


	dir.Append(Function(InputDirectoryItem(Search, title=L('search'), prompt="Suche dein Video", thumb=R("icon-search.png"))))
   	dir.Append(PrefsItem(title="Einstellungen",subtile="",summary="",thumb=R(THUMB_PREFS)))

	
	return dir
	return MessageContainer("No items available", "There are no items available.")
####################################################################################################
def Kategorien(sender):
	menu = ContextMenu(includeStandardItems=False)
 	menu.Append(Function(DirectoryItem(AddChannel, "Favorit hinzufügen")))
	dir = MediaContainer(viewGroup='Details',contextMenu=menu, title2=sender.itemTitle)
	dir.Append(Function(DirectoryItem(AlleSendungen,"Talkshow", contextKey="Talkshow",contextArgs={}, thumb=None), kanal="Talkshow", minlength=20))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Dokumentation", contextKey="Dokumentation",contextArgs={}, thumb=None), kanal="Dokumentation", minlength=10))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Comedy/Kaberett", contextKey="Comedy",contextArgs={}, thumb=None), kanal="Comedy", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Kinder", contextKey="Kinder",contextArgs={}, thumb=None), kanal="Kinder", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Krimi", contextKey="Krimi",contextArgs={}, thumb=None), kanal="Krimi", minlength=15))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Magazin/Ratgeber", contextKey="Magazin",contextArgs={}, thumb=None), kanal="Magazin", minlength=5))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Nachrichten", contextKey="Nachrichten",contextArgs={}, thumb=None), kanal="Nachrichten", minlength=0))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Serie", contextKey="Serie",contextArgs={}, thumb=None), kanal="Serie", minlength=15))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Show", contextKey="Show",contextArgs={}, thumb=None), kanal="Show", minlength=10))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Spielfilm", contextKey="Film",contextArgs={}, thumb=None), kanal="Film", minlength=30))
	dir.Append(Function(DirectoryItem(AlleSendungen,"Wissen", contextKey="Wissen",contextArgs={}, thumb=None), kanal="Wissen", minlength=0))

	return dir
####################################################################################################
####################################################################################################
def Favoriten(sender):
	menu = ContextMenu(includeStandardItems=False)
 	menu.Append(Function(DirectoryItem(RemoveFav, "Favorit entfernen")))

  	dir = MediaContainer(viewGroup='InfoList', contextMenu=menu, noCache=True)
	#dir = MediaContainer(mediaType='items',contextMenu=menu)
	dir.title2="Favoriten"
	if not Data.Exists(FAV_LIST):
    		PopulateInitialFavList()
  	favList = Data.LoadObject(FAV_LIST)
  	for fav in favList:
  		fav=unicode(fav, 'utf-8')
		dir.Append(Function(DirectoryItem(AlleSendungen, fav, contextKey=fav,contextArgs={}, thumb=None), kanal=fav, minlength=0))
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
		#Nur wenn der gesamte Titel von Gänsefüßchen umfasst ist, sollen diese entfernt werden:
		if title[0] == '"' and title[-1:] == '"':
			title=title.strip('"')
		thumbnail=content['items'][i]['thumbnailLarge']
		timestamp=content['items'][i]['timestamp'][:-6]
		summary=content['items'][i]['description']
		summary=summary.encode('utf-8')
		datum=content['items'][i]['date']
		provider=date=content['items'][i]['provider']
		downloadParam=content['items'][i]['downloadParam']
		series=content['items'][i]['series'].strip('"')
		#Richtige Kombination von Serie und Titel:
		title=formatTitle(series,title,kanal)
		
		url=""
		clip=""
		webvideo=False
		quicktime=False
		
		#Betrifft vor allem ZDF-Beiträge:
		#Log("Quicktime Stream" + str())
		#Log(Prefs['zdfformat'])

		#Prefs["quicktime"] == 1 and 
		if Prefs['zdfformat']=="Quicktime" and ("quicktime" in content['items'][i]) and (content['items'][i]['quicktime'] !=""):
			url=content['items'][i]['quicktime']
			quicktime=True
		#Betrifft das Schweizer Fernsehen:
		elif downloadParam.find("www.videoportal.sf.tv") != -1:
				url=content['items'][i]['url']
				webvideo=True
		elif downloadParam.find("videos.arte.tv") != -1:
				url=content['items'][i]['url']
				webvideo=True
		else:
			#Betrifft alle Videos ohne Trennung von clip und url:
			if downloadParam.find("--playpath") ==-1:
				clip=downloadParam[downloadParam.find("-r")+3:downloadParam.find("--")-1].strip('"')
				if clip.find("MP4:")>-1:
					clip=clip.strip('"')
					url=clip[0:clip.find("MP4:")]
					clip=clip[clip.find("MP4:"):]
				if clip.find("mp4:")>-1:
					clip=clip.strip('"')
					url=clip[0:clip.find("mp4:")]
					clip=clip[clip.find("mp4:"):]
				
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
				
			
			#Betrifft alle Videos die den String mp4 im Pfad haben:
			elif downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1].find("mp4:")==-1 and downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1].find(".mp4")==1:
				clip=downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1]
				url=downloadParam[downloadParam.find("--tcUrl")+8:downloadParam.find("--app")-1]
			
			else:		
				clip=downloadParam[downloadParam.find("--playpath")+11:downloadParam.find("--tcUrl")-1]
				url=downloadParam[downloadParam.find("--tcUrl")+8:downloadParam.find("--app")-1]
			
			##Polizeiruf-Fix (?sen.....)		
			if clip.find("?")>-1 and url.find("arte")==-1:
				clip=clip[0:clip.find("?")]
			clip=clip.encode('utf-8')
			clip=String.Quote(clip, usePlus=True)
			url=url.encode('utf-8')
			url=String.Quote(url, usePlus=True)
		if datum=="":
			datum="Unbekannt"
			
		#Alle Videos hinzufügen, die entweder länger als die vorgegebene Mindestlänge
		#sind oder keine Dauer angegeben haben:
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

		#Alle Videos hinzufügen, die kürzer als die vorgegebene Mindestlänge sind:
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
	#Falls es einen Ausschnitt gibt:
	if extractexists==True:
		dir.Append(Function(DirectoryItem(Extracts, "Ausschnitte", duration=None, summary="Alle Videos, die kürzer als "+str(minlength)+" Minuten sind.")))
		#aus irgendeinem Grund geht die übergabe durch die funktion nicht mehr
		Dict['foo'] = extractdir

	#dir=dir.Sort("datum")
	return dir

####################################################################################################
def Extracts(sender):
	dir=Dict['foo']
	#dirs=dir
	return dir

####################################################################################################
####################################################################################################
def MoeglicheFavoriten(sender):
		menu = ContextMenu(includeStandardItems=False)
 		menu.Append(Function(DirectoryItem(AddChannel, "Favorit hinzufügen")))
		dir = MediaContainer(viewGroup='Details',contextMenu=menu, title2=sender.itemTitle)
		channellist=["Anne Will", "Neues aus der Anstalt", "Hart aber Fair"]
		encoded = unicode('http://appdrive.net/mediathek/channels/list/', 'utf-8')
		content = JSON.ObjectFromURL(encoded, values=None, headers={}, cacheTime=3600)
		for channel in content:
			if channel.has_key('image'): 
				dir.Append(Function(DirectoryItem(AlleSendungen, channel['name'], contextKey=channel['name'],contextArgs={}, thumb=channel['image']), kanal=channel['name'], minlength=0))			
			else:
				dir.Append(Function(DirectoryItem(AlleSendungen, channel['name'], contextKey=channel['name'],contextArgs={}, thumb=None), kanal=channel['name'], minlength=0))
		
		#dir.Append(Function(PopupDirectoryItem(AddChannelMenu, title="Anne Will")))
		#dir.Append(Function(PopupDirectoryItem(AddChannelMenu, title="Neues aus der Anstalt")))
		#dir.Append(Function(PopupDirectoryItem(AddChannelMenu, title="Hart aber Fair")))
		#for channel in channellist:
		#	dir.Append(Function(DirectoryItem(AlleSendungen, channel, contextKey=channel,contextArgs={}, thumb=None), kanal=channel, minlength=0))

		#dirs=dir
		return dir

####################################################################################################
def AddChannelMenu(sender):
    	dir = MediaContainer()
    	dir.Append(Function(DirectoryItem(AddChannel, "Füge Kanal '"+sender.itemTitle+"' hinzu"), query=sender.itemTitle))
    	return dir
####################################################################################################
    
def Search(sender, query):
  #callback = HTTP.Request(AMT_SEARCH_URL % String.Quote(query)).content
  #if callback is None: return None
 # callback = callback.lstrip("searchCallback(")[:-3]
  #d = JSON.ObjectFromString(callback)
  dir = MediaContainer(title1="Search", title2=sender.itemTitle)
  #for item in d["results"]:
   # if item["location"].find("phobos.apple.com") == -1:
    #  thumb = AMT_SITE_URL + item["poster"]
     # dir.Append(Function(VideoItem(getVideo, title=item["title"], thumb=thumb), url=AMT_SITE_URL + item["location"]))
  #if len(dir) == 0:
  dir.Append(DirectoryItem("%s/search" % PLUGIN_PREFIX, "(No Results)", ""))
  return dir

####################################################################################################
####################################################################################################

#####Funktionen:
####################################################################################################
def PopulateInitialFavList():
	if not Data.Exists(FAV_LIST):
    		favList = ["Anne Will", "Hart aber Fair"] 
    		Data.SaveObject(FAV_LIST, favList)

####################################################################################################
#########################################################
def AddChannel(sender, **key):
	if key !=None and key!= "":
		for i in key:
			query=key[i]
			Log(query)
	else:
		Log(sender.itemTitle[sender.itemTitle.find("Füge Kanal '")+13:sender.itemTitle.find("' hinzu")])
		query=sender.itemTitle[sender.itemTitle.find("Füge Kanal '")+13:sender.itemTitle.find("' hinzu")]
	if not Data.Exists(FAV_LIST):
    		PopulateInitialFavList()
	favList = Data.LoadObject(FAV_LIST)
	if query not in favList:
			favList.append(query)
			Data.SaveObject(FAV_LIST, favList)
			message = L('successfull')
			return MessageContainer("Hinzufügen", message)
	else:
			return MessageContainer("Hinzufügen gescheitert!", "Existiert bereits")
    

#########################################################
####################################################################################################
#########################################################
def RemoveFav(sender, key, **kwargs):
    favList = Data.LoadObject(FAV_LIST)
    favList.remove(key)
    Data.SaveObject(FAV_LIST, favList)
    
#########################################################
#Richtige Kombination von Serie und Titel:

def formatTitle(series,title,kanal):
	series=series
	title=title
	kanal=kanal
	var1=False
	if (kanal == "Aktuell") or (kanal == "Talkshow") or (kanal == "Dokumentation") or (kanal == "Comedy")  or (kanal == "Kinder")  or (kanal == "Krimi")  or (kanal == "Magazin")  or (kanal == "Nachrichten")  or (kanal == "Serie")  or (kanal == "Show")  or (kanal == "Film")  or (kanal == "Wissen"):	
			if series !="" and title.find("Sendung vom") !=-1:
				Log("++++Titelveränderung 3 (Sendung vom)++++")
				title=title[title.find("Sendung vom")+12:]
				var1=True
			m1=re.findall('vom [0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4}',title)
			m2=re.findall('vom [0-9]{1,2}.*[0-9]{2,4}',title)
			if m2!=[] or m1 != []:
				Log("++++Titelveränderung 1 (vom bei heuteshow)++++")				
				series=title[0:title.find("vom")]
				title=title[title.find("vom ")+3:]
				var1=True
			m=re.findall('".*-.*" \([0-9]{1,4}\)',title)
			if m != []:
				Log("++++Titelveränderung 2 (strip() bei Lena..)++++")
				title=title[0:title.find("(")-1].strip('"')+" "+title[title.find("("):]
				#title=title.replace('"','')
				var1=True
			if series.find("Reportage / Dokumentation") !=-1:
				Log("++++Titelveränderung 4 (Reportage/Dokumentation)++++")
				series=series[series.find("Reportage / ")+12:]	
				var1=True
			if title.find(series) == -1:
				title=series+" - "+title
				Log("++++Serie und Titel zusammengefügt++++")
			elif title.find(": ")!=-1:
				Log("++++Titelveränderung 5(replace(:, -) + strip()++++")
				Log(series)
				Log(title)
				Log(title.find(series))
				title=title.replace(": "," - ")
				title=title[0:title.find(" - ")]+" - "+title[title.find(" - ")+3:].strip('"')
				var1=True
	if var1 ==False:	
		Log("++++Titelveränderung KEINE++++")
	return title
		