from queue import PriorityQueue

class Node:
    def __init__(self, name, parent = None, g = 0) -> None:             # g = cost
        self.name = name
        self.parent = parent
        self.g = g                                  # giá trị đường đi từ đầu tới đỉnh đang xét

    def __lt__(self, other) -> bool:
        return self.g < other.g
    
    def __eq__(self, other) -> bool:
        return self.name == other.name
    
    def __str__(self) -> str:
        return f'{self.name} <- {self.g}'

def path(O: Node) -> None:
    print(O.name, end=' ')
    if O.parent is not None:
        path(O.parent)
    return

def UCS(S: Node, T: Node) -> None:
    global Open, Close, data
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
        
        # duyệt các Node con của node O
        for name, weight in data[O.name]:
            tmp = Node(name, O, O.g + weight)               # cộng trọng số tính chi phí đường đi từ S đến điểm đang xét
            # chuyển pqueue về list các Node
            lst = Open.queue
            if tmp in lst:
                for x in lst:
                    if tmp == x and tmp.g < x.g:                    # kiểm tra nếu Node tmp đang xét có giá trị đường đi nhỏ hơn thì cập nhật giá trị đường đi
                        x.g = tmp.g     
                        x.parent = tmp.parent                       # nhớ cập nhật cả thằng cha của x nữa
                        break
                Open = PriorityQueue()
                for x in lst:
                    Open.put(x)
            else:
                Open.put(tmp)
            
if __name__ == '__main__':
    # data = {
    #     'S' : [('A', 5), ('B', 3), ('C', 4)],
    #     'A' : [('D', 1)],
    #     'B' : [('A', 1), ('E', 8)],
    #     'C' : [('E', 1)],
    #     'D' : [('G', 2)],
    #     'E' : [('G', 1)],
    #     'G' : []
    # }
    data = {
        'S' : [('A', 3), ('B', 5)],
        'A' : [('C', 4), ('D', 1)],
        'B' : [('D', 4)],
        'C' : [('E', 1), ('F', 1)],
        'D' : [('F', 2)],
        'E' : [('G1', 6)],
        'F' : [('G2', 5)],
        'G1' : [],
        'G2' : []
    }

    Open = PriorityQueue()
    Close = PriorityQueue()

    UCS(Node('S'), Node('G1'))
