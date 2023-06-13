import requests
import csv
import argparse
from pandas import *
import pandas as pd
import time
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

parser = argparse.ArgumentParser(description='download parser')
parser.add_argument('--input_csv', type=str, help='path to input csv')

def download(url, local_path):
    # Set proxy here
    #proxies = {'https': '67.219.101.157:48245'}
    proxies = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])

    with requests.Session() as session:
        session.proxies = proxies
        session.headers = headers
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        try:
            response = session.get(url, stream=True)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            print(f"File downloaded to {local_path}")
        except Exception as e:
            print(f"Error downloading file: {e}")

def download1(url,local_path):
    # set proxy here
    #proxies = {'https': '67.219.101.157:48245'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
            print(f"File downloaded to {local_path}")
    else:
        print(response.content)
        print("Error: could not download file")

if __name__ == "__main__":
    args = parser.parse_args()
    data = read_csv(args.input_csv,  encoding='utf_8_sig')
    # find uncheck records 
    checked_data = data[pd.notnull(data["Downloaded"])]
    unchecked_data = data[pd.isnull(data["Downloaded"])]
    
    print("columns:",data.columns)
    dois = unchecked_data['DOI'].tolist()
    IDs = unchecked_data['ID'].tolist()
    checked_record_num = len(checked_data)
    print("checked_record_num:",checked_record_num)
    current_dir_index = checked_record_num//1000
    current_dir = "./pdf/dir"+str(current_dir_index)+"/"
    print("current_dir:",current_dir)
    
    for i in range(len(dois)):
        doi = dois[i]
        print(doi)
        url = 'https://sci.bban.top/pdf/'+str(doi)+'.pdf?download=true'
        current_dir = "./pdf/dir"+str((i+checked_record_num)//1000)+"/"
        if not os.path.isdir(current_dir):
            os.mkdir(current_dir)
        pdf_name = IDs[i] + ".pdf"
        local_path = os.path.join(current_dir, pdf_name)
        #download file from url
        download(url,local_path)
        time.sleep(1)
        if os.path.isfile(local_path):
            unchecked_data.loc[checked_record_num + i, "Downloaded"] = True
            print("finished downloading",checked_record_num + i)
        else:
            unchecked_data.loc[checked_record_num + i, "Downloaded"] = False
            print("could not download file...",checked_record_num + i)
        #update csv 
        new_data = pd.concat([checked_data,unchecked_data],axis=0)
        new_data.to_csv(args.input_csv, index=False)

