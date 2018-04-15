# -*- coding: UTF8 -*-

adj_matrix = [[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]]
nodes2ports = [(1, 1), (2, 8), (3, 2), (4, 2), (5, 3)]


def find_mapping(adj_matrix, nodes2ports, is_cloud=False):
    """
    :param adj_matrix: матрица смежности, задающая граф, который определяет тестовую топологию
    :param nodes2ports: массив узлов, представляющих собой последовательность из двух элементов,
    первый - идентификатор узла, второй - количиство портов в свитче для этого узла
    :param is_cloud: определяет, потребуется облако или нет
    :return: последовательность из двух элементов, первый - результат соответствия,
    второй - описание результата
    """
    if not is_cloud and len(nodes2ports) < len(adj_matrix):
        return None, "There are not enough nodes in switch"

    ports_val_test = []

    for line_num in range(0, len(adj_matrix)):
        ports_val_test.append((line_num + 1, sum(adj_matrix[line_num])))

    nodes2ports.sort(key=lambda x: x[1])
    ports_val_test.sort(key=lambda x: x[1])

    adj_final = {}
    num = 0
    for i in range(0, len(ports_val_test)):
        for j in range(num, len(nodes2ports)):
            if ports_val_test[i][1] <= nodes2ports[j][1]:
                adj_final[ports_val_test[i][0]] = nodes2ports[j][0]
                num = j + 1
                break

    if not is_cloud and len(adj_final) < len(ports_val_test):
        return None, "Matching not found"
    else:
        return adj_final, "Matching found"


if __name__ == "__main__":
    print find_mapping(adj_matrix, nodes2ports)
