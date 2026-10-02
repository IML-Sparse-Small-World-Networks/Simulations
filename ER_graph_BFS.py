import numpy as np
import csv
import math

import BFS as BFS
import script as script

def main(n_, l_, p_, lambda__, alpha_, mu_, l_i):
    # parameters
    n = n_                              # number of vertices
    l = l_                              # shortcut range
    p = p_                              # probability of shortcut Binom dist
    lambda_ = lambda__                  # new lambda var for alpha
    alpha = alpha_                      # shortcut constant multiplier passed directly to main function
    mu = mu_                            # eigenvalue of growth matrix

    # random graph
    rng = np.random.default_rng()
    rng = np.random.default_rng()
    adj = [[(i + 1) % n, (i - 1) % n] for i in range(n)]
    offsets = np.arange(2, int(l) + 1)
    for i in range(n):
        hits = offsets[rng.random(len(offsets)) < p]
        for d in hits:
            j = (i + d) % n
            adj[i].append(j)
            adj[j].append(i)

    depth, discovered = BFS.bfs(adj, 0)

    # weights

    # run BFS
    #edge_list, shortcut_list, cycle_list, t = BFS.bfs(A, n, 0)

    edge_list = []
    shortcut_list = []
    cycle_list = []

    # record trial data
    data = [n, l, p, lambda_, alpha, len(edge_list), len(shortcut_list), len(cycle_list), depth, mu]
    with open(f"bfs_data_{l_i}.csv", 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)
    

if __name__ == "__main__":
    '''
    Standarized the variables with "_" suffix to pass to main() function
    Two for loops. One for l and one for l**2
    Automatically outputs data to 'data.csv'
    Run 'script.py' to generate bar graphs
    If you change the '10' in the for loops below, change 
                    the '10' in the script.py for loops as well
    '''
    
    n_ = 5000                                   # number of vertices
    l_1 = 10                                    # shortcut range
    l_2 = int(n_ / math.log(n_))
    l_3 = math.sqrt(n_)
    # alpha_[alpha_num_l-num]
    alpha_1_1 = 1                               # shortcut constant multipliers passed directly to main function
    alpha_2_1 = l_1
    alpha_3_1 = l_1**2
    alpha_1_2 = 1
    alpha_2_2 = l_2
    alpha_3_2 = l_2**2
    alpha_1_3 = 1
    alpha_2_3 = l_2
    alpha_3_3 = l_2**2
    lambda__ = 2                               # new lambda var for alpha
    p_1 = lambda__/(2*l_1 - 2)                  # probability of shortcut Binom dist   
    p_2 = lambda__/(2*l_2 - 2)                  # probability of shortcut Binom dist   
    p_3 = lambda__/(2*l_3 - 2)                  # probability of shortcut Binom dist   
    mu_ = 1 + lambda__ + math.sqrt((lambda__**2) + (6 * lambda__) + 1)          # eigenvalue of growth matrix
    num_trials =  20                        # number trials

    ######################## l_1 ############################
    with open('bfs_data_l_1.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_1", "alpha_1_1", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_1, alpha_1_1, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])

    print("Starting alpha = 1 ...")
    
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_1, p_1, lambda__, alpha_1_1, mu_, "l_1")

    '''
    with open('bfs_data_l_1.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_1", "alpha_2_1", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_1, alpha_2_1, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])
    
    print("Starting alpha = l ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_1, p_1, lambda__, alpha_2_1, mu_, "l_1")

    with open('bfs_data_l_1.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_1", "alpha_3_1", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_1, alpha_3_1, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])
    
    print("Starting alpha = l**2 ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_1, p_1, lambda__, alpha_3_1, mu_, "l_1")
    '''

    ######################## l_2 ############################
    with open('bfs_data_l_2.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_2", "alpha_1_2", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_1, alpha_1_2, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])

    print("Starting alpha = 1 ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_2, p_2, lambda__, alpha_1_2, mu_, "l_2")

    '''
    with open('bfs_data_l_2.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_2", "alpha_2_2", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_2, alpha_2_2, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])

    print("Starting alpha = l ...")
    
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_2, p_2, lambda__, alpha_2_2, mu_, "l_2")

    with open('bfs_data_l_2.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_2", "alpha_3_2", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_2, alpha_3_2, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])
    
    print("Starting alpha = l**2 ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_2, p_2, lambda__, alpha_3_2, mu_, "l_2")
    '''

    ######################## l_3 ############################
    with open('bfs_data_l_3.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_3", "alpha_1_3", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_3, alpha_1_3, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])
    
    print("Starting alpha = 1 ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_3, p_3, lambda__, alpha_1_3, mu_, "l_3")

    '''
    with open('bfs_data_l_3.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_3", "alpha_2_3", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_3, alpha_2_3, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])

    print("Starting alpha = l ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_3, p_3, lambda__, alpha_2_3, mu_, "l_3")

    with open('bfs_data_l_3.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["l_3", "alpha_3_3", "mu_", "", "", "", "", "", "", ""])
        writer.writerow([l_3, alpha_3_3, mu_, "", "", "", "", "", "", "", ""])
        writer.writerow(["n","l","p","lambda","alpha","num_edges","num_shortcuts","num_cycle_edges","time","mu"])
    
    print("Starting alpha = l**2 ...")
    for i in range(num_trials):
        print(f"Starting run {i + 1}...")
        main(n_, l_3, p_3, lambda__, alpha_3_3, mu_, "l_3")
    '''


    print("Generating bar graphs ...")
    script.main(num_trials, n_)
    print("finished!")
    
