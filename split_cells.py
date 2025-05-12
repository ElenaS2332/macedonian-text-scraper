import csv

input_file = 'filtered.csv'
output_file = 'output_split.csv'

def process_row(row):
    new_rows = []
    max_lines = max(cell.count('\n') for cell in row)
    
    for i in range(max_lines + 1):  
        new_row = []
        for cell in row:
            cell_lines = cell.split('\n')  
            if len(cell_lines) > i:
                new_row.append(cell_lines[i])  
            else:
                new_row.append('')  
        new_rows.append(new_row)
    
    return new_rows

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        new_rows = process_row(row)
        for new_row in new_rows:
            writer.writerow(new_row)

print(f"Processed CSV with split cells saved to {output_file}")
