import networkx as nx
import matplotlib.pyplot as plt


def draw_matching(G1, G2, matching_dict, matching_num=0, output_dir='output'):
    """
    :param G1: graph that reprethents the whole topology
    :param G2: graph to match on G1
    :param matching_dict: dictionary that shows G2 nodes mapping on G1

    https://networkx.github.io/documentation/networkx-1.9/examples/drawing/weighted_graph.html
    https://stackoverflow.com/questions/22967086/colouring-edges-by-weight-in-networkx
    """
    print matching_dict
    edges, weights = zip(*nx.get_edge_attributes(G1, 'weight').items())
    pos1 = nx.circular_layout(G1)
    pos2 = {}
    nx.draw(G1, pos1, node_color='b', node_size=1500, edgelist=edges, edge_color=weights, width=7.0,
            edge_cmap=plt.cm.Blues)
    nx.draw_networkx_edge_labels(G1, pos1)
    nx.draw_networkx_labels(G1, pos1, font_size=10, font_family='sans-serif', font_color='w')
    for node_graph1, node_graph2 in matching_dict.iteritems():
        pos2[node_graph2] = pos1[node_graph1]
        x, y = pos2[node_graph2]
        plt.text(x + 0.15, y, s=node_graph2, bbox=dict(facecolor='orange', alpha=0.5),
                 horizontalalignment='center')

    nx.draw_networkx_nodes(G2, pos2, node_color='orange', node_size=500)
    plt.axis('on')
    plt.savefig('{output_dir}/matching{num}.png'.format(output_dir=output_dir, num=matching_num))
    # https://stackoverflow.com/questions/9812996/python-networkx-graph-do-not-draw-old-graph-together-with-new-graph
    plt.clf()
