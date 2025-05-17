import sys

# Helper function to do the variable refactoring
def refactor_into_temp_vars(dleft, var_left, dright, var_right, temp_counter, new_statements):
    if dright > 1:
        cur_right = var_right
        while dright > 1:
            add_statement = (0, temp_counter[0], 1, cur_right)  # temp = *cur_right
            cur_right = temp_counter[0]
            temp_counter[0] += 1
            new_statements.append(add_statement)
            dright -= 1
        var_right = cur_right

    if dleft > 1:
        cur_left = var_left
        while dleft > 1:
            add_statement = (0, temp_counter[0], 1, cur_left)  # temp = *cur_left
            cur_left = temp_counter[0]
            temp_counter[0] += 1
            new_statements.append(add_statement)
            dleft -= 1
        var_left = cur_left

    if dleft == 1 and dright == 1:
        tmp = temp_counter[0]
        new_statements.append((0, tmp, 1, var_right))  # tmp = *var_right
        temp_counter[0] += 1
        new_statements.append((1, var_left, 0, tmp))   # *var_left = tmp
    elif dleft == 1 and dright == -1:
        tmp = temp_counter[0]
        new_statements.append((0, tmp, -1, var_right))  # tmp = &var_right
        temp_counter[0] += 1
        new_statements.append((1, var_left, 0, tmp))    # *var_left = tmp
    else:
        new_statements.append((dleft, var_left, dright, var_right))


# Function to parse through raw input and return list of statement refactored into Andersen compatible format
def transform_input(in_file):
    with open(in_file, "r") as input:
        lines = input.readlines()

    num_vars = 0
    statements = []
    #Extract the number of variables and the statements in the input
    for i in range(len(lines)):
        cur_line = lines[i].strip()
        if cur_line[0] == "c":
            continue
        elif cur_line[0] == "p":
            tokens = cur_line.split()
            num_vars = int(tokens[1])
        else:
            statements.append(cur_line)

    #Parse through statements to extract the variable and no. of dereferences
    new_statements = []
    temp_counter = [num_vars + 1]
    for cur_state in statements:   
        tokens = cur_state.split()
        dleft = int(tokens[1])
        var_left = int(tokens[2])
        dright = int(tokens[3])
        var_right = int(tokens[4])
        if (dleft > 1 or dright > 1 or (dleft == 1 and dright == -1)) or ( dright == 1 and dleft == 1 ):
            #function to re-write into temp vars
            refactor_into_temp_vars(dleft, var_left, dright, var_right, temp_counter, new_statements)
        else:
            new_statements.append((dleft, var_left, dright, var_right))

    return num_vars, temp_counter, new_statements

# Function to assign statements to constraints based on their form
def assign_constraints(statements):
    address_con = []
    copy_con = []
    load_con= []
    store_con= []

    for statement in statements:
        dleft = statement[0]
        var_left = statement[1]
        dright = statement[2]
        var_right = statement[3]
        if dleft == 0 and dright == -1:
            address_con.append((var_left, var_right))
        elif dleft == 0 and dright == 0:
            copy_con.append((var_left, var_right))
        elif dleft == 1 and dright == 0:
            store_con.append((var_left, var_right))
        elif dleft == 0 and dright == 1:
            load_con.append((var_left, var_right))
        else:
            print("Invalid statment")
    
    return address_con, copy_con, load_con, store_con

def make_points_to_sets(constraints, total_vars):
    addr_of = constraints[0]
    copy = constraints[1]
    load = constraints[2]
    store = constraints[3]

    pts_to = {}
    changed = True 
    

    for i in range(1,total_vars[0]):
        pts_to[i] = set()

    for const in addr_of: # 1 = &2
        pts_to[const[0]].add(const[1])

    while changed:
        changed = False
        for const in copy: # 1 = 2
            pointer = const[0]
            points_to = const[1]
            for pts_to_val in pts_to[points_to]:
                if pts_to_val not in pts_to[pointer]:
                    changed = True
                    pts_to[pointer].add(pts_to_val)

        for const in store: # *1 = 2
            pointer = const[0]
            points_to = const[1]
            what_pointer_points_to = pts_to[pointer]

            for a in what_pointer_points_to:
                for pts_to_val in pts_to[points_to]:
                    if pts_to_val not in pts_to[a]:
                        changed = True
                        pts_to[a].add(pts_to_val)
        
        for const in load: # 1 = *2
            pointer = const[0]
            points_to = const[1]

            for a in set(pts_to[points_to]):
                for b in pts_to[a]: # a → b
                    if b not in pts_to[pointer]:
                        changed = True
                        pts_to[pointer].add(b) # x → b


    return pts_to

def format_output(pts_to_set, num_vars, output_file):
    with open(output_file, "w") as out:
        for i in range(num_vars):
            pointer = i+1
            pts_to_list = list(pts_to_set[pointer])
            for j in range(len(pts_to_list)):
                output_str = f"pt {pointer} {pts_to_list[j]}\n"
                out.write(output_str)



def main():
    if len(sys.argv) != 3:
        print("Wrong arguments")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    num_vars, total_vars, statements = transform_input(input_path)

    #function to store the statements into different constraints
    addr_of, copy, load, store = assign_constraints(statements)
    all_constraints = [addr_of, copy, load, store]

    #function to assign points to sets
    pts_to = make_points_to_sets(all_constraints, total_vars)

    format_output(pts_to, num_vars, output_path)

    #print(statements)
    # print(f"address constraints: {addr_of}")
    # print(f"copy constraints: {copy}")
    # print(f"load constraints: {load}")
    # print(f"store constraints: {store}")
    # print(all_constraints)
    # print(pts_to)

if __name__ == "__main__":
    main()