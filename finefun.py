# -*- coding: cp1252 -*-
import os
import re
import shutil
import sys
from collections import OrderedDict
import urllib2
import urllib
from StringIO import StringIO
import gzip
import datetime
from sys import platform
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from BeautifulSoup import BeautifulSoup
import time
import requests
import json
import gc
from textblob import TextBlob
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
reload(sys)
sys.setdefaultencoding('utf8')

############Make the directory in python27 directory Name:  BrowersDriver and put geckodriver.exe in BrowersDriver directory##########
geckoPath = r'C:\Python27\BrowersDriver\geckodriver.exe'
###########################################################################

####################Lamda Functions##################
getFirstName = lambda x: " ".join(x[0:-1])
getLastName = lambda x,y: x[y]
checkArtistYearPatternSpace = lambda x: re.findall('(.*?)(\d{4} - \d{4})',x)
checkArtistYearPattern = lambda x: re.findall('(.*?)(\d{4}-\d{4})',x) #This check the artist name and start year and end year
checkArtistBirthPattern = lambda x: re.findall('(.*?)(b.\d{4})',x.lower()) #This check the artist name and birth with b.
yearExtract = lambda x: re.findall('(\d{4})', x)
checkDigitData = lambda x: re.findall(r"\([ /,.A-Za-z0-9_-]+\)", x)
X = lambda x : " ".join(x.replace(",","").replace('"',"").splitlines()) #This function remove coma and new lines
#######################################################


httpHeaders = {
    'User-Agent': r'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.162 Safari/535.19',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Connection': 'keep-alive'}

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

no_redirect_opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.HTTPSHandler(),
                                              NoRedirectHandler())  # ... and this is the "abnormal" one.
debug_opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))

def decodeGzippedContent(encoded_content):
    response_stream = StringIO(encoded_content)
    decoded_content = ""
    try:
        gzipper = gzip.GzipFile(fileobj=response_stream)
        decoded_content = gzipper.read()
    except:  # Maybe this isn't gzipped content after all....
        decoded_content = encoded_content
    return (decoded_content)

############This function return Page Soup Object#########################
def get_soup(pageUrl):
    gc.collect()
    pageRequest = urllib2.Request(pageUrl, None, httpHeaders)
    try:
        pageResponse = no_redirect_opener.open(pageRequest)
        headers = pageResponse.info()
        while headers.has_key("Location"):
            requestUrl = headers["Location"]
            if requestUrl == "/home.html":
                requestUrl = pageUrl+"home.html/"
            else:
                requestUrl = requestUrl
            pageRequest = urllib2.Request(requestUrl, None, httpHeaders)
            try:
                pageResponse = no_redirect_opener.open(pageRequest)
                headers = pageResponse.info()
            except:
                break
    except Exception, e:
        pass
        pageResponse = None

    if pageResponse == None:
        return None
    else:
        pageContent = decodeGzippedContent(pageResponse.read())
        pageSoup = BeautifulSoup(pageContent)
        gc.collect()
        return pageSoup

#######################This Function download the image#####################
def downloadImage(imageDir,downloadImages_True_False,product,lotNum,domainUrl):
    if downloadImages_True_False:
        if product:
            imgTag = product.find("img")
            if imgTag and imgTag.has_key('src'):
                if "http" in imgTag['src']:
                    imgLink = imgTag['src']
                else:
                    imgLink = domainUrl + imgTag['src']
            elif imgTag and imgTag.has_key('data-src'):
                if "http" in imgTag['data-src']:
                    imgLink = imgTag['data-src']
                else:
                    imgLink = domainUrl + imgTag['data-src']
	    elif imgTag and imgTag.has_key('data-lazy'):
                if "http" in imgTag['data-lazy']:
                    imgLink = imgTag['data-lazy']
                else:
                    imgLink = domainUrl + imgTag['data-lazy']

            if " " in imgLink:
                imgLink = imgLink.replace(" ", "%20")
            print imgLink, "KKKKKKKKKKKKKKKKKKKKKKKKK"
            imgLinkParts = imgLink.split("/")
            imgFilename = lotNum + ".jpg"  # imgLinkParts[imgLinkParts.__len__() - 1]
            imgRequest = urllib2.Request(imgLink, None, httpHeaders)
            try:
                imgResponse = no_redirect_opener.open(imgRequest)
                imgFileContent = imgResponse.read()
                fimg = open(imageDir + "/" + imgFilename, "wb")
                fimg.write(imgFileContent)
                fimg.close()
            except:
                pass

##############This Function Create image Directory#########################
def createImageDir(scrapperName, auctionId):
    baseDir = scrapperName.split('.')[0];
    baseDir_lowercase = baseDir.lower()
    try:
        imageDir = "/home/" +scraperDirectory[baseDir_lowercase] + "/images/"
    except:
        imageDir = "/home/" +baseDir_lowercase + "-scrape/images/"
    result = os.path.exists(imageDir)
    #print result
    if result == False:
        imageDir = imageDir+"%s"%auctionId
        os.makedirs(imageDir)
    else:
        if os.path.exists(imageDir+"%s"%auctionId):
            os.chdir(imageDir)
            shutil.rmtree("%s"%auctionId)
            os.makedirs("%s"%auctionId)
            imageDir=imageDir+"%s"%auctionId
        else:
            os.chdir(imageDir)
            os.makedirs("%s"%auctionId)
            imageDir=imageDir+"%s"%auctionId
    return imageDir
###############This Function Create the Directory and send the file path#################
def getDataFilename(scrapperName,auctionId):
    basepath = "/home/"
    scrappernNameBase = scrapperName.split('.')[0];
    print scrappernNameBase
    try:
        datafile = basepath + scraperDirectory[scrappernNameBase.lower()] + "/" + scrappernNameBase + "_" + auctionId + ".csv"
    except:
        datafile = basepath + scrappernNameBase.lower() + "-scrape/" + scrappernNameBase + "_" + auctionId + ".csv"
    print 'datafile', datafile
    return datafile
###########################################################################################
