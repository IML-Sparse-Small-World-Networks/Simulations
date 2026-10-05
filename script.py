import csv
import math
from collections import defaultdict
import matplotlib.pyplot as plt

def main(mu_, lambda__):
    times = defaultdict(list)
    ls = {}
    with open("bfs_data_.csv", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)                              # header
        for n, l, t in reader:
            times[int(n)].append(int(t))
            ls[int(n)] = float(l)

    ns = sorted(times)
    sample = [(sum(times[n]) / len(times[n])) / math.log(ls[n]) for n in ns]
    expected = 1 / (2 * math.log(mu_))

    plt.plot(ns, sample, 'o-', label='mean depth / log(l)')
    plt.axhline(expected, color='salmon', linestyle='--', label='1 / (2 log mu)')
    plt.xlabel('n')
    plt.ylabel('time / log(l)')
    plt.title('Average Time First Cycle | mu = ' + str(mu_) + ' | lambda = ' + str(lambda__))
    plt.legend()
    plt.savefig("first_cycle_time_mu=" + str(lambda__) )
    plt.clf()


'''   

import csv
import matplotlib.pyplot as plt
import math

def main(n_, l_i, p_i, lambda__, mu_, num_trials, num_ells):
        num_trials = num_trials
        numbers = []
        labels = []
        colors = []
        with open(f"bfs_data_.csv", mode='r', newline='', encoding='utf-8') as file:
                for i in range(num_ells):
                        reader = csv.reader(file)
                        blank = next(reader)
                        average_time = 0
                        for _ in range(num_trials):
                                row=next(reader)
                                average_time += int(row[1])
                        t_i = average_time / num_trials
                        t_i = t_i / math.log(l_i)
                        numbers.append(t_i)
                        constant_time =  1 / (2 * math.log(mu_))
                        numbers.append(constant_time)

        for i in range(1,num_ells + 1):
                labels.append(str("t_" + str(i)))
                labels.append(str("e_" + str(i)))
                colors.append('skyblue')
                colors.append('salmon')
        
        plt.bar(labels, numbers, color=colors)
        plt.title("Average Time of First Cycle ")
        plt.ylabel('time')
        plt.savefig("first_cycle_time")
        plt.clf()
        
        
                
if __name__ == "__main__":
        main(20)         




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

'''