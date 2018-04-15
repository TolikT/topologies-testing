import copy
import csv
import os
import shutil

import networkx as nx
import numpy as np
from networkx.algorithms import isomorphism

from common.drawing import draw_matching

if __name__ == "__main__":

    # number of columns is constant in .csv topology definition files
    NUM_OF_COLUMNS = 4
    OUTPUT_DIR = 'case1_out'

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

    # read test topology matrix
    with open("input/test_infrastructure.csv", "r") as test_matrix_file:
        reader = csv.reader(test_matrix_file)
        test_topology_full = list(reader)
        test_topology = test_topology_full[1:]
        count_items = len(test_topology)
        for i in range(count_items):
            for j in range(NUM_OF_COLUMNS):
                test_topology[i][j] = int(test_topology[i][j])

    # read real topology matrix
    with open("input/phys_infrastructure.csv", "r") as infra_matrix_file:
        reader = csv.reader(infra_matrix_file)
        real_topology_full = list(reader)
        real_topology = real_topology_full[1:]
        count_items = len(real_topology)
        for i in range(count_items):
            for j in range(NUM_OF_COLUMNS):
                real_topology[i][j] = int(real_topology[i][j])

    # find number of test hosts
    first_column = [int(line[0]) for line in test_topology]
    third_column = [int(line[2]) for line in test_topology]
    count_test_nodes = len(set(first_column + third_column))

    # find number of real hosts
    first_column = [int(line[0]) for line in real_topology]
    third_column = [int(line[2]) for line in real_topology]
    count_real_nodes = len(set(first_column + third_column))

    # fill test adj matrix
    test_adj_matrix = [[0 for i in range(count_test_nodes)] for j in range(count_test_nodes)]
    for line in test_topology:
        test_adj_matrix[line[0]][line[2]] += 1
        test_adj_matrix[line[2]][line[0]] += 1

    # fill real adj matrix
    real_adj_matrix = [[0 for i in range(count_real_nodes)] for j in range(count_real_nodes)]
    for line in real_topology:
        real_adj_matrix[line[0]][line[2]] += 1
        real_adj_matrix[line[2]][line[0]] += 1

    # find the first of matchings
    G1 = nx.from_numpy_matrix(np.array(real_adj_matrix), create_using=nx.MultiGraph())
    G2 = nx.from_numpy_matrix(np.array(test_adj_matrix), create_using=nx.MultiGraph())
    edge_match = lambda edge1, edge2: edge1[0]['weight'] == edge2[0]['weight']
    GM = isomorphism.MultiGraphMatcher(G1, G2, edge_match=edge_match)

    if GM.subgraph_is_isomorphic():
        matchings = [mapping for mapping in GM.subgraph_isomorphisms_iter()]
        print matchings
    else:
        matchings = None
        print "matching not found"

    if matchings:
        matching_num = 0
        for matching in matchings:
            # draw matchings without interfaces information
            matching_num += 1
            draw_matching(G1, G2, matching, matching_num, OUTPUT_DIR)

            # create final matching matrix with interfaces
            final_matching = []
            working_test_topology = copy.deepcopy(test_topology)
            for line_real in real_topology:
                if line_real[0] in matching.keys() and line_real[2] in matching.keys():
                    line_count = -1
                    for line_test in working_test_topology:
                        # count current line number to delete already used test line
                        line_count += 1
                        # [0,1,2,0] and [2,0,0,1] mean the same in input .csv
                        matching_set = {line_test[0], line_test[2]}
                        # this is the reason why sets of two elements should be compared
                        if {matching[line_real[0]], matching[line_real[2]]} == matching_set:
                            line_to_append1 = line_real[:2]
                            line_to_append2 = line_real[2:]
                            if matching[line_real[0]] == line_test[0]:
                                line_to_append1 += line_test[:2]
                                line_to_append2 += line_test[2:]
                            else:
                                line_to_append1 += line_test[2:]
                                line_to_append2 += line_test[:2]
                            final_matching.append(line_to_append1)
                            final_matching.append(line_to_append2)
                            del working_test_topology[line_count]
                            break
            with open("{output_dir}/matching_matrix{num}.csv".format(output_dir=OUTPUT_DIR, num=matching_num),
                      "w") as result_file:
                for line in final_matching:
                    result_file.write(",".join(str(elem) for elem in line) + "\n")
