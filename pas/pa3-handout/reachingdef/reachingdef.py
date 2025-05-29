import sys
from abc import abstractmethod

# Start of Common Utilities
def parse_input(input_path: str) -> tuple[dict, dict, dict, int, int, int]:
    lines = []
    with open(input_path, "r") as file_obj:
        raw_lines = file_obj.readlines()
        for curr_line in raw_lines:
            if curr_line[0] == "c":
                continue
            lines.append(curr_line.strip())

    problem_decl = lines[0].split()

    V = int(problem_decl[1])
    B = int(problem_decl[2])
    E = int(problem_decl[3])
    s = int(problem_decl[4])
    x = int(problem_decl[5])

    basic_blocks = dict()
    cfg = dict()
    rev_cfg = dict()

    #Initialization
    for i in range(1, B + 1, 1):
        basic_blocks[i] = None
        cfg[i] = []
        rev_cfg[i] = []

    for curr_line in lines:
        curr_line_split = curr_line.split()
        if curr_line_split[0] == "b":
            basic_block_id = int(curr_line_split[1])
            rest_of_basic_block_decl = curr_line_split[2:]
            if len(rest_of_basic_block_decl) == 0:
                basic_blocks[basic_block_id] = None
            elif len(rest_of_basic_block_decl) == 1:
                lhs_var_num = int(rest_of_basic_block_decl[0])
                basic_blocks[basic_block_id] = (lhs_var_num, None)
            else:
                lhs = None
                rhs = []
                if int(rest_of_basic_block_decl[0]) > 0:
                    lhs = int(rest_of_basic_block_decl[0])
                
                for i in range(1, len(rest_of_basic_block_decl), 1):
                    rhs.append(int(rest_of_basic_block_decl[i]))
                basic_blocks[basic_block_id] = (lhs, rhs)
        elif curr_line_split[0] == "e":
            source = int(curr_line_split[1])
            dest = int(curr_line_split[2])

            cfg[source].append(dest)
            rev_cfg[dest].append(source)

    """
    Basic Blocks - Map that maps Basic Block ID --> Statement
    Statement is a tuple (lhs, rhs) ex: v1 = v2 + v3 --> (1, [2, 3])

    cfg --> Adjacency list of graph for Control Flow Graph
    rev_cfg --> Adjacency list of reverse graph for Control Flow Graph
    s --> Entry node
    x --> Exit node
    """

    return basic_blocks, cfg, rev_cfg, s, x, V

class DataFlowAnalysis:
    def __init__(self, basic_blocks: dict, cfg: dict, rev_cfg: dict, entry: int, exit: int, extra_info: dict):
        #Control Flow Graph
        self.basic_blocks = basic_blocks
        self.cfg = cfg
        self.rev_cfg = rev_cfg
        self.entry = entry
        self.exit = exit

        #Sub class defined functions
        self.extra_info = extra_info

        #Used for solving dataflow analysis
        self.domain = None #Set of dataflow values
        self.direction = None
        self.basic_blocks_dataflow_values = dict()

    @abstractmethod
    def top(self) -> set:
        pass
    
    @abstractmethod
    def set_domain(self):
        pass
    
    @abstractmethod
    def set_direction(self):
        pass

    @abstractmethod
    def get_boundary_condition_value(self) -> set:
        pass
    
    @abstractmethod
    def transfer_function(self, basic_block_id: int, dataflow_values: set) -> set:
        pass

    @abstractmethod
    def meet(self, meet_dataflow_values: list[set]) -> set:
        pass

    def _set_boundary_condition(self):
        boundary_condition_value = self.get_boundary_condition_value()
        if self.direction == "forward":
            #Add dummy entry
            self.cfg[0] = [self.entry]
            self.rev_cfg[0] = []
            self.rev_cfg[self.entry].append(0)

            #Add boundary condition
            self.basic_blocks_dataflow_values[0] = [set(), boundary_condition_value]
        elif self.direction == "backward":
            #Add dummy exit
            self.cfg[0] = []
            self.cfg[self.exit].append(0)
            self.rev_cfg[0] = [self.exit]

            #Add boundary condition
            self.basic_blocks_dataflow_values[0] = [boundary_condition_value, set()]
        else:
            raise NotImplementedError()
        
    def _init_dataflow_values_per_basic_block(self):
        for i in self.basic_blocks.keys():
            if self.direction == "forward":
                self.basic_blocks_dataflow_values[i] = [set(), self.top()]
            elif self.direction == "backward":
                self.basic_blocks_dataflow_values[i] = [self.top(), set()]
            else:
                raise NotImplementedError()


    def solve(self):
        self.set_domain() #Initialize domain of dataflow values
        self.set_direction() #Initialize direction of dataflow analysis
        self._init_dataflow_values_per_basic_block() #Initialize dataflow values at every basic block
        self._set_boundary_condition() #Initialize boundary condition at every basic block

        is_changed = True
        while is_changed:
            is_changed = False
            for basic_block_id in self.basic_blocks.keys():
                if self.direction == "forward":
                    data_flow_of_preds = []
                    for pred_basic_block_id in self.rev_cfg[basic_block_id]:
                        data_flow_of_preds.append(self.basic_blocks_dataflow_values[pred_basic_block_id][1])
                    new_in = self.meet(data_flow_of_preds)

                    if new_in != self.basic_blocks_dataflow_values[basic_block_id][0]:
                        is_changed = True
                        self.basic_blocks_dataflow_values[basic_block_id][0] = new_in

                    new_out = self.transfer_function(basic_block_id, new_in)

                    if new_out != self.basic_blocks_dataflow_values[basic_block_id][1]:
                        is_changed = True
                        self.basic_blocks_dataflow_values[basic_block_id][1] = new_out

                elif self.direction == "backward":
                    data_flow_of_succ = []
                    for succ_basic_block_id in self.cfg[basic_block_id]:
                        data_flow_of_succ.append(self.basic_blocks_dataflow_values[succ_basic_block_id][0])
                    new_out = self.meet(data_flow_of_succ)

                    if new_out != self.basic_blocks_dataflow_values[basic_block_id][1]:
                        is_changed = True
                        self.basic_blocks_dataflow_values[basic_block_id][1] = new_out

                    new_in = self.transfer_function(basic_block_id, new_out)

                    if new_in != self.basic_blocks_dataflow_values[basic_block_id][0]:
                        is_changed = True
                        self.basic_blocks_dataflow_values[basic_block_id][0] = new_in

                else:
                    raise NotImplementedError()

