import csv
import yaml
import os
import shutil

from common.mapping import find_mapping


def merge_two_dicts(dict1, dict2):
    merged = dict1.copy()
    merged.update(dict2)
    return merged


if __name__ == "__main__":

    NUM_OF_COLUMNS = 4
    OUTPUT_DIR = 'case3_out'

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

    # read existing topology
    # example: {'node1': {0: 0, 1: 1, 2: 2}, 'node3': {0: 6, 1: 7, 2: 8}, 'node2': {0: 3, 1: 4, 2: 5}}
    with open("input/nodes_switch_map.yml", "r") as map_file:
        nodes = yaml.safe_load(map_file)

    real_node_names = nodes.keys()

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

    # generate dictionary with number of links for each node
    # example: {'test_node3': 3, 'test_node2': 2, 'test_node1': 3}
    test_links = {}
    for i in range(0, count_test_nodes):
        test_links[node_names[i]] = sum(test_adj_matrix[i])

    # create data structure to execute find_mapping()
    # example: [('node1', 3), ('node3', 3), ('node2', 3)]
    nodes2ports = [(node, len(ports)) for node, ports in nodes.iteritems()]

    # find mapping of nodes in test and real topologies
    mapping_result = find_mapping(test_adj_matrix, nodes2ports, is_cloud=True)
    # example: {1: 'node2', 2: 'node1'}
    test2test = mapping_result[0]

    test2test_final = {}
    for key, value in test2test.iteritems():
        test2test_final[node_names[key - 1]] = value

    cloud_names = [elem for elem in node_names if elem not in test2test_final.keys()]
    cloud_indexes = [elem for elem in range(1, count_test_nodes + 1) if elem not in test2test.keys()]

    # example: test2cloud_final = {'test_node3': 'cloud_node1'}
    test2cloud = {}
    test2cloud_final = {}

    for i in range(1, len(cloud_names) + 1):
        # example: {3: 'cloud_node1'}
        test2cloud[cloud_indexes[i - 1]] = "cloud_node" + str(i)
        # example: {'test_node3': 'cloud_node1'}
        test2cloud_final[cloud_names[i - 1]] = "cloud_node" + str(i)

    # example: {1: 'node2', 2: 'node1', 3: 'cloud_node1'}
    test2real = merge_two_dicts(test2test, test2cloud)
    # example: {'test_node3': 'cloud_node1', 'test_node2': 'node1', 'test_node1': 'node2'}
    test2real_final = merge_two_dicts(test2test_final, test2cloud_final)

    # example: {'node1': 2, 'node2': 1, 'cloud_node1': 3}
    real2test = {value: key for key, value in test2real.iteritems()}
    # example: {'node1': 'test_node2', 'node2': 'test_node1', 'cloud_node1': 'test_node3'}
    real2test_final = {value: key for key, value in test2real_final.iteritems()}

    # generate cloud_switch_ports
    # example: {'cloud1': [1, 2], 'cloud3': [6, 7, 8], 'cloud2': [3, 4, 5]}
    # 0 is reserved port number to link test and cloud switches
    start_pos = 1
    cloud_switch_ports = {}
    for key in test_links:
        if key in test2cloud_final.keys():
            next_pos = start_pos + test_links[key]
            cloud_switch_ports[test2cloud_final[key]] = range(start_pos, next_pos)
            start_pos = next_pos

    # start fill lines to append in result matrix
    final_result = []

    final_switch_ports_mapping = []
    final_cloud_switch_ports_mapping = []
    both_mapping = []
    for i in range(1, count_test_nodes + 1):
        for j in range(i + 1, count_test_nodes + 1):
            node1 = test2test_final[node_names[i - 1]] if node_names[i - 1] in test2test_final else test2cloud_final[
                node_names[i - 1]]
            node2 = test2test_final[node_names[j - 1]] if node_names[j - 1] in test2test_final else test2cloud_final[
                node_names[j - 1]]
            ports2join = test_adj_matrix[i - 1][j - 1]
            for port_num in range(0, ports2join):
                line2append1 = []
                line2append2 = []
                # check where nodes are located
                # there are 4 cases: local-local, local-cloud, cloud-local, cloud-cloud
                if not node1.startswith("cloud") and not node2.startswith("cloud"):
                    final_switch_ports_mapping.append((switch_ports[node1][0], switch_ports[node2][0]))
                    line2append1 += [node1, switch_ports[node1][0], node_names[i - 1]]
                    line2append2 += [node2, switch_ports[node2][0], node_names[j - 1]]
                    del (switch_ports[node1][0])
                    del (switch_ports[node2][0])
                elif node1.startswith("cloud") and not node2.startswith("cloud"):
                    both_mapping.append(
                        ("cloud: " + str(cloud_switch_ports[node1][0]), 0, 0, "test: " + str(switch_ports[node2][0])))
                    line2append1 += [node1, cloud_switch_ports[node1][0], node_names[i - 1]]
                    line2append2 += [node2, switch_ports[node2][0], node_names[j - 1]]
                    del (cloud_switch_ports[node1][0])
                    del (switch_ports[node2][0])
                elif not node1.startswith("cloud") and node2.startswith("cloud"):
                    both_mapping.append(
                        ("test: " + str(switch_ports[node1][0]), 0, 0, "cloud: " + str(cloud_switch_ports[node2][0])))
                    line2append1 += [node1, switch_ports[node1][0], node_names[i - 1]]
                    line2append2 += [node2, cloud_switch_ports[node2][0], node_names[j - 1]]
                    del (switch_ports[node1][0])
                    del (cloud_switch_ports[node2][0])
                else:
                    final_cloud_switch_ports_mapping.append(
                        (cloud_switch_ports[node1][0], cloud_switch_ports[node2][0]))
                    line2append1 += [node1, cloud_switch_ports[node1][0], node_names[i - 1]]
                    line2append2 += [node2, cloud_switch_ports[node2][0], node_names[j - 1]]
                    del (cloud_switch_ports[node1][0])
                    del (cloud_switch_ports[node2][0])
                # go through test topology and get ports from there for final result (last element of the line: )
                for line_num in range(0, len(test_topology)):
                    # node numbers starts with 0 in .csv files, but with 1 in test2test_reverse
                    if {test_topology[line_num][0] + 1, test_topology[line_num][2] + 1} == {real2test[node1],
                                                                                            real2test[node2]}:
                        if test_topology[line_num][0] == real2test[node1]:
                            line2append1.append(test_topology[line_num][1])
                            line2append2.append(test_topology[line_num][3])
                        else:
                            line2append1.append(test_topology[line_num][1])
                            line2append2.append(test_topology[line_num][3])
                        # delete used line from test topology and stop cycle
                        del (test_topology[line_num])
                        break
                final_result.append(line2append1)
                final_result.append(line2append2)

    with open("{output_dir}/results".format(output_dir=OUTPUT_DIR), "w") as results:
        results.write("local-cloud switch ports mapping: {}\n".format(str(both_mapping)))
        results.write("local switch ports mapping: {}\n".format(str(final_switch_ports_mapping)))
        results.write("cloud switch ports mapping: {}\n\nFinal matrix:\n".format(str(final_cloud_switch_ports_mapping)))
        for line in final_result:
            results.write(",\t\t\t".join(str(elem) for elem in line) + "\n")
