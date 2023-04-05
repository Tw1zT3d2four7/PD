#import modules
from base import *
from ui.ui_print import *
import releases

name = "torrentio"

default_opts = [["sort","qualitysize"],["qualityfilter","480p,other,scr,cam,unknown"]]

session = requests.Session()

def get(url):
    try:
        response = session.get(url,timeout=60)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return response
    except:
        return None

def setup(cls, new=False):
    from settings import settings_list
    from scraper.services import active
    settings = []
    for category, allsettings in settings_list:
        for setting in allsettings:
            if setting.cls == cls:
                settings += [setting]
    if settings == []:
        if not cls.name in active:
            active += [cls.name]
    back = False
    if not new:
        while not back:
            print("0) Back")
            indices = []
            for index, setting in enumerate(settings):
                print(str(index + 1) + ') ' + setting.name)
                indices += [str(index + 1)]
            print()
            if settings == []:
                print("Nothing to edit!")
                print()
                time.sleep(3)
                return
            choice = input("Choose an action: ")
            if choice in indices:
                settings[int(choice) - 1].input()
                if not cls.name in active:
                    active += [cls.name]
                back = True
            elif choice == '0':
                back = True
    else:
        if not cls.name in active:
            active += [cls.name]

def scrape(query, altquery):
    from scraper.services import active
    scraped_releases = []
    if not 'torrentio' in active:
        return scraped_releases
    if altquery == "(.*)":
        altquery = query
    type = ("show" if regex.search(r'(S[0-9]|complete|S\?[0-9])',altquery,regex.I) else "movie")
    opts = []
    for opt in default_opts:
        opts += ['='.join(opt)]
    opts = '%7C'.join(opts)
    ep = ""
    if type == "show":
        s = (regex.search(r'(?<=S)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=S)([0-9]+)',altquery,regex.I) else None)
        e = (regex.search(r'(?<=E)([0-9]+)',altquery,regex.I).group() if regex.search(r'(?<=E)([0-9]+)',altquery,regex.I) else None)
        if s == None or int(s) == 0:
            s = 1
        ep += ':' + str(int(s))
        if e == None or int(e) == 0:
            e = 1
        ep += ':' + str(int(e))
    if regex.search(r'(tt[0-9]+)', altquery, regex.I):
        query = regex.search(r'(tt[0-9]+)', altquery, regex.I).group()
    if type == "show":
        url = 'https://torrentio.strem.fun/' + opts + '/stream/series/' + query + ep + '.json'
    else:    
        url = 'https://torrentio.strem.fun/' + opts + '/stream/movie/' + query + '.json'
    response = get(url)
    if not hasattr(response,"streams"):
        try:
            ui_print('[torrentio] error: ' + str(response))
        except:
            ui_print('[torrentio] error: unknown error')
        return scraped_releases
    for result in response.streams:
        title = result.title.split('\n')[0].replace(' ','.')
        size = (float(regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= GB)',result.title).group()) if regex.search(r'(?<=💾 )([0-9]+.?[0-9]+)(?= GB)',result.title) else 0)
        links = ['magnet:?xt=urn:btih:' + result.infoHash + '&dn=&tr=']
        seeds = (int(regex.search(r'(?<=👤 )([0-9]+)',result.title).group()) if regex.search(r'(?<=👤 )([1-9]+)',result.title) else 0)
        source = ((regex.search(r'(?<=⚙️ )(.*)(?=\n|$)',result.title).group()) if regex.search(r'(?<=⚙️ )(.*)(?=\n|$)',result.title) else "unknown")
        scraped_releases += [releases.release('[torrentio: '+source+']','torrent',title,[],size,links,seeds)]
    return scraped_releases