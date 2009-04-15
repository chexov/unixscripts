#!/usr/bin/env python
import logging
import urllib2
import os
import sys
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
    '''Class that can download get direct video URL
       and download it to your local storage
    '''
    @staticmethod
    def retriveYoutubeTokenUsingWatchpage(ID):
        """
        l="var fullscreenUrl = '/watch_fullscreen?fs=1&fexp=900142%2C900030%2C900162&iv_storage_server=http%3A%2F%2Fwww.google.com%2Freviews%2Fy%2F&creator=amiablewalker&sourceid=r&video_id=VJyTA4VlZus&l=353&sk=QtBR18Y95jsDyLXHgv9jbMu0ghb3MxoSU&fmt_map=34%2F0%2F9%2F0%2F115%2C5%2F0%2F7%2F0%2F0&t=vjVQa1PpcFPt0HhU0HkTG6A75-QxhAiV6WuMqB2a4r4%3D&hl=en&plid=AARnlkLz-d6cbsVe&vq=None&iv_module=http%3A%2F%2Fs.ytimg.com%2Fyt%2Fswf%2Fiv_module-vfl89178.swf&cr=US&sdetail=p%253Afriendfeed.com%2Feril&title=How To Learn Any Accent Part 1';"
        """
        url = "http://www.youtube.com/watch?v=%s" % ID
        html = urllib2.urlopen(url).read()
        for l in html.splitlines():
            token_start = l.find('&t=')
            if token_start > -1:
                token = l[token_start+3:].split('&')[0]
                return token
        return None


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
        token = Youtube.retriveYoutubeTokenUsingWatchpage(ID)
        if token:
            videourl = "http://www.youtube.com/get_video.php?video_id=%s&fmt=22&t=%s" % (ID, token)
        return videourl

    @staticmethod
    def getHQVideourlByID(ID):
        videourl = None
        token = Youtube.retriveYoutubeTokenUsingWatchpage(ID)
        if token:
            videourl = "http://www.youtube.com/get_video.php?video_id=%s&fmt=18&t=%s" % (ID, token)
        return videourl
        
    @staticmethod
    def run(serviceID, outFilePath=None):
        if not outFilePath:
            outFolder = os.getcwd()
            outFilePath = os.getcwd() + os.sep + serviceID
        
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
            log.debug("Downloading %s" % url)
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
            log.debug("Downloading %s" % url)
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

