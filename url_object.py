from error_codes import ErrorCode as er
class UrlObject:
    def __init__(self, urls_file):
        with open(urls_file, "r") as webs_file: 
            webs = webs_file.read().splitlines()
        self.pairs_list = []
        for w in webs:
            self.pairs_list.append(w.split(","))
    
    def checkLink(self, link):
        for pair in self.pairs_list:
            if(link.checkURL(pair[0]) == True):
                link.setUrlObjInfo(pair[1])
                return True
        return False

