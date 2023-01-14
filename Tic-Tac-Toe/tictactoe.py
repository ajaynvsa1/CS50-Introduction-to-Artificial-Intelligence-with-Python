"""
Tic Tac Toe Player
"""

import math
from sys import _xoptions

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xCounter = 0
    oCounter = 0
    for i in range(3):
        for j in range(3):
            if(board[i][j] == X):
                xCounter+=1
            elif(board[i][j] == O):
                oCounter += 1
    return X if xCounter == oCounter else O
    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    result = set()
    for i in range(3):
        for j in range(3):
            if(board[i][j] == EMPTY):
                result.add((i,j))
    return result

    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newBoard = initial_state()
    
    for i in range(3):
        for j in range(3):
            newBoard[i][j] = board[i][j]
    if(terminal(board)):
        return newBoard
    if(action != None):
        if(action[0]>2 or action[0] < 0):
            raise ValueError
        if(action[1]>2 or action[1] < 0):
            raise ValueError
    else:
        return newBoard
    newBoard[action[0]][action[1]] = player(board)
    return newBoard
    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if(board[i][0] != EMPTY):
            if(board[i][0] == board[i][1] and board[i][1] == board[i][2]):
                return board[i][0]
    for i in range (3):
        if(board[0][i] != EMPTY):
            if(board[0][i] == board[1][i] and board[1][i] == board[2][i]):
                return board[0][i]
    if(board[0][0] != EMPTY):
        if(board[0][0] == board[1][1] and board[1][1] == board[2][2]):
            return board[0][0]
    if(board[2][0] != EMPTY):
        if(board[2][0] == board[1][1] and board[1][1] == board[0][2]):
            return board[2][0]
    return None
    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return ((len(actions(board)) == 0) or (winner(board) != None))
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    theWinner = winner(board)
    if(theWinner == X):
        return 1
    elif(theWinner == O):
        return -1
    return 0
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #Copying
    newBoard = initial_state()
    for i in range(3):
        for j in  range(3):
            newBoard[i][j] = board[i][j]
    newState = State(newBoard,None,None) #Convert to State
    stack = []
    stack.append(newState)
    while(stack): #dfs
        curr = stack[-1] #curr is e.o.s
        #curr is due to be scored if curr is terminal or all children of curr have been scored
        if(curr.terminal or curr.unprocessedAction == len(curr.actions)): #Scoring
            #Not terminal but due to be scored
            if(not curr.terminal): 
                #Ternary operator for scoring
                curr.score = max(curr.actionScores) if player(curr.board) == X else min(curr.actionScores)
                #Finding the action that gave the score 
                index = curr.actionScores.index(curr.score)
                curr.scoreProvider = curr.actions[index]
            #To avoid querying attributes of NoneType (also if curr.parent == None, curr is newState) 
            if(curr.parent != None): 
                index = curr.parent.unprocessedAction-1
                curr.parent.actionScores[index] = curr.score
                #If child has extreme score in alignment with parent player's objective, 
                #Then no need to check other children to score parent
                if(curr.score == 1 and curr.parent.player == X):  
                    curr.parent.unprocessedAction = len(curr.parent.actions)
                elif(curr.score == -1 and curr.parent.player == O):
                    curr.parent.unprocessedAction = len(curr.parent.actions)
            stack.remove(curr)
        #Add new State to stack
        else: 
            initAction = curr.actions[curr.unprocessedAction]
            stack.append(State(result(curr.board,initAction),initAction,curr))
            curr.unprocessedAction = curr.unprocessedAction + 1
    return newState.scoreProvider
    raise NotImplementedError

class State():
    def __init__(self,board,initAction,parent):
        self.board = board
        self.terminal = terminal(board)
        self.player = player(board)
        self.actions = list(actions(board))
        self.actionScores = [0]*len(self.actions) #corresponds index-wise to actions
        self.unprocessedAction = 0 #index for actionScores 
        self.initAction = initAction #action from parent that got to this node
        self.parent = parent #parent node of type State 
        self.score = None if not self.terminal else utility(board)
        self.scoreProvider = None
        