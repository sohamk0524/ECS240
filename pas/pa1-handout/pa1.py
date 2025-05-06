from __future__ import annotations
import sys

class DomTreeNode:
    node: int
    children: list[DomTreeNode]

    def __init__(self, node: int):
        self.node = node
        self.children = []

    def add_child(self, child: DomTreeNode):
        self.children.append(child)

def draw_custom_vertical_tree(node: DomTreeNode, prefix: str = "", is_last: bool = True):
    print(prefix + "Node(" + str(node.node) + ")")
    child_count = len(node.children)

    for i, child in enumerate(node.children):
        is_last_child = i == child_count - 1
        connector = "└──     " if is_last_child else "├──     "
        draw_custom_vertical_tree(child, prefix + connector, is_last_child)

"""
Helper Functions START
"""
def parse_input(in_file: str, out_file: str) -> tuple[dict, dict, int, int]:
    graph = {}
    rev_graph = {}
    with open(in_file, "r") as f1:
        lines = f1.readlines()

    start = -1
    exit = -1
    for i in range(len(lines)):
        cur_line = lines[i].strip()
        if cur_line[0] == "p":
            tokens = cur_line.split()
            num_nodes = tokens[1]
            start = int(tokens[2])
            exit = int(tokens[3])
            for i in range(1, int(num_nodes) +1):
                graph[i] = []
                rev_graph[i] = []
        elif cur_line[0] == "e":
            tokens = cur_line.split()
            start_node = int(tokens[1])
            end_node = int(tokens[2])
            graph[start_node].append(end_node)
            rev_graph[end_node].append(start_node)
        else:
            continue

    return graph, rev_graph, start, exit

def compute_dom(graph: dict, start: int, end: int, rev_graph: dict) -> dict:
    """
    dom[x] = S
    everything in S dominates x
    """
    dom = {}
    for node in graph.keys():
        dom[node] = set(graph.keys())

    is_changed = True
    while is_changed:
        is_changed = False
        for node in graph.keys():
            preds = rev_graph[node]
            curr_node_dom = set()
            if len(preds) >= 1:
                curr_node_dom = dom[preds[0]]
                for i in range(1, len(preds)):
                    curr_node_dom = curr_node_dom & dom[preds[i]]
            curr_node_dom = curr_node_dom | {node}
            if curr_node_dom != dom[node]:
                dom[node] = curr_node_dom
                is_changed = True
    return dom

def compute_dom_tree(graph: dict, start: int, end: int, rev_graph: dict) -> tuple[dict, dict]:
    dom = compute_dom(graph, start, end, rev_graph)

    #Initialize Dominator Tree Nodes
    idom_relation = {}
    node_dom_tree_map = {}
    for node in graph.keys():
        node_dom_tree_map[node] = DomTreeNode(node)
        idom_relation[node] = None

    #Construct Dominator Tree
    for node in graph.keys():
        #Backtrack until you hit a dominator for each node to get immediate dominator
        imm_dom = node
        visited = set() #Keep track of visited nodes
        while imm_dom == node or imm_dom not in dom[node]: #While imm_dominator is not a strict dominator of node
            preds = rev_graph[imm_dom]
            is_traverse = False
            for pred in preds:
                if pred not in visited:
                    is_traverse = True
                    imm_dom = pred
                    visited = visited | {imm_dom}
                    break

            if not is_traverse:
                break

        if imm_dom != node:
            #Add relationship in dominator tree
            imm_dom_dom_tree_node = node_dom_tree_map[imm_dom]
            node_dom_tree_node = node_dom_tree_map[node]
            imm_dom_dom_tree_node.add_child(node_dom_tree_node)
            idom_relation[node] = imm_dom

    return node_dom_tree_map, idom_relation

def compute_dom_frontier(graph: dict, start: int, end: int, rev_graph: dict, node_dom_tree_map: dict, idom: dict) -> dict:
    df = {}
    for node in graph.keys():
        df[node] = set()

    def recursive_helper(dom_tree_node: DomTreeNode):
        for curr_child in dom_tree_node.children:
            recursive_helper(curr_child)

        #Compute DF Local
        x = dom_tree_node.node
        for y in graph[x]:
            if x != idom[y]:
                df[x] = df[x] | {y}

        #Compute DF UP
        for curr_child in dom_tree_node.children:
            z = curr_child.node
            for y in df[z]:
                if x != idom[y]:
                    df[x] = df[x] | {y}

    recursive_helper(node_dom_tree_map[start])

    return df

def write_output_file(output_file_name: str, file_contents_idom: list[str], file_contents_cd: list[str]):
    with open(output_file_name, 'w') as f:
        for line in file_contents_idom:
            f.write(f"{line}\n")
        for line in file_contents_cd:
            f.write(f"{line}\n")

"""
Helper Functions END
"""

def compute_idom(graph: dict, start: int, end: int, rev_graph: dict) -> list[str]:
    _, idom_relation = compute_dom_tree(graph, start, end, rev_graph)

    ret_list = []
    for u, v in idom_relation.items():
        idom_string = f"idom {u}"
        if v is not None:
            idom_string += f" {v}"
        ret_list.append(idom_string)

    return ret_list

def compute_cd(graph: dict, start: int, end: int, rev_graph: dict) -> list[str]:
    rev_dom_tree_map, rev_idom = compute_dom_tree(rev_graph, end, start, graph)
    rdf = compute_dom_frontier(rev_graph, end, start, graph, rev_dom_tree_map, rev_idom)

    cd = {}
    for node in graph.keys():
        cd[node] = set()

    for y in graph.keys():
        for x in rdf[y]:
            cd[x] = cd[x] | {y}

    ret_list = []
    for node, cd_list in cd.items():
        cd_string = f"cd {node}"
        for curr_cd in cd_list:
            cd_string += f" {curr_cd}"
        ret_list.append(cd_string)

    return ret_list

def main():
    if len(sys.argv) != 3:
        print("Wrong arguments")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    graph, rev_graph, start, end = parse_input(input_path, output_path)
    
    file_contents_idom = compute_idom(graph, start, end, rev_graph)
    file_contents_cd = compute_cd(graph, start, end, rev_graph)

    write_output_file(output_path, file_contents_idom, file_contents_cd)

if __name__ == "__main__":
    main()