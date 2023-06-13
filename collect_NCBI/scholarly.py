from scholarly import ProxyGenerator
from scholarly import scholarly
import requests


if __name__ == "__main__":
    # Set up a ProxyGenerator object to use free proxies
    # This needs to be done only once per session
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    proxies = { "http":'http://67.219.101.157:8080', "https":'137.184.70.141:3128' }
    x = requests.get('https://twitter.com/dddddssd', proxies=proxies)
    print(x)
    
    # pg = ProxyGenerator()
    # success = pg.SingleProxy(http='67.219.101.157:8080', https='67.219.101.157:8080')
    # print("SUCCESS:",success)              # Print True here
    # scholarly.use_proxy(pg, pg)
    # Now search Google Scholar from behind a proxy
    # search_query = scholarly.search_pubs('Perception of physical stability and center of mass of 3D objects')
    # scholarly.pprint(next(search_query))
