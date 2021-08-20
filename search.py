#!/usr/bin/python3

from cmd import Cmd
import re
import requests
import urllib
from colorama import Fore, Back, Style
from requests_html import HTMLSession
import os

class Manga:
    name = ""
    source = ""
    liste = []

    def __init__(self, name, liste):
        self.name = name
        self.liste = liste

    def choice(self):
        choice = []
        if self.liste == []:
            print(Fore.RED + "[-]" + Style.RESET_ALL, "Sorry, manga not found, you must try to add another source")
        elif len(self.liste) == 1:
            print(Fore.BLUE + "[+]" + Style.RESET_ALL, "Only one manga found")
            choice = input("Do you want to read it ? (Y/n): ").capitalize().strip()
            if choice == "Y" or choice == "":
                print("Well, here we gos")
                result = [ i for i in self.liste]
            else:
                result = []
        else:
            print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Many manga found")
            for i, manga in enumerate(self.liste):
                print("{:3d}: {} : {}".format(i, manga[1], manga[2]))
            choice = input("Pick your poison ? (Y/n): ").split()
            while(len(choice) != 1 and len(choice) != 2) or not Manga.betweenrange(choice, len(self.liste)):
                print(Fore.RED + "[-]" + Style.RESET_ALL, "You must pick 1 or 2 number(s) and the number(s) must be between 0 and {}".format(len(self.liste)-1))
                choice = input("Pick your poison ? (Y/n): ").split()
            print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Nice, good choice: {}".format("-".join(choice)))
            result = [ self.liste[eval(i)] for i in choice]
        return result


    @staticmethod
    def betweenrange(choice, size):
        for i in choice:
            if eval(i) < 0 or eval(i) >= size:
                return False
        return True

class Manga_one(Manga):
    site = ""
    name = ""
    source = ""
    nbchaps = 0
    start = 0
    chapter_format = ""

    def __init__(self, liste):
        Manga.__init__(self, liste[0][1], liste[0])
        self.site = liste[0][0]
        self.name = urllib.parse.urlparse(self.site).path.split('/')[-1]
        self.source = urllib.parse.urlparse(self.site).hostname
        self.nbchaps = eval(liste[0][2])
        self.start = liste[0][3]
        self.find_chapter_format()

    def find_chapter_format(self):
        if self.source == "mangahere.win":
            self.chapter_format = MangaHere.chapter_format.replace("NAME", self.name)
            print(self.name, self.chapter_format)


    def display(self, beg, end):
        if beg == 0:
            beg = self.start
        num = beg
        print(self.chapter_format)
        while(num <= end):
            (path, num) = MangaHere.download(self.chapter_format, num)

    
        

class Source:
    _name = ""
    _site = ""
    _language = ""
    searchpath = ""
    # proxies={"http": 'http://127.0.0.1:8080'}
    proxies={}
    q = ""

    def __init__(self, site):
        self._site = site
        self._name = (urllib.parse.urlparse(site)).hostname

    def name(self):
        return self._name

    def findpath(self):
        print("Searching for a path for searching")
        try:
            response = requests.get(self._site)
            print(response.text)
        except requests.exceptions.RequestException as err:
            print(Fore.RED + "[-]" + Style.RESET_ALL, "Host {} not found".format(self._site))



class Terminal(Cmd):
    prompt = "yosh => "
    liste = []

    def do_help(self, args):
        print("Documented commands (type help <topic>):",
            "========================================", sep="\n")
        print("1: search <manga>")
        print("2: add    <source>")
        print("3: history")
        print(".: quit")

    def do_search(self, args):
        # Maybe check the history here at first
        source = MangaHere("http://mangahere.win/")
        manga = Manga(args, source.find(args))
        result = manga.choice()
        if len(result) == 1:
            choice = input("This manga contains {} chapters: what are your range: ".format(result[0][2])).split()
            print(result)
            while(len(choice) != 2) or not Manga.betweenrange(choice, eval(result[0][2])):
                print(Fore.RED + "[-]" + Style.RESET_ALL, "You must pick 2 numbers and the numbers must be between 0 and {}".format(result[0][2]))
                choice = input("Pick your poison ? (Y/n): ").split()
            print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Nice, good choice: {}".format("-".join(choice)))
            choice = [ eval(i) for i in choice]
            manga_one = Manga_one(result)
            manga_one.display(choice[0], choice[1])
        else:
            print("Not implemented yet")

    def do_read_one(self, args):
        liste = [i for i in os.listdir("/home/gabi/.Mangas/MangaSolo") if args in i]
        if len(liste) == 1:
            choice = input("You choosed to read {}. Is that right ? (Y/n): ".format(liste[0]))
            if choice == "Y" or choice == "":
                choice = liste[0]
            else:
                print("Bye")
                return 1
        else:
            for i, choix in enumerate(liste):
                print("{:3d}: {}".format(i, choix))
            choice = eval(input("Pick your poison ? (Y/n) : "))
            while(choice < 0 or choice >= len(liste)):
                print(Fore.RED + "[-]" + Style.RESET_ALL, "You must pick 1 number and the number must be between 0 and {}".format(len(liste)-1))
                choice = eval(input("Pick your poison ? (Y/n): "))
            print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Nice, good choice: {}".format(choice))
            choice = liste[choice]

        print(choice)
        # here we verify the historique
        chapters = os.listdir("/home/gabi/.Mangas/MangaSolo/{}".format(choice))
        chapters.sort()
        chapters = [(i, name) for (i, name) in enumerate(chapters)]
        print(Fore.BLUE + "[i]" + Style.RESET_ALL + " {} have been found".format(len(chapters)))
        for i in chapters:
            print("{:3d}: {}".format(i[0], i[1]))
        chap = eval(input("From where you want to start reading ? "))
        while(chap < 0 or chap >= len(chapters)):
            print(Fore.RED + "[-]" + Style.RESET_ALL, "You must pick 1 number and the number must be between 0 and {}".format(len(chapters)-1))
            chap = eval(input("Pick your poison ? (Y/n): "))
        print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Nice, good chap: {}".format(chap))
        print(chap)

        cmd = ""
        for i in range(chap, len(chapters)):
            cmd += "/home/gabi/.Mangas/MangaSolo/{}/{} ".format(choice, chapters[i][1])
        cmd = "eog " + cmd
        print(cmd)
        os.popen(cmd)


    def do_quit(self, args):
        exit(0)

