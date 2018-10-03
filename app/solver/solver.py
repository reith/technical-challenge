from itertools import product
from exc import ApiError
import math

class InputError(ApiError):
    status = 400
    def __init__(self, message):
        super(InputError, self).__init__()
        self.message = message

def solver(problem, repetitive=False):
    colors = problem.get("colors")
    customers = problem.get("customers")
    demands = problem.get("demands")

    glossies = []
    matte = {}
    for c in range(customers):
        try:
            length = demands[c][0]
        except IndexError:
            raise InputError("Customer #{} demands are not known".format(c+1))
        demand = demands[c][1:]
        glossies.append([])
        if length * 2 != len(demand):
            raise InputError(
                "Customer #{} have {} demands but given {} colors and types"
                .format(c+1, length, len(demand))
            )
        for i in range(length):
            (color, is_matte) = (demand[2 * i], demand[2 * i + 1])
            if not 1 <= color <= colors:
                raise InputError(
                    "Invalid color #{} for customer #{}"
                    .format(color, color, c+1)
                )
            if is_matte:
                if matte.has_key(c):
                    raise InputError(
                        "Customer #{} has multiple matte choices: {}, {}"
                        .format(c+1, matte[c]+1, color)
                    )
                matte[c] = color - 1
            else:
                glossies[c].append(color - 1)
    starter = start_repetitive if repetitive else start
    solved, solution = starter(colors, customers, glossies, matte)
    if solved:
        return " ".join(map(str, solution))
    else:
        return "IMPOSSIBLE"

def check(solution, customers, glossies, matte):
    for customer in range(customers):
        good = False
        for i in range(len(solution)):
            if solution[i] == 0 and i in glossies[customer]:
                good = True
            if solution[i] == 1 and matte.get(customer) == i:
                good = True
        if not good:
            return False
    return True


def start(colors, customers, glossies, matte):
    solution = [0] * colors
    if check(solution, customers, glossies, matte):
        return True, solution
    result = None
    solved = False
    for i in range(len(solution)):
        if solution[i] == 0:
            solved_i, result_i = reduce(solution, i, customers, glossies, matte)
            if solved_i:
                if not solved:
                    solved = True
                    result = result_i
                if sum(result_i) < sum(result):
                    result = result_i
    return solved, result

def reduce(solution_on_stack, change, customers, glossies, matte):
    solution = list(solution_on_stack)
    solution[change] = 1
    if check(solution, customers, glossies, matte):
        return True, solution
    if sum(solution) == len(solution):
        return False, None
    result = None
    solved = False
    for i in range(len(solution)):
        if solution[i] == 0:
            solved_i, result_i = reduce(solution, i, customers, glossies, matte)
            if solved_i:
                if not solved:
                    solved = True
                    result = result_i
                if sum(result_i) < sum(result):
                    result = result_i
    return solved, result

def start_repetitive(colors, customers, glossies, matte):
    """
    This a non-recursive solution.  We test all possible solutions in a loop
    so we won't hit by stack limit on huge and well-constrainted input
    """
    least_mattes = colors
    result = None
    possible_solutions = [list(g) for g in product([0, 1], repeat=colors)]
    all_mattes = list(matte.values())
    i = skip_next = 0
    for solution_g in product([0, 1], repeat=colors):
        solution = list(solution_g)
        if skip_next > 0:
            skip_next -= 1
        else:
            can_skip, skip_count = could_skip_iteration(colors, all_mattes, i)
            if can_skip:
                skip_next = skip_count - 1
            elif check(solution, customers, glossies, matte):
                if result is None or sum(solution) < least_mattes:
                    least_mattes = sum(solution)
                    result  = solution
        i += 1
    return result is not None, result

def could_skip_iteration(colors, mattes, i):
    """
    Some iterations could be skipped since they can't result in a optimal
    solutions.  For example we don't need make batch of mattes on a color if
    no customer wants that color in matte.
    """
    if i == 0:
        return False, 0
    iter_log = math.log(i, 2)
    new_matte_p = colors - int(iter_log) - 1 if iter_log.is_integer() else -1
    if new_matte_p > 0 and new_matte_p not in mattes:
        return True, i
    else:
        return False, 0
