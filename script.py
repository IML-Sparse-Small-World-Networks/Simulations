import csv
n = 1000
average_path_len = 0
average_shortcuts = 0
with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader) 
        
        for row in reader:
                 average_path_len += int(row[5])
                 average_shortcuts += int(row[6])

print("average path length: ", average_path_len / 29)
print("average shortcuts:", average_shortcuts/29)