import logging
import urllib2
import os
import sys
from xml.dom import minidom

NAME='YOUTUBE'
logging.basicConfig()
log = logging.getLogger(__name__)
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
    def retriveYoutubeToken(ID):
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
        token = Youtube.retriveYoutubeToken(ID)
        if token:
            videourl = "http://www.youtube.com/get_video?video_id=%s&fmt=22&t=%s" % (ID, token)
        return videourl

    @staticmethod
    def getHQVideourlByID(ID):
        videourl = None
        token = Youtube.retriveYoutubeToken(ID)
        if token:
            videourl = "http://www.youtube.com/get_video?video_id=%s&fmt=18&t=%s" % (ID, token)
        return videourl
        
    @staticmethod
    def run(serviceID, outFolder=None, outFilename=None):
        if not outFolder:
            outFolder = os.getcwd()
        if not outFilename:
            outFilename = serviceID
        
        data = None
        finished = False
        outFilePath = outFolder + os.sep + outFilename
        
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
        Youtube.run(sys.argv[1], sys.argv[2])
    else:
        print "youtube.py <Youtube ID> [<Out Folder>]"
        sys.exit(13)

