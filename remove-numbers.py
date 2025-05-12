import csv
import re

input_file = 'final_sentences.csv'
output_file = 'filtered.csv'

def is_valid_row(row):
    for cell in row:
        text = cell.strip()
        if re.search(r'\d', text):           
            return False
        if len(text.split()) < 5:            
            return False
        if '-' in text or '()' in text:     
            return False
    return True

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

    for row in reader:
        stripped_row = [cell.strip() for cell in row]
        if is_valid_row(stripped_row):
            writer.writerow(stripped_row)

print("Cleaned rows saved to", output_file)
