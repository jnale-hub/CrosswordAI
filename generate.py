import sys
from crossword import *
from queue import Queue


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        # Unary constraint: word length
        for var in self.domains:
            consistent_values = {val for val in self.domains[var] if len(val) == var.length}

            # Update the consistent_values to variable domains 
            self.domains[var] = consistent_values

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap:
            i, j = overlap
            domains_x = self.domains[x]
            domains_y = self.domains[y]

            # Update the domains x where there is no word x that is equal to word y
            self.domains[x] = {word_x for word_x in domains_x if any(word_x[i] == word_y[j] for word_y in domains_y)}

            # Return if the domain x is changed
            revised = len(self.domains[x]) != len(domains_x)

        return revised
        
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Initialize arcs if None
        if arcs is None:
            arcs = list(self.crossword.overlaps.keys())

        # Make a queue for arc processing
        q = Queue()
        for arc in arcs:
            q.put(arc)

        while not q.empty():
            x, y = q.get()

            # Revise the domain of x with respect to y
            if self.revise(x, y):
                if not self.domains[x]:
                    return False

                # Add neighbors of x without y to the queue
                neighbors = self.crossword.neighbors(x)
                neighbors.discard(y)
                for z in neighbors:
                    q.put((z, x))

        # Arc consistency is enforced, no empty domains
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        all_variables = set(self.crossword.variables)
        assigned_variables = set(assignment.keys())
        # Comapre all the variables to the assigned variables
        return all_variables == assigned_variables

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        for var, word in assignment.items():
            # Check if every value is the correct length
            if var.length != len(word):
                return False
            # Check if every values is distict
            for key, value in assignment.items():
                if var != key:
                    if word == value:
                        return False
            # Check if there is no conflict with the overlaps
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if neighbor in assignment:
                        if word[i] != assignment[neighbor][j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        heuristics = {}
        neighbors = self.crossword.neighbors(var)
        for word in self.domains[var]:
            # Check if the word is not in the assignment
            if word not in assignment:
                ruled_out = 0
                for neighbor in neighbors:
                    if word in self.domains[neighbor]:
                        ruled_out += 1
                heuristics[word] = ruled_out

        # Sort values based on the number of ruled-out values (ascending order)
        sorted_values = sorted(heuristics.keys(), key=lambda word: heuristics[word])
        
        return sorted_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Find unassigned variables
        unassigned_variables = [var for var in self.crossword.variables if var not in assignment]

        if not unassigned_variables:
            return None  # All variables are assigned

        # Sort unassigned variables based on criteria
        def variable_priority(var):
            remaining_values = len(self.domains[var])
            degree = -len(self.crossword.neighbors(var))
            return (remaining_values, degree)

        sorted_variables = sorted(unassigned_variables, key=variable_priority)

        return sorted_variables[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
