COL = 10
RAW = 9

class Node:
    def __init__(self, i, j, parent = None, g = 0, h = 0) -> None:
        self.i = i
        self.j = j
        self.parent = parent
        self.g = g
        self.h = h

    def __eq__(self, other) -> bool:
        return self.i == other.i and self.j == other.j
    
    def __lt__(self, other) -> bool:
        return self.g + self.h < other.g + other.h
    
    def __str__(self) -> str:
        return f'({self.i},{self.j}) <- {self.parent}'

def isValid(i: int, j : int) -> bool:
    return 0 <= i < RAW and 0 <= j < COL

def isUnBlocked(i: int, j : int, grid: tuple) -> bool:
    return grid[i][j] != 0


def calcHeuristic(S : Node, T: Node) -> int:
    return  abs(T.i - S.i) + abs(T.j - S.j)





if __name__ == '__main__':
    grid = (
            (1, 0, 1, 1, 1, 1, 0, 1, 1, 1),
            (1, 1, 1, 0, 1, 1, 1, 0, 1, 1),
            (1, 1, 1, 0, 1, 1, 0, 1, 0, 1),
            (0, 0, 1, 0, 1, 0, 0, 0, 0, 1),
            (1, 1, 1, 0, 1, 1, 1, 0, 1, 0),
            (1, 0, 1, 1, 1, 1, 0, 1, 0, 0),
            (1, 0, 0, 0, 0, 1, 0, 0, 0, 1),
            (1, 0, 1, 1, 1, 1, 0, 1, 1, 1),
            (1, 1, 1, 0, 0, 0, 1, 0, 0, 1)
    )
    
    src = Node(0, 0)
    dest = Node(8, 0)