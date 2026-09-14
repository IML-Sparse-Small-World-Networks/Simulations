import csv
from multiprocessing import Pool, cpu_count
 
import opt_ER_graph as ER_graph
 
 
HEADER = ['Trial', 'n', 'l', 'p', 'StartVertex', 
          'EndVertex', 'FirstPassageTime', 'Distance']
 
 
def _run_one(args):
    trial, n, l, p, start_vertex, end_vertex = args
    return ER_graph.run_trial(trial, n, l, p, start_vertex, end_vertex) 

def main():
    n = 1000          # number of vertices
    l = n / 10      # shortcut neighbor range
    p = 0.7         # probability of a shortcut
    num_trials = 100  # 1 thousand trials, e.g.
    start_vertex, end_vertex = 0, n // 2
 
    jobs = [(i, n, l, p, start_vertex, end_vertex) for i in range(num_trials)]
 
    with open('data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(HEADER)
        for job in jobs:
            print("Trial:", job[0] + 1)
            writer.writerow(_run_one(job))

def main_parallel(num_trials=1000, n=100, l=None, p=0.7, 
                  start_vertex=0, end_vertex=None, processes=None):
    l = n / 10 if l is None else l
    end_vertex = n // 2 if end_vertex is None else end_vertex
    processes = processes or cpu_count()
 
    jobs = [(i, n, l, p, start_vertex, end_vertex) for i in range(num_trials)]
 
    with open('data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(HEADER)
 
        with Pool(processes=processes) as pool:
            for row in pool.imap_unordered(_run_one, jobs, chunksize=max(1, num_trials // (processes * 4) or 1)):
                writer.writerow(row)

if __name__ == "__main__":
    main()
