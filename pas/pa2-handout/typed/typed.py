import sys
from copy import deepcopy

def parse_input(file: str) -> dict:
    lines = []
    with open(file, "r") as file_obj:
        raw_lines = file_obj.readlines()
        for curr_line in raw_lines:
            if curr_line[0] == "c":
                continue
            lines.append(curr_line)

    variable_layer = dict() #Maps each variable to it's layer
    statements = {"direct_assignment": list(), "copying_statements": list()} #Stores the set of program statements

    problem_decl = lines[0].strip().split(" ")
    n = int(problem_decl[1])
    s = int(problem_decl[2])

    #Layer Declaration
    max_layer = -1
    for i in range(1, n + 1, 1):
        layer_decl = lines[i].strip().split(" ")
        var = int(layer_decl[1])
        layer = int(layer_decl[2])
        variable_layer[var] = layer
        max_layer = max(max_layer, layer)

    #Statement Declaration
    for i in range(n + 1, n + s + 1, 1):
        statement_decl = lines[i].strip().split(" ")
        statement = (int(statement_decl[1]), int(statement_decl[2]), int(statement_decl[3]), int(statement_decl[4]))
        if statement[2] == -1:
            statements["direct_assignment"].append(statement)
        else:
            statements["copying_statements"].append(statement)

    return {"n": n, "s": s, "max_layer": max_layer, "variable_layer": variable_layer, "statements": statements}

def find_all_targets(G: dict, source: int, dist: int) -> list[int]:
    all_targets = []

    def dfs_helper(curr_source: int, curr_dist: int):
        if curr_dist == 0:
            all_targets.append(curr_source)
            return

        for next_source in G[curr_source]:
            dfs_helper(next_source, curr_dist - 1)
        
        return

    dfs_helper(source, dist)

    return all_targets

def find_all_vertex_disjoint_targets(G: dict, source1: int, dist1: int, source2: int, dist2: int, F: set[tuple[tuple[int, int], tuple[int, int]]], layer_variables: dict, variable_layer: dict) -> list[tuple[int, int]]:
    G = deepcopy(G)
    layer_variables = deepcopy(layer_variables)

    N = max(G.keys())

    dist = -1
    if variable_layer[source1] < variable_layer[source2]:
        #Add dummy nodes to source1
        num_dummy_nodes = variable_layer[source2] - variable_layer[source1]

        #Add dummy nodes as vertices to graph
        curr_layer = variable_layer[source2]
        for curr_dummy_node in range(N + 1, N + 1 + num_dummy_nodes, 1):
            if curr_layer - 1 == variable_layer[source1]:
                G[curr_dummy_node] = [source1]
            else:
                G[curr_dummy_node] = [curr_dummy_node + 1]
            variable_layer[curr_layer].append(curr_dummy_node)
            curr_layer -= 1

        source1 = N + 1
        dist = dist2
        
    if variable_layer[source1] > variable_layer[source2]:
        #Add dummy nodes to source2
        num_dummy_nodes = variable_layer[source1] - variable_layer[source2]

        #Add dummy nodes as vertices to graph
        curr_layer = variable_layer[source1]
        for curr_dummy_node in range(N + 1, N + 1 + num_dummy_nodes, 1):
            if curr_layer - 1 == variable_layer[source2]:
                G[curr_dummy_node] = [source2]
            else:
                G[curr_dummy_node] = [curr_dummy_node + 1]
            variable_layer[curr_layer].append(curr_dummy_node)
            curr_layer -= 1

        source2 = N + 1
        dist = dist1

    if variable_layer[source1] == variable_layer[source2]:
        dist = dist1
    
    new_G = {}

    #Add Vertexes for New Graph
    for layer, var_in_layer in layer_variables.items():
        for u in var_in_layer:
            for v in var_in_layer:
                if u == v:
                    continue
                
                new_G[(u, v)] = []

    for curr_vertex in new_G.keys():
        u1, v1 = curr_vertex

        for u2 in G[u1]:
            for v2 in G[v1]:
                poss_forbidden_pair = ((u1, u2), (v1, v2))
                if poss_forbidden_pair in F: # u1 -> u2 and v1 -> v2 is a forbidden pair
                    continue

                new_G[curr_vertex].append((u2, v2))

    all_targets: list[tuple[int, int]] = []

    def dfs_helper(curr_source: tuple[int, int], curr_dist: int):
        if curr_dist == 0:
            all_targets.append(curr_source)
            return

        for next_source in new_G[curr_source]:
            dfs_helper(next_source, curr_dist - 1)
        
        return
    
    dfs_helper((source1, source2), dist)

    return all_targets

