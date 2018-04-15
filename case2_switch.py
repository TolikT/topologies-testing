import csv
import yaml
import os
import shutil

from common.mapping import find_mapping

if __name__ == "__main__":

    NUM_OF_COLUMNS = 4
    OUTPUT_DIR = 'case2_out'

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

    # read existing topology definition
    # example: {'node1': {0: 0, 1: 1, 2: 2}, 'node3': {0: 6, 1: 7, 2: 8}, 'node2': {0: 3, 1: 4, 2: 5}}
    with open("input/nodes_switch_map.yml", "r") as map_file:
        nodes = yaml.safe_load(map_file)

    # mapping real nodes to corresponding switch ports
    # example: {'node1': [0, 1, 2], 'node3': [6, 7, 8], 'node2': [3, 4, 5]}
    switch_ports = {}
    for item, ports in nodes.iteritems():
        switch_ports[item] = ports.values()

    # read test topology definition
    with open("input/test_infrastructure.csv", "r") as test_matrix_file:
        reader = csv.reader(test_matrix_file)
        test_topology_full = list(reader)
        test_topology = test_topology_full[1:]
        count_items = len(test_topology)
        for i in range(count_items):
            for j in range(NUM_OF_COLUMNS):
                test_topology[i][j] = int(test_topology[i][j])

    # find number of test hosts
    first_column = [int(line[0]) for line in test_topology]
    third_column = [int(line[2]) for line in test_topology]
    count_test_nodes = len(set(first_column + third_column))

    # create list that contains node names
    node_names = ["test_node{num}".format(num=num) for num in range(1, count_test_nodes + 1)]

    # fill test adj matrix
    test_adj_matrix = [[0 for i in range(count_test_nodes)] for j in range(count_test_nodes)]
    for line in test_topology:
        test_adj_matrix[line[0]][line[2]] += 1
        test_adj_matrix[line[2]][line[0]] += 1

    # create data structure to execute find_mapping()
    # example: [('node1', 3), ('node3', 3), ('node2', 3)]
    nodes2ports = [(node, len(ports)) for node, ports in nodes.iteritems()]

    # find mapping of nodes in test and real topologies
    mapping_result = find_mapping(test_adj_matrix, nodes2ports)
    # example test2test: {1: 'node3', 2: 'node1', 3: 'node2'}
    test2test = mapping_result[0]
    reason = mapping_result[1]

    # handle if mapping found
    if test2test:
        # create reverse test to test for processing
        test2test_reverse = {value: key for key, value in test2test.iteritems()}
        print test2test_reverse
        test2test_final = {}
        for key, value in test2test.iteritems():
            test2test_final[node_names[key - 1]] = value
        final_switch_ports_mapping = []
        size_matrix = len(test_adj_matrix)
        # start fill lines to append in result matrix
        final_result = []

        # loop only for part of matrix before/under diagonal
        # WARNING: test_topology object will be changed in the code below and can't be used anymore
        for i in range(1, size_matrix + 1):
            for j in range(i + 1, size_matrix + 1):
                # get real node names from mapping
                node1 = test2test[i]
                node2 = test2test[j]
                # get number of ports to match
                ports2join = test_adj_matrix[i - 1][j - 1]
                # match this number of ports in cycle
                for port_num in range(0, ports2join):
                    # one line in test topology -> two lines in result
                    line2append1 = []
                    line2append2 = []
                    line2append1 += [node1, switch_ports[node1][0], node_names[i - 1]]
                    line2append2 += [node2, switch_ports[node2][0], node_names[j - 1]]
                    # go through test topology and get ports from there for final result (last element of the line: )
                    for line_num in range(0, len(test_topology)):
                        # node numbers starts with 0 in .csv files, but with 1 in test2test_reverse
                        if {test_topology[line_num][0] + 1, test_topology[line_num][2] + 1} == {
                        test2test_reverse[node1], test2test_reverse[node2]}:
                            if test_topology[line_num][0] == test2test_reverse[node1]:
                                line2append1.append(test_topology[line_num][1])
                                line2append2.append(test_topology[line_num][3])
                            else:
                                line2append1.append(test_topology[line_num][1])
                                line2append2.append(test_topology[line_num][3])
                            # delete used line from test topology and stop cycle
                            del (test_topology[line_num])
                            break
                    # add ports to final matching
                    final_switch_ports_mapping.append((switch_ports[node1][0], switch_ports[node2][0]))
                    # delete ports that already used in mapping
                    del (switch_ports[node1][0])
                    del (switch_ports[node2][0])
                    final_result.append(line2append1)
                    final_result.append(line2append2)
        with open("{output_dir}/results".format(output_dir=OUTPUT_DIR), "w") as results:
            results.write("node mapping: {}\n".format(str(test2test_final)))
            results.write("switch ports mapping: {}\n\nFinal matrix:\n".format(str(final_switch_ports_mapping)))
            for line in final_result:
                results.write(",".join(str(elem) for elem in line) + "\n")

    # if mapping not found
    else:
        with open("{output_dir}/results".format(output_dir=OUTPUT_DIR), "w") as results:
            results.write(reason)
