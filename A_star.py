from queue import PriorityQueue

class Node:
    def __init__(self, name, parent = None, g = 0, h = 0) -> None:
        self.name = name
        self.parent = parent
        self.g = g
        self.h = h
    
    def __lt__(self, other) -> bool:
        return self.g + self.h < other.g + other.h
    
    def __eq__(self, other) -> bool:
        return self.name == other.name
    
def path(O: Node) -> None:
    print(O.name, end=' ')
    if O.parent is not None:
        path(O.parent)
    return

def Astar(S: Node, T: Node) -> None:
    global Open, Close, data
    S.h = data[S.name][-1]      # set giá trị h cho Node S

    Open.put(S)
    while True: 
        if Open.empty():
            print('Not Found!')
            return
        
        O = Open.get()
        Close.put(O)

        if O == T:
            print('Found!')
            path(O)
            print('\nmin distance:', O.g)
            return

        for name, weight in data[O.name][:-1]:
            h = data[O.name][-1]
            tmp = Node(name, O, O.g + weight, h)        # tmp là Node kề với Node O

            lst = Open.queue
            if tmp in lst:
                for x in lst:
                    if x == tmp and (tmp.g + tmp.h) < (x.g + x.h):              # kiểm tra nếu Node tmp đang xét có giá trị đường đi tới đích nhỏ hơn thì cập nhật giá trị g, h
                        x.g = tmp.g
                        x.h = tmp.h
                        x.parent = tmp.parent                            # nhớ cập nhật cả thằng cha của x nữa
                        break
                Open = PriorityQueue()
                for x in lst:
                    Open.put(x)
            else:
                Open.put(tmp)
                

if __name__ == '__main__':
    data  = {
        'S' : [('A', 2), ('B', 3), 6],
        'A' : [('D', 3), 4],
        'B' : [('C', 3), ('D', 1), 4],
        'C' : [('E', 2), 3],
        'D' : [('C', 1), ('F', 3), 4],
        'E' : [('G', 1), 1],
        'F' : [('G', 2), 1], 
        'G' : [0]
    }

    Open = PriorityQueue()
    Close = PriorityQueue()

    Astar(Node('S'), Node('G'))