import re
import csv
import argparse
import hashlib

parser = argparse.ArgumentParser(description='Extract data from text file and write to CSV')
parser.add_argument('input_file', type=str, help='path to input file')
parser.add_argument('csv_name', type=str, help='csv name')


if __name__ == "__main__":
	args = parser.parse_args()
	# Open the input file containing multiple blocks of text
	with open(args.input_file, mode='r', encoding="utf-8") as f:
		data = f.read()

	# Split the input file into individual blocks of text
	blocks = re.findall(r'\d+:\s(.+?PMCID.+?)\n', data, re.DOTALL)
	print(blocks[1])
	print(blocks[2])

	# Extract the relevant fields from each block of text
	results = []
	for block in blocks:
		#fields = re.findall(r'(.+?)\n(.+)\n.+?(\d{4}\s.*);\sPublished.+?:\s(.+)\n', block)
		# Extract title
		title = re.search(r'^.*?(?=\n)', block).group()
		print("TITLE:",title)

		# Extract authors
		authors = re.search(r'(?<=\n)[^\n]*(?=\n)', block).group()
		#authors = str(authors).split(",")
		print("authors:",authors)

		# Extract publish date
		publish_date = re.search(r'Published online (\d{4} \w{3} \d{1,2})\.', block)
		if publish_date:
			publish_date = publish_date.group(1)
		print("publish_date:",publish_date)

		# Extract DOI
		doi = re.search(r'doi:(.*?)\n', block)
		if doi:
			doi = doi.group(1)
			doi = doi[1:]
			if "Correction" in doi:
				correction_index = doi.index("Correction")
				doi = doi[:correction_index]
		print(doi)


		PMCID = re.search(r'PMCID:(\s+\w+)', block)
		if PMCID:
			PMCID = PMCID.group(1)
			PMCID = PMCID[1:]
		print(PMCID)

		ID = hashlib.sha224(str(title).encode()).hexdigest()[:20]

		results.append([ID, title, authors, publish_date, doi, PMCID])

	# Write the extracted fields to a CSV file by column
	with open(args.csv_name+'.csv', mode='w', newline='', encoding="utf_8_sig") as f:
		writer = csv.writer(f)
		writer.writerow(['ID', 'Title', 'Authors', 'Create Date', 'DOI', 'PMCID', 'Downloaded'])
		for row in results:
			writer.writerow(row)
