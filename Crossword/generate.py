import sys
from crossword import *


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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        #Enforce length
        for var in self.crossword.variables:
            remove = set()
            for val in self.domains[var]:
                if(len(val) != var.length):
                    remove.add(val)
            for val in remove:
                self.domains[var].remove(val)     
            

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        #Set of all values in x-domain to be removed
        remove = set()
        for valx in self.domains[x]:
            for valy in self.domains[y]:
                #If found successful pair go to next value in x-domain
                if(valx[self.crossword.overlaps[x,y][0]] == valy[self.crossword.overlaps[x,y][1]]):
                    break
                #If haven't found succesful pair by last value in y-domain mark removed
                elif(valy == list(self.domains[y])[len(self.domains[y])-1]):
                    remove.add(valx)
                    revised = True                      
        for valx in remove:
            self.domains[x].remove(valx)
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        q=[]
        #Reinitialize q with starting arcs
        if arcs == None:
            for var in self.crossword.variables:
                for neighbor in self.crossword.neighbors(var):
                    q.append((var,neighbor))  
        else:
            q = arcs
        #While q has elements
        while q:
            #Poll queue
            x,y = q[0]
            q.remove(q[0]) 

            #If revise made changes to domain of x in arc
            if(self.revise(x,y)):
                #If domain empty problem is unsolvable
                if(not self.domains[x]):
                    return False
                #Add new arcs for new x domain and neighbors
                for z in (self.crossword.neighbors(x) - set([y])):
                    q.append((z,x))
        #Return True when q of arcs to be processed is empty
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #If all Variables have an assigned value return True
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #temp will contain values assigned to the Variables in assignment
        temp = set()
        for item in assignment.items():
            temp.add(item[1])
        #Checking for duplicates in assignment.values()
        if(len(temp) != len(assignment)):
            return False
        #Check if overlaps match up for given assignment between two Variable values (and so on for every pair)
        for var in assignment:
            operSet = set(assignment.keys()).intersection(self.crossword.neighbors(var))
            valx = assignment[var]
            for neighbor in operSet:
                valy = assignment[neighbor]
                if(valx[self.crossword.overlaps[var,neighbor][0]] != valy[self.crossword.overlaps[var,neighbor][1]]):
                    return False      
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """ 
        result = {} #Maps value to number of other values eliminated
        unassignedNeighbors = self.crossword.neighbors(var)-assignment.keys()
        for valx in self.domains[var]:
            #Counter to keep track of values choosing current value for this Variable will eliminate
            counter = 0
            for neighbor in unassignedNeighbors:
                for valy in self.domains[neighbor]:
                    #If not compatible, increment elim counter
                    if(valx[self.crossword.overlaps[var,neighbor][0]] != valy[self.crossword.overlaps[var,neighbor][1]]):
                        counter+=1
            result[valx] = counter
        #Sort dict items by values of dict (dict values are elim counters itc)
        resultNew = dict(sorted(result.items(), key=lambda item: item[1]))
        resultList = []
        for key in resultNew:
            resultList.append(key)
        return resultList

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        #Unassigned vars are vars that are not in assignment as keys
        unassignedVariables = list(self.crossword.variables-assignment.keys()) 
        #Initially sort so that smallest domain first
        unassignedVariables.sort(key=lambda var: len(self.domains[var]))
        unVarList = []
        #Put all vars tied for first in smallest domain together in a list
        for var in unassignedVariables:
            if(len(self.domains[var]) == len(self.domains[unassignedVariables[0]])):
                unVarList.append(var)
        #Sort in descending order of degree
        unVarList.sort(key = lambda var: len(self.crossword.neighbors(var)), reverse=True)
        return unVarList[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #If complete, complete
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        
        for value in self.order_domain_values(var,assignment):
            #Copy to check if new assignment will be consistent
            assignmentCpy = assignment.copy()
            assignmentCpy[var] = value
            
            if self.consistent(assignmentCpy):
                assignment[var] = value
                #Continue backtracking search with new assignment map
                result = self.backtrack(assignment)
                if result != None:
                    return result
                #If result is None remove latest assignment
                del assignment[var]
        #If failed assignment map entry
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
