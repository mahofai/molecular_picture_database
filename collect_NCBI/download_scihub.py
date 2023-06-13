import requests
import csv
import argparse
from pandas import *
import pandas as pd
import time
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re
from urllib.parse import urlparse
import concurrent.futures
import random
from collections import defaultdict

parser = argparse.ArgumentParser(description='download parser')
parser.add_argument('--input_csv', type=str, help='path to input csv')
parser.add_argument('--scihub_mirrors', type=str, nargs='+', help='scihub mirrors url')
parser.add_argument('--http_proxies', type=str, nargs='+', help='http proxies', default = "")
parser.add_argument('--https_proxies', type=str, nargs='+', help='https proxies', default = "")


def download(url, local_path,proxies):
    # download file in url to local path 
    # Set proxy here
    #proxies = {'https': '67.219.101.157:48245'}
    # sleep random seconds
    random_int = random.randrange(1, 4)
    time.sleep(random_int)

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
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

def get_download_link(source_url, doi, proxies):
    # access the scihub webpage with paper and fetch link in download button
    page_url = os.path.join(source_url,doi)
    print("page_url:",page_url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    time.sleep(2)
    response = requests.get(page_url, headers=headers, proxies=proxies)
    html_code = response.content
    html_string = html_code.decode("utf-8")
    # Define a regular expression pattern that matches the '?download=true' and its surrounding text to find download url
    pattern = r"['\"]([^'\"]*{}[^'\"]*)['\"]".format(re.escape('?download=true'))

    # Find all matches of the pattern in the HTML code string
    matches = re.findall(pattern, html_string)
    download_link = ""
    if matches:
        download_link = matches[0]
    return download_link

def fetch_pdfs(sub_dataframe, dir_index, source_url, proxies):
    # iterate subdataframe, access webpage and download file according to DOI

    #create sub dir
    current_dir = "./pdf/dir"+str(dir_index)+"/"
    if not os.path.isdir(current_dir):
        os.mkdir(current_dir)

    for i, row in sub_dataframe.iterrows():
        print("row:",row)
        try:
            doi = row['DOI']
            download_link =  get_download_link(source_url, doi, proxies)
            if not download_link:
                print("download link do not exist, pass!!!!")
                sub_dataframe.loc[i, "Downloaded"] = False
                continue
            is_absolute_url = bool(urlparse(download_link).netloc)
            if is_absolute_url and ("http" not in download_link):
                download_link = "https:"+download_link
            if not is_absolute_url:
                download_link ="https://sci-hub.st"+download_link
            print("download_link:", download_link)
            pdf_name = row["ID"] + ".pdf"
            local_path = os.path.join(current_dir, pdf_name)
            result = download(download_link, local_path, proxies)
            sub_dataframe.loc[i, "Downloaded"] = result

        except Exception as e:
            print(f"An exception occurred: {e}")
    return sub_dataframe

def update_csv(source_dir,csv_path):
    all_file_paths = []
    for root, subdir, filenames in os.walk(source_dir):
        for filename in filenames:
            all_file_paths.append(os.path.join(root, filename))
    id_list = [(os.path.basename(path)).split(".")[0] for path in all_file_paths]
    df = read_csv(csv_path, encoding='utf_8_sig')
    # Apply the mapping function to the "ID" column and assign the result to the "Downloaded" column
    print("df",df)
    # Use boolean indexing to get a filtered DataFrame that contains only the rows where the "ID" column is in id_list
    id_series = pd.Series({'a': id_list})
    print("id_series:",id_series)
    df1['Downloaded'] = False
    df1.loc[df1['ID'].isin(id_series), 'Downloaded'] = True
    print("df1",df1[:20])
    filtered_df = df[df['ID'].isin(id_list)]
    print("filtered_df",df['ID'].isin(id_list)[:10])
    filtered_df["Downloaded"] = True
    # find max index of filtered cell
    indexes = filtered_df.index
    max_index = indexes.max()
    print("max_index",max_index)
    # df.to_csv(args.input_csv, index=False)

def check_duplicated_files(source_dir):
    print("find duplicated files")
    all_file_paths = []
    for root, subdir, filenames in os.walk(source_dir):
        for filename in filenames:
            all_file_paths.append(os.path.join(root, filename))
    
    # Create a defaultdict object to store the base names as keys and lists of paths as values
    base_name_dict = defaultdict(list)
    for path in all_file_paths:
        # Get the base name of the file (without the directory or extension)
        base_name = os.path.splitext(os.path.basename(path))[0]
        if base_name in base_name_dict:
            base_name_dict[base_name].append(path)
        else:
            base_name_dict[base_name] = [path]
        # # Add the path to the list of paths for this base name
        # base_name_dict[base_name].append(path)
    duplicates_to_remove = []
    for base_name, paths in base_name_dict.items():
        if len(paths) > 1:
            duplicates_to_remove.append(paths.pop(0))
    # # Create a list of paths with duplicate base names
    # duplicate_paths = [path for paths in base_name_dict.values() if len(paths) > 1 for path in paths]

    print(duplicates_to_remove)
    return duplicates_to_remove

def remove_duplicated_record(csv_path):
    df = read_csv(csv_path, encoding='utf_8_sig')
    df.drop_duplicates(subset="ID", keep="first", inplace=True)
    df.to_csv(csv_path, index=False)
    

if __name__ == "__main__":
    args = parser.parse_args()

    # remove duplicated record from csv
    remove_duplicated_record(args.input_csv)

    # check and remove duplicated files
    duplicate_paths = check_duplicated_files("./pdf/")
    for duplicate_path in duplicate_paths:
        os.remove(duplicate_path)
        print("remove file:",duplicate_path)
        
    # update csv according to ./pdf/ content
    update_csv("./pdf/","/user/mahaohui/IMG2SMILES/collect_NCBI_pdf/output1.csv")

    # load csv to dataframe
    data = read_csv(args.input_csv, encoding='utf_8_sig')
    # if programe stop accidently, run from output.csv to continue
    if os.path.isfile("output.csv"):
        data = read_csv("output.csv", encoding='utf_8_sig')
        print(" reading output.csv!!!!!!!!!!!")
    # get download link
    scihub_mirrors=["https://sci-hub.ru", "https://sci-hub.st","https://sci-hub.se"]
    # set proxies here in case IP was blocked by scihub mirror
    proxies = {"https" : args.http_proxies, "http" : args.http_proxies}
    

    
    # identify the dir counter, 1000 records per dir
    checked_data = data[pd.notnull(data["Downloaded"])]
    checked_record_num = len(checked_data)
    if checked_record_num == len(data):
        print("finish download attemptions on all records")
        exit()
    dir_index = checked_record_num//1000
    # each task with df size 1000/mirrors_num
    sub_df_size = int(1000/len(scihub_mirrors))
    print("sub_df_size:",sub_df_size)
    


    # check ./pdf dir and update csv in case stop accidently cause error
    #updated_subdf = update_subdf("/user/mahaohui/IMG2SMILES/collect_NCBI_pdf/pdf/dir30",data)
    # print(updated_subdf)
    
    # # use threading pool
    # with concurrent.futures.ThreadPoolExecutor(max_workers=len(scihub_mirrors)) as executor:
        
    #     # load all tasks to thread pool
    #     tasks = []
    #     while checked_record_num <= len(data):
    #         random_int = random.randrange(0, len(scihub_mirrors))
    #         sub_df = data[checked_record_num:checked_record_num + sub_df_size]
    #         #print("sub_df:",sub_df)
    #         tasks.append(executor.submit(fetch_pdfs, sub_df, dir_index, scihub_mirrors[random_int], proxies))
    #         #print("append task")
    #         checked_record_num = checked_record_num + sub_df_size
    #         dir_index = checked_record_num//1000

    #     # Wait for the tasks to complete and print their results
    #     for future in concurrent.futures.as_completed(tasks):
    #         checked_data = pd.concat([checked_data,future.result()],axis=0)
    #         checked_data = checked_data.sort_index()
    #         data['Downloaded'] = checked_data['Downloaded']
    #         # store records in output.csv
    #         data.to_csv("output.csv", index=False)
    #     print("checked_data:",checked_data)
    
    # final_data = read_csv("output.csv" encoding='utf_8_sig')
    # final_data.to_csv(args.input_csv, index=False)
    # copy the output.csv to input csv and delete output.csv when finish programe


