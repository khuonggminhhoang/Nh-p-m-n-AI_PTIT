from queue import PriorityQueue
COL = 10
RAW = 9
# COL = 4
# RAW = 4
vct = ((-1, 0), (0, 1), (1, 0), (0, -1))

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

def path(O: Node) -> None:
    print(f'({O.i}, {O.j})', end=' ')
    if O.parent is not None:
        path(O.parent)
    return

def aStar(src: Node, dest: Node, grid: list) -> None:
    global openList, closedList

    if not isValid(src.i, src.j) or not isValid(dest.i, dest.j):
        print('Source or destination is invalid!')
        return
    
    if not isUnBlocked(src.i, src.j, grid) or not isUnBlocked(dest.i, dest.j, grid):
        print('Source or the destination is blocked')
        return

    src.h = calcHeuristic(src, dest)
    openList.put(src)

    while True:
        if openList.empty():
            print('Not Found!')
            return
        
        O: Node = openList.get()
        closedList[O.i][O.j] = True         # đánh dấu điểm đã xét bằng true

        if O == dest:
            print('Found!')
            print(O)
            print(f'min distance: {O.g}')
            return
        
        for index in range(4):
            x = O.i + vct[index][0]
            y = O.j + vct[index][1]
            if isValid(x ,y) and not closedList[x][y] and isUnBlocked(x, y, grid):
                tmpNode = Node(x, y, O, O.g + 1)
                tmpNode.h = calcHeuristic(tmpNode, dest)
                
                lst = openList.queue
                if tmpNode in lst:
                    for x in lst:
                        if x == tmpNode and (tmpNode.g + tmpNode.h) < (x.g +  x.h):
                            x.g = tmpNode.g
                            x.h = tmpNode.h
                            x.parent = tmpNode.parent 
                            break
                    openList = PriorityQueue()
                    for x in lst:
                        openList.put(x)
                else:
                    openList.put(tmpNode)

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

    # grid = (
    #     (1, 0, 1, 0),
    #     (1, 1, 1, 1),
    #     (1, 0, 1, 0),
    #     (1, 1, 1, 1)
    # )
    
    src = Node(0, 0)
    dest = Node(8, 0)

    openList = PriorityQueue()
    closedList = [[False for _ in range(COL)] for _ in range(RAW)]
    aStar(src, dest, grid)

    for x in closedList:
        print(*x)