def compute_1cpp(V: list[tuple[str, int]], C: list[tuple[str, int]], S: list[tuple[tuple[str, int], tuple[str, int]]]) -> list[tuple[tuple[str, int], tuple[str, int]]]:
    G = dict()

    for curr_var in V:
        G[curr_var] = []
    
    for curr_constant in C:
        G[curr_constant] = []

    for lhs, rhs in S:
        G[lhs].append(rhs)

    def find_all_reachable_constants(curr_node: tuple[str, int], reachable_constants: set[tuple[str, int]]):
        if len(G[curr_node]) == 0:
            #There are no more edges
            if curr_node[0] == "C":
                reachable_constants.append(curr_node)
            
            return
        
        for next_node in G[curr_node]:
            find_all_reachable_constants(next_node, reachable_constants)
        
        return
    
    one_cpp: list[tuple[tuple[str, int], tuple[str, int]]] = []

    for curr_var in V:
        reachable_constants: list[tuple[str, int]] = []
        find_all_reachable_constants(curr_var, reachable_constants)
        for curr_constant in reachable_constants:
            one_cpp.append((curr_var, curr_constant))

    return one_cpp

def compute_2cpp(V: list[tuple[str, int]], C: list[tuple[str, int]], S: list[tuple[tuple[str, int], tuple[str, int]]]) -> list[tuple[tuple[tuple[str, int], tuple[str, int]], tuple[tuple[str, int], tuple[str, int]]]]:
    var_const_stmt: list[tuple[tuple[str, int], tuple[str, int]]] = [] # Xi = Cj
    var_var_stmt: list[tuple[tuple[str, int], tuple[str, int]]] = [] # Xi = Xj

    for curr_stmt in S:
        lhs, rhs = curr_stmt
        if rhs[0] == "C":
            var_const_stmt.append(curr_stmt)
        else:
            var_var_stmt.append(curr_stmt)

    two_cpp: set[tuple[tuple[tuple[str, int], tuple[str, int]], tuple[tuple[str, int], tuple[str, int]]]] = set()

    if len(var_const_stmt) > 1:
        for stmt1 in var_const_stmt:
            lhs1, rhs1 = stmt1

            for stmt2 in var_const_stmt:
                lhs2, rhs2 = stmt2

                if lhs1 == lhs2:
                    continue

                two_cpp.add(((lhs1, rhs1), (lhs2, rhs2)))
    else:
        for stmt1 in var_const_stmt:
            lhs1, rhs1 = stmt1

            for stmt2 in var_var_stmt:
                lhs2, rhs2 = stmt2

                if lhs1 == lhs2:
                    continue

                if rhs2 != lhs1:
                    continue

                two_cpp.add(((lhs1, rhs1), (lhs2, rhs1)))
                two_cpp.add(((lhs2, rhs1), (lhs1, rhs1)))

    changed = True
    while changed:
        changed = False
        add_set: set[tuple[tuple[tuple[str, int], tuple[str, int]], tuple[tuple[str, int], tuple[str, int]]]] = set()
        for ele1, ele2 in two_cpp:
            X = ele1[0]
            x = ele1[1]
            Y = ele2[0]
            y = ele2[1]

            for stmt in var_const_stmt:
                Z, z = stmt
                if X == Z:
                    continue
                ele_to_add = (ele1, (Z, z))
                if ele_to_add not in two_cpp:
                    add_set.add(ele_to_add)
                    changed = True
            
            for stmt in var_var_stmt:
                Z, z = stmt
                if X != z:
                    continue

                if X != Z:
                    ele_to_add = (ele1, (Z, x))
                    if ele_to_add not in two_cpp:
                        add_set.add(ele_to_add)
                        changed = True
                if Y != Z:
                    ele_to_add = ((Z, x), ele2)
                    if ele_to_add not in two_cpp:
                        add_set.add(ele_to_add)
                        changed = True
        
        two_cpp = two_cpp.union(add_set)

    return list(two_cpp)

