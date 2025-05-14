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
    
def main():
    if len(sys.argv) != 3:
        print("Wrong arguments")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    num_vars, total_vars, statements = transform_input(input_path)

    
    print(statements)
    print(num_vars)
    print(total_vars)

if __name__ == "__main__":
    main()