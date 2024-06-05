import sys
import os

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)


from queue import PriorityQueue

COL = 30
RAW = 32

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
        return f'({self.i},{self.j}, f={self.g + self.h}) <- {self.parent}'

def isValid(i: int, j : int) -> bool:
    return 0 <= i < RAW and 0 <= j < COL

def isUnBlocked(i: int, j : int, grid: tuple) -> bool:
    return grid[i][j] < 3    # sửa ở đây


def calcHeuristic(S : Node, T: Node) -> int:
    return  abs(T.i - S.i) + abs(T.j - S.j)

def path(O: Node) -> None:
    print(f'({O.i}, {O.j})', O.g + O.h, end=' ')
    if O.parent is not None:
        path(O.parent)
    return

def aStar(src: Node, dest: Node, grid: list) -> Node:
    visited = [[False for _ in range(COL)] for _ in range(RAW)]
    openedList = PriorityQueue()
    closedList = PriorityQueue()

    if not isValid(src.i, src.j) or not isValid(dest.i, dest.j):
        print('Source or destination is invalid!')
        return
    
    if not isUnBlocked(src.i, src.j, grid) or not isUnBlocked(dest.i, dest.j, grid):
        print('Source or the destination is blocked')
        return

    src.h = calcHeuristic(src, dest)
    openedList.put(src)

    while not openedList.empty():
        if openedList.empty():
            print('Not Found!')
            return
        
        O: Node = openedList.get()
        visited[O.i][O.j] = True
        closedList.put(O)               # đẩy Node vào close

        if O == dest:
            print('Found!')
            print(O, O.g + O.h)
            print(f'min distance: {O.g}')
            return O
        
        for index in range(4):
            x = O.i + vct[index][0]
            y = O.j + vct[index][1]
            if isValid(x ,y) and isUnBlocked(x, y, grid) and not visited[x][y]:
                tmpNode = Node(x, y, O, O.g + 1)     
                tmpNode.h = calcHeuristic(tmpNode, dest)
                
                # kiểm tra Node tmp có nằm trong open hay không, nếu có thì cập nhật giá trị đường đi, nếu không kiểm tra tập close
                lstOpen = openedList.queue
                flag1 = False
                for o in lstOpen:
                    if o == tmpNode and (tmpNode.g + tmpNode.h) < (o.g +  o.h):
                        o.g = tmpNode.g
                        o.h = tmpNode.h
                        o.parent = tmpNode.parent 
                        flag1 = True
                        break

                if flag1:
                    openedList = PriorityQueue()
                    for o in lstOpen:
                        openedList.put(o)

                # kiểm tra tập close, nếu có tồn tại và Node trong close có f lớn hơn tmpNode thì put vào open
                flag2 = False
                lstColse = closedList.queue
                for o in lstColse:
                    if o == tmpNode and (tmpNode.g + tmpNode.h) < (o.g +  o.h):
                        openedList.put(tmpNode)
                        flag2 = True
                        break
                
                # nếu không nằm trong open và close thì đẩy vào open
                if not flag1 and not flag2:
                    openedList.put(tmpNode)