def compute_realisability_graph(parsed_info: dict) -> dict:
    N = parsed_info["n"]
    L = parsed_info["max_layer"]
    G = {}

    for i in range(1, N + 1, 1):
        G[i] = []

    layer = parsed_info["variable_layer"]
    variables_by_layer = {}

    for i in range(0, L + 1, 1):
        variables_by_layer[i] = []

    for var, var_layer in layer.items():
        variables_by_layer[var_layer].append(var)

    F: set[tuple[tuple[int, int], tuple[int, int]]] = set() #Data type inside F --> ((u1, u2), (v1, v2)) --> This means that u1 -> u2 and v1 -> v2 CANNOT happen together
    for l in range(L, 0, -1):
        V = [("X", i) for i in variables_by_layer[l]]
        C = [("C", i) for i in variables_by_layer[l - 1]]
        S = []

        for stmt in parsed_info["statements"]["direct_assignment"]:
            d = stmt[0]
            p = stmt[1]
            z = stmt[3]
            if (layer[z] == l - 1) and (layer[p] == l + d):
                all_q = find_all_targets(G, p, d)
                for q in all_q:
                    ccp_stmt = (("X", q), ("C", z))
                    S.append(ccp_stmt)

        for stmt in parsed_info["statements"]["copying_statements"]:
            d1 = stmt[0]
            p1 = stmt[1]
            d2 = stmt[2]
            p2 = stmt[3]
            if (layer[p1] == l + d1) and (layer[p2] == l + d2):
                all_vertex_disjoint_targets = find_all_vertex_disjoint_targets(G, p1, d1, p2, d2, F, variables_by_layer, parsed_info["variable_layer"])
                for q1, q2 in all_vertex_disjoint_targets:
                    cpp_stmt = (("X", q1), ("X", q2))
                    S.append(cpp_stmt)

        one_cpp = compute_1cpp(V, C, S)
        for cpp_var, constant in one_cpp:
            G[cpp_var[1]].append(constant[1])

        two_cpp = compute_2cpp(V, C, S)

        F_local: set[tuple[tuple[int, int], tuple[int, int]]] = set()

        for i in range(0, len(one_cpp)):
            cpp_var1, cpp_constant1 = one_cpp[i]
            q1 = cpp_var1[1]
            z1 = cpp_constant1[1]

            for j in range(0, len(one_cpp)):
                if one_cpp[i] == one_cpp[j]:
                    continue

                cpp_var2, cpp_constant2 = one_cpp[j]
                q2 = cpp_var2[1]
                z2 = cpp_constant2[1]

                if q1 != q2:
                    if (one_cpp[i], one_cpp[j]) not in two_cpp:
                        forbidden_pair = ((q1, z1), (q2, z2))
                        F_local.add(forbidden_pair)
        
        F = F.union(F_local)

    return G

def dump_points_to_relations(realizability_graph: dict, file: str):
    with open(file, "w") as file_obj:
        for u, all_v in realizability_graph.items():
            for v in all_v:
                file_obj.write(f"pt {u} {v}\n")

def main():
    if len(sys.argv) != 3:
        print("Wrong Arguments")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    parsed_info = parse_input(input_path)

    realizability_graph = compute_realisability_graph(parsed_info)

    dump_points_to_relations(realizability_graph, output_path)


main()