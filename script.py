import csv
import pandas as pd
import matplotlib.pyplot as plt

n = 1000
average_path_len = 0
average_shortcuts = 0

with open('data.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader) 
        mu1 = next(reader)
        for i in range(100):
                row=next(reader)
                average_path_len = int(row[5])
                average_shortcuts += int(row[6])

        labels = ['average_path_len', 'average_shortcuts']
        numbers = [average_path_len, average_shortcuts]
        plt.bar(labels, numbers, color=['skyblue', 'salmon'])
        plt.title('Bar Graph with Three Numbers')
        plt.xlabel('mu = (l * alpha) / n')
        plt.ylabel('Values')
        plt.savefig("mu1")
        
        ######################## second mu ############################
        average_path_len = 0
        average_shortcuts = 0
        mu2 = next(reader)
        for i in range(100):
                        row=next(reader)
                        average_path_len += int(row[5])
                        average_shortcuts += int(row[6])

        labels = ['average_path_len', 'average_shortcuts']
        numbers = [average_path_len, average_shortcuts]
        plt.bar(labels, numbers, color=['skyblue', 'salmon'])
        plt.title('Bar Graph with Three Numbers')
        plt.xlabel('mu = (l * alpha) / n')
        plt.ylabel('Values')
        plt.savefig("mu2")
        
                         




#df = pd.read_csv('data.csv', skiprows=range(1,2), nrows=100)
#print(df)

#df.plot(x="n", y=["len_path", "shortcut_edges_taken"], kind="bar")

# 3. Display the chart
#plt.ylabel("Units Sold")
#plt.title("Sales Comparison")
#plt.xticks(rotation=0)  # Keeps category names horizontal
#plt.show()

#print("average path length: ", average_path_len / 29)
#print("average shortcuts:", average_shortcuts/29)