#End of Common Utilities

# Start of Reaching Definitions Specific
class ReachingDefinitions(DataFlowAnalysis):
    def top(self):
        return set()
    
    def set_domain(self):
        self.domain = self.extra_info["all_defs"]

    def set_direction(self):
        self.direction = "forward"

    def get_boundary_condition_value(self):
        return set()
    
    def meet(self, meet_dataflow_values: list[set]):
        #Union
        if len(meet_dataflow_values) == 0:
            return set()
        if len(meet_dataflow_values) == 1:
            return meet_dataflow_values[0]
        else:
            return_value = meet_dataflow_values[0]
            for i in range(1, len(meet_dataflow_values), 1):
                return_value = return_value.union(meet_dataflow_values[i])
            return return_value

    def transfer_function(self, basic_block_id: int, dataflow_values: set) -> set:
        stmt = self.basic_blocks[basic_block_id]
        if stmt == None:
            return dataflow_values
        elif stmt[0] == None:
            #No left hand side
            return dataflow_values
        else:
            kill = self.extra_info["defs_per_var"][stmt[0]]
            new_dataflow_values = dataflow_values - kill
            new_dataflow_values = new_dataflow_values.union({basic_block_id})
            return new_dataflow_values

def get_reaching_definitions_info(basic_blocks: dict, num_vars: int):
    all_defs = set()    
    defs_per_var = {}
    for i in range(1, num_vars + 1, 1):
        defs_per_var[i] = set()

    for basic_block_id, stmt in basic_blocks.items():
        if stmt != None and stmt[0] != None:
            all_defs = all_defs.union({basic_block_id})
            defs_per_var[stmt[0]] = defs_per_var[stmt[0]].union({basic_block_id})

    extra_info = {"all_defs": all_defs, "defs_per_var": defs_per_var}
    return extra_info

def dump_reaching_defintions_info(output_path: str, reaching_definitions: ReachingDefinitions):
    with open(output_path, "w") as file_obj:
        for basic_block_id in reaching_definitions.basic_blocks.keys():
            dataflow_values = reaching_definitions.basic_blocks_dataflow_values[basic_block_id][1]
            file_obj.write(f"rdout {basic_block_id}")
            for i in list(dataflow_values):
                file_obj.write(f" {i}")
            file_obj.write("\n")

def main():
    if len(sys.argv) != 3:
        print("Wrong arguments")
        return 1
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    basic_blocks, cfg, rev_cfg, entry, exit, num_vars = parse_input(input_path)

    extra_info = get_reaching_definitions_info(basic_blocks, num_vars)

    reaching_definitions = ReachingDefinitions(basic_blocks, cfg, rev_cfg, entry, exit, extra_info)
    reaching_definitions.solve()

    dump_reaching_defintions_info(output_path, reaching_definitions)


if __name__ == "__main__":
    main()