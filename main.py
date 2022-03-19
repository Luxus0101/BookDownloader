from error_codes import ErrorCode as er, FileDownloadStatus as fd
from url_object import UrlObject
from link import Link
from report import Report

from bs4 import BeautifulSoup as bs
import requests
from googlesearch import search

MAX_RESULTS = 2
MAX_PDFS = 2
MAX_RESULTS = 10
FILENAME = "status_query"
OPT_ACCEPTED_WEBSITES = 1
OPT_PDFS = 1


class Main:

    def __init__(self, url_object_filename):
        #Storage object for the data about accepted websites
        self.url_object = UrlObject(url_object_filename)

        self.current_search = None

        #Filtered links obtained of the current search
        self.current_search_results = []

        #Final link chosen to be downloaded
        self.current_search_link_for_download = None
        
        #Report object that summarizes the session
        self.current_session_report = Report()

        self.current_option = 0
        self.verbose = True

    def printLinksInfo(link_list):
        for l in link_list:
            l.printLink()

    def printCurrentResultsInfo(self):
        for link in self.current_search_results:
            link.printLink()

    def searchResultsAsLinks(self, option):
        results = None
        if(option == 0):
            results = search(self.current_search + " pdf", num_results=MAX_RESULTS)
        elif(option == 1):
            results = search(self.current_search + " filetype:pdf", num_results=MAX_PDFS)
        
        if(results == None):
            return er.ERROR_CONNECTING_TO_SERVER

        for res in results:
            self.current_search_results.append(Link(self.current_search, res))

        return er.OK

    #For future reference, self.current_search_results usually returns empty from 
    # this function since the odds if finding a correct website are small
    def obtainFilteredNonPDFs(self):
        filtered_results = []
        #Obtain all the query's results
        self.searchResultsAsLinks(OPT_ACCEPTED_WEBSITES)
        if(self.current_search_results == None):
            return er.ERROR_CONNECTING_TO_SERVER

        for link in self.current_search_results:
            #Check if the link is part of the accepted websites, if it is append it with the web info
            if(self.url_object.checkLink(link) == True):
                filtered_results.append(link)

        self.current_search_results = filtered_results
        return er.OK

    def obtainInitialPDFs(self):
        #Obtain all the query's pdfs
        self.searchResultsAsLinks(OPT_PDFS)
        if(len(self.current_search_results) == 0):
            return er.ERROR_CONNECTING_TO_SERVER

        return er.OK

    def obtainDownloadLink(self): #Main class
        answer_link = None
        status = er.OK
        #If option == 0 -> try reputable sources
        if(self.current_option == 0):
            status = self.obtainFilteredNonPDFs()
            if(status != er.OK):
                return status
            
            if(len(self.current_search_results) == 0):
                return er.ERROR_SEARCH_RETURNED_NOTHING

            if(self.verbose == True):
                #Select the link for download
                self.printCurrentResultsInfo()
                self.current_search_link_for_download = self.current_search_results[int(input("Opcion: "))]

            else:
                #If verbose is not True, return the first link in the array
                self.current_search_link_for_download = self.current_search_results[0]

        #If option == 1 -> go straight for pdfs
        else:
            status = self.obtainInitialPDFs()
            if(status != er.OK):
                return status

            if(self.verbose == True):
                #Select the link for download
                self.printCurrentResultsInfo()
                self.current_search_link_for_download = self.current_search_results[int(input("Opcion: "))]

            else:
                #If verbose is not True, return the first link in the array
                self.current_search_link_for_download = self.current_search_results[0] 
            
        return er.OK

    ###Sketch for new downloadSearch function
    def downloadSearch(self):
        #Obtain the download link
        status = self.obtainDownloadLink()
        if(status != er.OK or self.current_search_link_for_download == None):
            return status
        
        self.current_search_link_for_download.printLink()
        #Download the current link and check for error
        status = self.current_search_link_for_download.download(self.current_option)
        if(status != er.OK):
            return status

        #Add the downloaded link to the current session report
        self.current_session_report.addDownloadReport(self.current_search_link_for_download)
        
        return er.OK
        
    ###Sketch for new searchLoop function (The aim is to reuse code as much as possible)
    def manualSearch(self):
        while(True):
            #Restart the parameters
            self.cleanParams()

            #Get the search from the user
            search = input("Busqueda: ")
            if(search == "exit"): break

            #Set the parameters of the current search
            self.current_option = int(input("Deseas descargar el pdf de paginas \"de confianza \" o prefieres descargar los dos primeros pdfs que aparezcan?(0 para lo primero, 1 para lo segundo):"))
            self.current_search = search

            #The manual mode always has verbose = True
            self.verbose = True

            #Download
            status = self.downloadSearch()
            
            #Error control, if the first search doesnt go well try the other option,
            #if it doenst go well either, return the error
            if(status != er.OK):
                print("Error: %s\nProbando la otra opcion" % status.name)
                #Change the option
                if(self.current_option == 0):
                    self.current_option = 1
                else:
                    self.current_option = 0

                status = self.downloadSearch()   
                if(status != er.OK):
                    print("Error: %s" % status.name)
                    return status
        self.current_session_report.generateReport('report.csv')

        return er.OK


    def automatedSearch(self):
        pass

    def getCurrentSearch(self):
        return self.current_search

    def getCurrentSearchResults(self):
        return self.current_search_results

    def cleanParams(self):
        self.current_search = None

        #Filtered links obtained of the current search
        self.current_search_results = []

        #Final link chosen to be downloaded
        self.current_search_link_for_download = None

        self.current_option = 0
        self.verbose = False

main = Main("/home/luke/Desktop/Python/Buscador de libros/webs.txt")
main.manualSearch()