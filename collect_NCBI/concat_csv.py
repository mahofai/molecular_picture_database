import pandas as pd
import argparse
import hashlib


parser = argparse.ArgumentParser(description='')
parser.add_argument('--input_files', type=str, nargs='+', help='add multiple csv file paths')
parser.add_argument('--output_file', type=str, help='add multiple csv file paths', default = "concat.csv" )

if __name__ == "__main__":
    args = parser.parse_args()
    file_list = args.input_files
    #df1 = pd.read_csv(args.original_file, encoding="utf_8_sig", usecols=['Title', 'Authors', 'DOI', 'PMCID'])
    print("start!!!!!!")
    df1 = pd.DataFrame(columns=['ID', 'Title', 'Authors', 'DOI', 'PMCID', 'Downloaded'])
    for file in file_list:
        print("concating file:", file)
        # Read in the second CSV file as a dataframe
        df2 = pd.read_csv(file, encoding="utf_8_sig")
        if not "ID" in df2.columns:
            df2.insert(0, 'ID',"")
            # generate hash ID according to title of record
            for index, row in df2.iterrows():
                df2.at[index, 'ID'] = hashlib.sha224(row['Title'].encode()).hexdigest()[:20]

        if not "Downloaded" in df2.columns:
            df2.insert(len(df2.columns), 'Downloaded',"")
        df2= df2.loc[:, ['ID', 'Title', 'Authors', 'DOI', 'PMCID', 'Downloaded']]
        # Merge the dataframes while keeping only the non-duplicated rows from df2
        duplicated = pd.merge(df1, df2, on=['DOI'], how='inner')
        for index, row in duplicated.iterrows():
            df2.drop(df2[(df2['DOI'] == row['DOI'])].index, inplace=True)
        #drop all records without DOI
        df2 = df2.dropna(subset=['DOI'], how='all')


        # generate 
        df1 = pd.concat([df1,df2],axis=0)

    # Write the resulting merged dataframe to a new CSV file
    df1.to_csv(args.output_file, index=False)
