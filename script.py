import csv
import matplotlib.pyplot as plt
import math

def main(num_trials_, n_):
        num_trials = num_trials_
        with open('bfs_data_l_1.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                ######################## l_1 alpha_1 ############################
                blank = next(reader)
                l1 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_1 = average_time / num_trials
                #expected_cycle_time_l1 = math.log(float(l1[0])) / (2 * math.log(float(l1[2])))
                expected_cycle_time_l1 = math.log(n_) / (2 * math.log(float(l1[2])))

                '''
                ######################## l_1 alpha_2 ############################
                blank = next(reader)
                l2 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_2 = average_time / num_trials
                expected_cycle_time_l2 = math.log(float(l2[0])) / (2 * math.log(float(l2[2])))
                
                ######################## l_1 alpha_3 ############################
                blank = next(reader)
                l3 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_3 = average_time / num_trials
                expected_cycle_time_l3 = math.log(float(l3[0])) / (2 * math.log(float(l3[2])))
                print(expected_cycle_time_l3)
                '''

                labels = ['t_1', 'expected_t_1']
                numbers = [t_1, expected_cycle_time_l1]
                plt.bar(labels, numbers, color=['skyblue', 'salmon', 'skyblue', 'salmon', 'skyblue', 'salmon'])
                plt.title("Average Time of First Cycle ")
                plt.ylabel('time')
                plt.savefig("l_1")
                plt.clf()
                
        with open('bfs_data_l_2.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                ######################## l_2 alpha_1 ############################
                blank = next(reader)
                l1 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_1 = average_time / num_trials
                #expected_cycle_time_l1 = math.log(float(l1[0])) / (2 * math.log(float(l1[2])))
                expected_cycle_time_l1 = math.log(n_) / (2 * math.log(float(l1[2])))
                
                '''
                ######################## l_2 alpha_2 ############################
                blank = next(reader)
                l2 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_2 = average_time / num_trials
                expected_cycle_time_l2 = math.log(float(l2[0])) / (2 * math.log(float(l2[2])))

                ######################## l_2 alpha_3 ############################
                blank = next(reader)
                l3 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_3 = average_time / num_trials
                expected_cycle_time_l3 = math.log(float(l3[0])) / (2 * math.log(float(l3[2])))
                print(expected_cycle_time_l3)
                '''

                labels = ['t_1', 'expected_t_1']
                numbers = [t_1, expected_cycle_time_l1]
                plt.bar(labels, numbers, color=['skyblue', 'salmon', 'skyblue', 'salmon', 'skyblue', 'salmon'])
                plt.title("Average Time of First Cycle ")
                plt.ylabel('time')
                plt.savefig("l_2")
                plt.clf()
                

        with open('bfs_data_l_3.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                ######################## l_3 alpha_1 ############################
                blank = next(reader)
                l1 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_1 = average_time / num_trials
                #expected_cycle_time_l1 = math.log(float(l1[0])) / (2 * math.log(float(l1[2])))
                expected_cycle_time_l1 = math.log(n_) / (2 * math.log(float(l1[2])))

                '''
                ######################## l_3 alpha_2 ############################
                blank = next(reader)
                l2 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_2 = average_time / num_trials
                expected_cycle_time_l2 = math.log(float(l2[0])) / (2 * math.log(float(l2[2])))

                ######################## l_3 alpha_3 ############################
                blank = next(reader)
                l3 = next(reader)
                blank = next(reader)
                average_time = 0
                for _ in range(num_trials):
                        row=next(reader)
                        average_time += int(row[8])
                t_3 = average_time / num_trials
                expected_cycle_time_l3 = math.log(float(l3[0])) / (2 * math.log(float(l3[2])))
                print(expected_cycle_time_l3)
                '''

                labels = ['t_1', 'expected_t_1']
                numbers = [t_1, expected_cycle_time_l1]
                plt.bar(labels, numbers, color=['skyblue', 'salmon', 'skyblue', 'salmon', 'skyblue', 'salmon'])
                plt.title("Average Time of First Cycle ")
                plt.ylabel('time')
                plt.savefig("l_3")
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