from bs4 import BeautifulSoup as bs
import requests
from googlesearch import search
import csv
from PyPDF2 import PdfFileReader, utils
from time import sleep

MAX_RESULTS = 10
FILENAME = "status_query"

def searchForGoodWebs(webs_filename, results):
    webs = None
    webs_file = None
    with open(webs_filename, "r") as webs_file: webs = webs_file.read().splitlines()
    for link in results:
        for web in webs:
            if(web in link): return link
    return None

def searchForPDF(results):
    for link in results:
        if(link.endswith(".pdf")): return link
    return None

def getLinksFromPageWithString(soup, string):
    data = None
    links = soup.findAll("a")
    for link in links:
        href = link.get("href")
        for stri in string:
            if(stri in link.get_text()): return str(href)

    return None

def downloadPDF(query, url, depth):
    links_in_page = None
    page = None

    #Open first link
    try:
        page = requests.get(url, allow_redirects=True)
    except requests.ConnectionError:
        return 0
    if(page == None): return 0

    #If depth = 0, download the (PDF) document with no further processing and return
    if(depth == 0):
        print(depth)
        with open(query, "wb") as file:
            file.write(page.content)
        with open(query, "rb") as pdf_file:
            pdf_reader = None
            try:
                pdf_reader = PdfFileReader(pdf_file)
            except utils.PdfReadError:
                return 3

            #Condition to alert of possible wrong downloads
            if(pdf_reader.numPages <= 15): return 3
        return 2

    #Else get the link from page that contain the keywords 'PDF' or 'pdf' (high probability they are the download button)
    soup = bs(page.content, 'html.parser')
    href = getLinksFromPageWithString(soup, ['PDF', 'pdf'])
    print("First link obtained %s \n" % href)
    if(href == None): return 0
    pdf_r = None

    #Open download button link
    try:
        pdf_r = requests.get(href, allow_redirects=True)
    except requests.ConnectionError:
        return 0
    if(pdf_r == None): return 0

    #If link is a pdf file, download it and return
    if(href.endswith('.pdf') == True):
        file = open(query, "wb")
        file.write(pdf_r.content)
        file.close()
        return 1

    #Else repeat the last process for the button link

    else:
        pdf_soup = bs(pdf_r.content, 'html.parser')
        href = getLinksFromPageWithString(pdf_soup, ['PDF', 'pdf', 'Descargar', 'Download'])
        print("Second link obtained %s \n" % href)
        try:
            pdf_r = requests.get(href, allow_redirects=True)
        except requests.ConnectionError:
            return 0
        file = open(query, "wb")
        file.write(pdf_r.content)
        file.close()
        #If the downloaded file doesnt end in .pdf, mark it for revission
        return 1

def generateReport(filename, disponibility):
    if(disponibility == None or filename == None): return
    with open(filename, 'w', newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['Titulo','Autor','Status'])
        csvwriter.writerows(disponibility)

def txtFileMode(filename):
    disponibility_data = []
    with open(filename, 'r') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            print(line)
            titulo = line[0]
            autor = line[1]
            dispo_raw = [titulo, autor, 0]

            query = line[0] + " " + line[1] + " pdf"
            results = None
            try:
                results = search(query, num_results=MAX_RESULTS)
            except requests.ConnectionError:
                return 0

            print("\nSearching for %s\n" % query)
            url = searchForGoodWebs("webs.txt", results)
            if(url == None):
                url = searchForPDF(results)
                if(url != None):
                    dispo_raw[2] = downloadPDF(query, url, 0) #Use query as filename for pdfs
                    if(dispo_raw[2] == 0): print("Error downloading pdf")
                    else: print("pdf downloaded")

                else:
                    print("Couldnt find any PDF, skiping to next query\n")
                disponibility_data.append(dispo_raw)
                sleep(1)
                continue
            print("Downloading PDF from %s\n" % url)
            dispo_raw[2] = downloadPDF(query, url, 1)
            if(dispo_raw[2] == 0): print("Error downloading pdf")
            else: print("pdf downloaded")
            disponibility_data.append(dispo_raw)
            sleep(1)

    return disponibility_data

def manualMode():
    while(True):
        query = input("Busqueda: ")
        if(query == "exit"): break
        results = search(query, num_results=MAX_RESULTS)
        print("\nSearching for %s\n" % query)
        url = searchForGoodWebs("/home/luke/Desktop/Python/webs.txt", results)
        if(url == None):
            url = searchForPDF(results)
            if(url != None):
                status = downloadPDF(query, url, 0)
                if(status == 0): print("Error downloading pdf")
                else: print("pdf downloaded with status %s" % status)
            else:
                print("Couldnt find any explicit PDF, skipping to next query...\n")
            continue
        print("Downloading PDF from %s\n" % url)
        status = downloadPDF(query, url, 1)
        if(status == 0): print("Error downloading pdf")
        else: print("pdf downloaded with status %s" % status)

def main():
    disponibility = None
    data_doc = None
    mode = input("Configuracion (csv/libre): ")
    if(mode == "csv"):
        data_doc = input("Introduce el direcorio del archivo csv: ")
        disponibility = txtFileMode(data_doc)
        generateReport(FILENAME + "_" + data_doc, disponibility)
    elif(mode == "libre"):
        manualMode()
        generateReport(FILENAME, disponibility)
    else:
        print("Entrada incorrecta\n")
        return

main()
