#!/usr/bin/env python
import logging
import urllib2
import os
import sys
import re
from xml.dom import minidom

logging.basicConfig()
log = logging.getLogger("youtube.downloader")
log.setLevel(logging.DEBUG)

def downloadFileByUrl(url):
   data = None
   try:
       f = urllib2.urlopen(url)
       data = f.read()
       f.close()
   except:
       log.error ("While downloading file %s: %s" %(url, sys.exc_value) )
   finally:
       return data


def dataToFile(filename, data):
   f = open(filename,'wb')
   f.write(data)
   f.close()


class Youtube(object):
    '''Youtube class is created to download video from youtube.com.
    '''
    @staticmethod
    def retriveYoutubePageToken(ID, htmlpage=None):
        """
        l="var fullscreenUrl = '/watch_fullscreen?fs=1&fexp=900142%2C900030%2C900162&iv_storage_server=http%3A%2F%2Fwww.google.com%2Freviews%2Fy%2F&creator=amiablewalker&sourceid=r&video_id=VJyTA4VlZus&l=353&sk=QtBR18Y95jsDyLXHgv9jbMu0ghb3MxoSU&fmt_map=34%2F0%2F9%2F0%2F115%2C5%2F0%2F7%2F0%2F0&t=vjVQa1PpcFPt0HhU0HkTG6A75-QxhAiV6WuMqB2a4r4%3D&hl=en&plid=AARnlkLz-d6cbsVe&vq=None&iv_module=http%3A%2F%2Fs.ytimg.com%2Fyt%2Fswf%2Fiv_module-vfl89178.swf&cr=US&sdetail=p%253Afriendfeed.com%2Feril&title=How To Learn Any Accent Part 1';"
        """
        if not htmlpage:
            url = "http://www.youtube.com/watch?v=%s" % ID
            htmlpage = urllib2.urlopen(url).read()
        match = re.search(r"var fullscreenUrl =.+&t=([^&]+)", htmlpage)
        if match:
            token = match.group(1)
        else:
            raise ValueError("Can't extract token from HTML page. Youtube changed layout. Please, contact to the author of this script")
        return token
    
    @staticmethod
    def retriveYoutubePageTitle(ID, htmlpage=None, clean=True):
        title = ID
        if not htmlpage:
            url = "http://www.youtube.com/watch?v=%s" % ID
            htmlpage = urllib2.urlopen(url).read()
        match = re.search(r"<title>(.+)</title>", htmlpage)
        if match:
            title = match.group(1)
            if clean:
                title = re.sub("[^a-z.]", "_", title.strip().lower())
        return title
    
    @staticmethod
    def retriveYoutubeTokenUsingAPI(ID):
        """Getting youtube token.
         token is need for building FLV URL"""
        youtube_token = None
        url = "http://www.youtube.com/api2_rest?method=youtube.videos.get_video_token&video_id=%s" % ID
        u = None
        try:
            log.debug("urlopen %s" % url)
            u = urllib2.urlopen(url)
        except:
            log.error("Can't retrive token using %s: %s" % (url, sys.exc_value))

        if u:
            # getting youtube token from XML
            rawxml = u.read()
            try:
                #log.debug("youtube XML answer: %s" % rawxml)
                xmldoc = minidom.parseString(rawxml)
                grammarNode = xmldoc.firstChild
                refNode = grammarNode.childNodes[0]
                pNode = refNode.childNodes[0]
                youtube_token = pNode.data
                log.debug("got youtube token: %s" % youtube_token)
            except:
                log.error("Can't exctract youtube token from XML '%s': %s" % (rawxml, sys.exc_value) )
        return youtube_token
    
    @staticmethod
    def getHDVideourlByID(ID):
        videourl = None
        token = Youtube.retriveYoutubePageToken(ID)
        if token:
            videourl = "http://www.youtube.com/get_video.php?video_id=%s&fmt=22&t=%s" % (ID, token)
        return videourl

    @staticmethod
    def getHQVideourlByID(ID):
        videourl = None
        token = Youtube.retriveYoutubePageToken(ID)
        if token:
            videourl = "http://www.youtube.com/get_video.php?video_id=%s&fmt=18&t=%s" % (ID, token)
        return videourl
        
    @staticmethod
    def run(serviceID, outFilePath=None):
        url = "http://www.youtube.com/watch?v=%s" % serviceID
        htmlpage = None
        if not outFilePath:
            htmlpage = urllib2.urlopen(url).read()
            title = Youtube.retriveYoutubePageTitle(serviceID, htmlpage, clean=True)
            outFolder = os.getcwd()
            outFilePath = os.path.join(os.getcwd(), title + '.mp4')
        
        data = None
        finished = False
        
        # if file exist on local node, do not download FLV one more.
        if os.path.isfile(outFilePath):
            log.warning("We already have %s. Not retrieving" % (outFilePath))
            finished = True
            return finished

        log.debug("Trying to get HD video")
        url = Youtube.getHDVideourlByID(serviceID)
        if not url:
            log.debug("Can't get HD video url")
        else:
            log.debug("Downloading %s -> %s" % (url, outFilePath))
            data = downloadFileByUrl(url)
            if data:
                log.info("saving %s into %s" % (serviceID, outFilePath))
                dataToFile(outFilePath, data)
                finished = True
                return finished
            else:
                log.debug("no data while downloading '%s'" % url)
        
        log.debug("Trying to get HQ video")
        url = Youtube.getHQVideourlByID(serviceID)
        if not url:
            log.debug("Can't get HQ video url")
        else:
            log.debug("Downloading %s -> %s" % (url, outFilePath))
            data = downloadFileByUrl(url)
            if data:
                log.info("saving %s into %s" % (serviceID, outFilePath))
                dataToFile(outFilePath, data)
                finished = True
                return finished
            else:
                log.debug("no data while downloading '%s'" % url)
        return finished


if __name__ == "__main__":
    log.setLevel(logging.DEBUG)
    if len(sys.argv) == 2:
        ID = sys.argv[1]
        Youtube.run(ID)
    elif len(sys.argv) == 3:
        Youtube.run(serviceID=sys.argv[1], outFilePath=sys.argv[2])
    else:
        print "%s <Youtube ID> [<Out Filename>]" % sys.argv[0]
        sys.exit(13)