class MangaHere(Source):
    chapter_format = "http://mangahere.win/NAME-chapter-NUM"

    def __init__(self, site):
        Source.__init__(self, site)
        self.searchpath = urllib.parse.urljoin(self._site, "search?q=")
        self.q = "q"


    def find(self, name):
        names = []
        search_re = r'<div class="list-truyen-item-wrap">\s*?<a href="(.*?)" title="(.*?)">.*?">Chapter ([0-9.]*?)</a>'
        try:
            response = requests.get(self.searchpath+name, proxies=self.proxies)
            
            names = re.findall(search_re, response.text, re.DOTALL)
            
            search_sentence = r'<li><a href="http://mangahere.win/search\?q={}&amp;page=(\d*?)">(\d*?)</a></li>'.format(name)
            pages = re.findall(search_sentence, response.text, re.DOTALL)
            if pages:
                numpages = int(pages[-1][0])

                #http://mangahere.win/search?q=b&page=2
                
                for i in range(2, numpages+1):
                    result = self.search_page(self.searchpath+"{}&page={}".format(name, i), search_re)
                    names.extend(result)
            
        except requests.exceptions.RequestException as err:
            print(Fore.RED + "[-]" + Style.RESET_ALL, "Host {} not found".format(self._site))

        names = [i + (0,) for i in names]

        for i in names:
            print(i)

        return names

    def search_page(self, site, search_re):
        response = requests.get(site, allow_redirects=True)
        names = re.findall(search_re, response.text, re.DOTALL)
        return names


    @staticmethod
    def download(site, num):
        if num == 0:
            site = site.replace("-chapter-NUM", "")
            site = site.split("/")
            site.insert(-1, "manga")
            site = "/".join(site)
            response = requests.get(site)
            search_re = r'<span><a  href="(.*?)"'
            names = re.findall(search_re, response.text, re.DOTALL)
            site = names[-1]
        else:
            site = site.replace("NUM", str(num))
        
        session = HTMLSession()
        response = session.get(site)
        response.html.render()
        search_re = r'id="arraydata" style="display:none">(.*?)</p>'
        names = re.findall(search_re, response.html.html, re.DOTALL)[0]
        names = names.split(',')
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)

        name = site.split("/")[-1]
        name = name.split("-")
        num = eval(name[-1])
        name = "-".join(name[:-2])
        
        search_re = r'<a class="loadAllImgPage pull-right next hide" href=".*?-([0-9.]*?)">'
        next_num = num
        next_num = re.findall(search_re, response.html.html, re.DOTALL)

        if num - int(num) != 0:
            path = "/home/gabi/.Mangas/MangaSolo/{}/Chapter_{:05.1f}".format(name, num)
        else:
            path = "/home/gabi/.Mangas/MangaSolo/{}/Chapter_{:03}".format(name, num)
        try:
            os.makedirs(path)
            for i, image in enumerate(names):
                name_picture = "{}/{}_{:05.1f}_{:03}.jpg".format(path, name, num, i)
                urllib.request.urlretrieve(image, name_picture)
            print(Fore.GREEN + "[+]" + Style.RESET_ALL + " Chapter {} downloaded successfully".format(num))

        except FileExistsError:
            print(Fore.LIGHTBLUE_EX + "[+]" + Style.RESET_ALL + " Chapter {} already exist".format(num))

        if next_num:
            next_num = eval(next_num[0])
        return (path, next_num)


term = Terminal()
term.cmdloop()
#term.do_search("kitsune")


"""
prochaine étape, télécharger et enregistrer les différents liens
https://www.activestate.com/resources/quick-reads/how-to-add-images-in-tkinter/
https://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/
"""
