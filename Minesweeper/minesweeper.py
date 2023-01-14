import itertools
import random
from shutil import move


class Minesweeper():
    """
    Minesweeper game representation
    """
    
    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
       
    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        temp = set()
        #If the number of mines is the same as the number of cells
        #Then all cells are mines
        if(self.count == len(self.cells)): 
            for cell in self.cells:
                temp.add(cell)
        return temp
         
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        temp = set()
        #If the number of mines is 0
        #Then all cells are safe
        if(self.count == 0):
            for cell in self.cells:
                temp.add(cell)
        return temp
         
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #If a cell is a mine can be disambiguated from cells set
        #Reduce count once discarded
        if(cell in self.cells):
            self.cells.remove(cell)
            self.count-=1
                  

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #If a cell is safe can be disambiguated from cells set
        if(cell in self.cells):
            self.cells.remove(cell)
            
        


class MinesweeperAI():
    """
    Minesweeper game player
    """
    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        i=0

        #Marks mine in all Sentences that contain the mine
        while i < len(self.knowledge):
            self.knowledge[i].mark_mine(cell)
            if(not self.knowledge[i].cells):
                self.knowledge.remove(self.knowledge[i])
                i-=1
            i+=1

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        i=0

        #Marks safe in all Sentences that contain the safe cell
        while i < len(self.knowledge):
            self.knowledge[i].mark_safe(cell)
            if(not self.knowledge[i].cells):
                self.knowledge.remove(self.knowledge[i])
                i-=1
            i+=1

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as miness
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        all_known_safes = set()
        all_known_mines = set()

        #1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        #2) mark the cell as safe
        self.mark_safe(cell)
        cells = set()

        #Iterate through neighbors and discard moves made, safes, and mines
        for i in range(3):
            for j in range(3):
                toAdd = (cell[0]+i-1,cell[1]+j-1)
                if toAdd==cell or toAdd[0] < 0 or toAdd[1] < 0 or toAdd[0] >= self.height or toAdd[1] >= self.width or toAdd in self.moves_made or toAdd in self.safes:
                    continue
                if toAdd in self.mines:
                    #Update count to reflect true number of mines before discarding
                    count-=1
                    continue
                cells.add(toAdd)
        newSentence = Sentence(cells,count)

        #3) add a new sentence to the AI's knowledge base
        #   based on the value of `cell` and `count`
        self.knowledge.append(newSentence)

        #4) mark any additional cells as safe or as miness
        #   if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            all_known_safes = all_known_safes.union(sentence.known_safes())
            all_known_mines = all_known_mines.union(sentence.known_mines())
        for unmarkedSafe in all_known_safes:
            self.mark_safe(unmarkedSafe)
        for unmarkedMine in all_known_mines:
            self.mark_mine(unmarkedMine)

        #5) add any new sentences to the AI's knowledge base
        templist = []
        for sentence in self.knowledge:
            for sentence1 in self.knowledge:
                if(sentence1 == sentence):
                    continue
                s1Tos = sentence1.cells.issubset(sentence.cells) # s1Tos = sentence1 is a subset of sentence T/F

                #No need to check for sTos1 because will eventually encounter again as swapped 
                if(s1Tos):
                    difference = sentence.cells-sentence1.cells
                    sentenceA = Sentence(difference,abs((sentence.count-sentence1.count)))
                    if(sentenceA.cells and sentenceA not in self.knowledge and sentenceA not in templist):
                        templist.append(sentenceA)
        self.knowledge.extend(templist)
                
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i in range(self.height):
            for j in range(self.width):
                move = (i,j)
                if(move in self.safes and not move in self.moves_made):
                    return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        eligibles = []
        for i in range(self.height):
            for j in range(self.width):
                move = (i,j)
                if(not move in self.mines and not move in self.moves_made):
                    eligibles.append(move)
        if(not eligibles):
            return None            
        index = random.randrange(0,len(eligibles))
       
        return eligibles[index]
