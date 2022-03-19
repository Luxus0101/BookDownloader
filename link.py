from bs4 import BeautifulSoup as bs
import requests
from googlesearch import search
from PyPDF2 import PdfFileReader, utils
from error_codes import ErrorCode as er, FileDownloadStatus as fd

class Link:
    def __init__(self, search, url):
        self.search = search
        self.url = url
        self.mark_for_revision = False
        self.download_status = fd.NOT_DOWNLOADED
        self.url_obj_info = None

    def setUrlObjInfo(self, info):
        self.url_obj_info = info

    def checkURL(self, link):
        return (link in self.url)

    def printLink(self):
        print("Query: %s | URL: %s | Acceptable?: %s | Download Status?: %s" % (self.search, self.url, self.url_obj_info != None, self.download_status.name))

    def download(self, option):
        page = None
        href = None
        file = None
        pdf_r = None
        i = 0
        #Open first link
        try:
            page = requests.get(self.url, allow_redirects=True)
        except requests.ConnectionError:
                return 0
        if(page == None): 
            return er.ERROR_DOWNLOADING_LINK
        
        #Download from accepted website
        if(option == 0):
            # Dive in the website until the final button is reached.
            # This part is dependent on each website, that is why the 
            # information is stored in the database, and it is passed
            # to the Link object
            for keyword in self.url_obj_info:
                i += 1
                #Obtain button link
                href = self.getButtonLink(page, keyword)
                print("Link %s obtained %s \n" % (i, href))

                #Error control
                if(href == None):
                    return er.ERROR_RETRIEVING_BUTTON_LINK

                #Open download button link
                try:
                    pdf_r = requests.get(href, allow_redirects=True)
                except requests.ConnectionError:
                    return er.ERROR_OPENING_BUTTON_LINK
                if(pdf_r == None): 
                    return er.ERROR_OPENING_BUTTON_LINK

            if(href.endswith('.pdf') == False):
                self.mark_for_revision = True

            self.download_status = fd.DOWNLOADED_FROM_ACCEPTED_WEBSITE
                
        #Download from PDF
        else:
            try:
                file = open(self.search+".pdf", "wb")
                file.write(page.content)
                file.close()
            except OSError:
                return er.ERROR_WRITING_NEW_PDF

            self.download_status = fd.DOWNLOADED_FROM_PDF
        
        #Here the future control for the number of pages in the downloaded pdf will be implemented
        #self.checkPDF()

        return er.OK

    #This function name is misleading in its use, must change
    def getStatus(self):
        return [self.search+".pdf", self.download_status]

    def getButtonLink(self, page, keyword):
        soup = bs(page.content, 'html.parser')
        data = None
        links = soup.findAll("a")
        for link in links:
            href = link.get("href")
            if(keyword in link.get_text()): return str(href)
                
        return None