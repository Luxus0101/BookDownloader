from link import Link
from error_codes import ErrorCode as er, FileDownloadStatus as fd

import csv

class Report:
    def __init__(self):
        self.download_reports = []
        #Total, Webs, PDFs, Not downloaded
        self.metadata = [0,0,0,0]

    def addDownloadReport(self, link):
        self.download_reports.append(link.getStatus())

    def analizeReports(self):
        for rep in self.download_reports:
            self.metadata[0] += 1
            self.metadata[rep[1].value] += 1

    def generateReport(self, filename):
        if(len(self.download_reports) == 0 or filename == None): return

        self.analizeReports()

        with open(filename, 'w', newline='') as f:
            csvwriter = csv.writer(f)

            csvwriter.writerow(['Numero de descargas','Porcentaje de webs aceptables','Porcentaje de pdfs', 'Porcentaje de errores de descarga'])            
            csvwriter.writerow(self.metadata)
            #En versiones futuras, habra que añadir un campo para las marcas de revision
            csvwriter.writerow(['Archivo','','Status'])
            csvwriter.writerows(self.download_reports)
        