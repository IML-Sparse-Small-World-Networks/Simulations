import numpy as np
import csv
import math

import BFS as BFS
import script as script

def main(n_, l_, p_, lambda__, mu_, writer):
    # parameters
    n = n_                              # number of vertices
    l = l_                              # shortcut range
    p = p_                              # probability of shortcut Binom dist
    lambda_ = lambda__                  # new lambda var for alpha
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

    # record trial data    
    writer.writerow([n, l, depth])  


if __name__ == "__main__":
    '''
    Standarized the variables with "_" suffix to pass to main() function
    Two for loops. One for l and one for l**2
    Automatically outputs data to 'data.csv'
    Run 'script.py' to generate bar graphs
    If you change the '10' in the for loops below, change 
                    the '10' in the script.py for loops as well
    '''
    
    lambda__ = 4                                                                     # new lambda var for alpha
    mu_ = (1 + lambda__ + math.sqrt((lambda__**2) + (6 * lambda__) + 1) ) /2         # eigenvalue of growth matrix
    num_trials =  15                        # number trials
    count = 1
    num_ells = 45
    with open(f"bfs_data_.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["n", "l", "time"])
        for i in range(1, num_ells+1):
            n_ = 7500 * (i)
            l_i = (n_)**(1/10)
            p_i = lambda__/(2*l_i - 2)
            
            
            for trial in range(num_trials):
                print(f"n={n_}, run {1 + trial}...")
                main(n_, l_i, p_i, lambda__, mu_, writer)

    print("Generating bar graph ...")
    script.main(mu_, lambda__)
    #script.main(n_, l_i, p_i, lambda__, mu_, num_trials, num_ells)
    print("finished!")
    
