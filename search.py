#!/usr/bin/python3

from cmd import Cmd
import re
import requests
import urllib.parse
from colorama import Fore, Back, Style


class Manga:
    name = ""
    source = ""
    liste = []

    def __init__(self, name, liste):
        self.name = name
        self.liste = liste

    def choice(self):
        if self.liste == []:
            print(Fore.RED + "[-]" + Style.RESET_ALL, "Sorry, manga not found, you must try to add another source")
        elif len(self.liste) == 1:
            print(Fore.BLUE + "[+]" + Style.RESET_ALL, "Only one manga found")
            choice = input("Do you want to read it ? (Y/n): ").capitalize().strip()
            if choice == "Y" or choice == "":
                print("Well, here we gos")
        else:
            print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Many manga found")
            for i, manga in enumerate(self.liste):
                print("{:3d}: {} : {}".format(i, manga[1], manga[2]))
            choice = input("Pick your poison ? (Y/n): ").split()
            while(len(choice) != 1 and len(choice) != 2) or not self.betweenrange(choice, len(self.liste)):
                print(Fore.RED + "[-]" + Style.RESET_ALL, "You must pick 1 or 2 number(s) and the number(s) must be between 0 and {}".format(len(self.liste)-1))
                choice = input("Pick your poison ? (Y/n): ").split()
            print(Fore.GREEN + "[+]" + Style.RESET_ALL, "Nice, good choice: {}".format("-".join(choice)))


    def betweenrange(self, choice, size):
        for i in choice:
            if int(i) < 0 or int(i) >= size:
                return False
        return True

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
        source = MangaHere("http://mangahere.win/")
        manga = Manga(args, source.find(args))
        manga.choice()

    def do_quit(self, args):
        exit(0)

class MangaHere(Source):
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


            for i in names:
                #pass
                print(i)

            
        except requests.exceptions.RequestException as err:
            print(Fore.RED + "[-]" + Style.RESET_ALL, "Host {} not found".format(self._site))

        return names

    def search_page(self, site, search_re):
        response = requests.get(site)
        names = re.findall(search_re, response.text, re.DOTALL)
        return names


term = Terminal()
term.cmdloop()


# prochaine étape, parcourir toutes les pages s'il y en a plusieurs et enregistrer les liens et sites