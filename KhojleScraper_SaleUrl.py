# -*- coding: utf-8 -*-
from finefun import *
import subprocess
###########################################################################################
def writeHeader(fp,company_name):
    fp.write('Auction Name:%s' %company_name )
    fp.write('\n')
    titles = ["Category","Sub_Category","Ad website URL","Ad Title","Image Url","Ad Information","seller name","seller mailid","seller_number","Location","City"] 
    fp.write(','.join(titles))
    fp.write('\n')
###########################################################################################    
class Scrape:
    def __init__(self, auction_id, main_url, domain_url, download_images, scrapper_name, image_dir, f_p):
        self.auctionId = auction_id
        self.mainUrl = main_url
        self.domainUrl = domain_url
        self.downloadImages = download_images
        self.scrapperName = scrapper_name
        self.imageDir = image_dir
        self.fp = f_p
        self.run()

    def run(self):
        soup = get_soup(self.mainUrl)
        self.write_headers(soup)
        last_page=100000
        for page_no in range(1,last_page):
            soup=get_soup(self.mainUrl+"?p="+str(page_no))
            productDetails=''
            try:
                productDetails = soup.findAll("h3", {"class":"product-name"})
            except:
                pass
            for product in productDetails:
                Category=''
                Ad_Information=''
                seller_name=''
                Sub_Category=""
                seller_number,seller_mailid,title ,ad_details = "",'',"",""
                Location,city='',''
                Ad_website_link=''
                aTag = product.find("a")
                if aTag:
                    description_lot_list = []
                    detailPageUrl = self.domainUrl + aTag["href"]
                    print detailPageUrl,'__________________________________________'
                    try:
                        Ad_website_link=detailPageUrl
                    except:
                        pass
                    try:
                        detailPageSoup = get_soup(detailPageUrl)
                    except:
                        detailPageSoup = None
                        pass
                    
                    try:
                        Category_details=detailPageSoup.find("div",{"class":"breadcrumbs"}).getText().split("/")
                        Category=Category_details[-2].strip().replace('/','')
                        Sub_Category=Category_details[-1].strip()
                    except:
                        pass
                    try:
                        title=detailPageSoup.find("div",{"class":"product-name"}).find("h1").getText().strip().replace(',','')
                    except:
                        pass
                    try:
                        image_url=detailPageSoup.find("p",{"class":"product-image"}).find('img')["src"]
                    except:
                        pass
                    try:
                        seller_information=detailPageSoup.find("div",{"class":"customer-information"})
                    except:
                        pass
                    try:
                        seller_name=seller_information.find("div",{"class":"left"}).getText()
                    except:
                        pass
                    try:
                        seller_mailid=seller_information.find("li",{"class":"email"}).getText().strip().strip().replace(',','')
                    except:
                        pass
                    try:
                        seller_number=seller_information.find("li",{"class":"contact-no"}).getText().strip().strip().replace(',','')
                    except:
                        pass
                    try:
                        ad_seller_Information=detailPageSoup.findAll("td",{"class":"data"})
                        Location=ad_seller_Information[-1].getText().strip().replace(',','')
                        city=ad_seller_Information[-2].getText().strip().replace(',','')
                    except:
                        pass
                    try:
                        seller_name=seller_name.replace(seller_mailid,'').replace(seller_number,'')
                    except:
                        pass
                    fp.write(Category+","+Sub_Category+","+Ad_website_link+","+title+","+image_url +","
                             +Ad_Information+ ","+seller_name+','+seller_mailid+','+seller_number +','+Location +','+city + '\n')
   

       
    def write_headers(self, soup):

        company_name="khojle"
        writeHeader(self.fp,company_name)

        

    def url_cutter(self, url, no):
        try:
            return url.split("_")[0] + "_" + str(no)
        except:
            return url


    def getTextData(self,detailPageList,textName):
        try:
            textData = [item for index,item in enumerate(detailPageList) if textName.lower() in item.lower()][0]
            provenance = textData.strip().replace("\n","").replace("\r","").replace(">","")
            return provenance
        except:
            return ""

    def getIndexData(self,detailPageList,textName):
        try:
            indexNo = [index for index,item in enumerate(detailPageList) if textName.lower() in item.lower()][0]
            provenance = textName +" " + detailPageList[indexNo+1]
            provenance = provenance.strip().replace("\n","").replace("\r","")
            return provenance
        except:
            return ""

if __name__ == "__main__":
    mainUrl = sys.argv[1]
    try:
        auctionId = mainUrl.split("/")[-1]
    except:
        auctionId = ""
        pass
    domainUrl = "http://www.khojle.in"
    scrapperName = "khojle"
    downloadImages = True

    if sys.argv.__len__() > 2 and sys.argv[2] == "True":
        downloadImages = "True"

    imageDir = createImageDir(scrapperName, auctionId)
    datafile = getDataFilename(scrapperName, auctionId)
    fp = open(datafile, "w")

    Scrape(auctionId, mainUrl, domainUrl, downloadImages, scrapperName, imageDir, fp)
    fp.close()
    filename = datafile
    subprocess.call(['/bin/chmod', '-R', '777', '/home/ubuntu/webtools/uploads/datadump/'])
