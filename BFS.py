# LIFO
class Node:
    def __init__(self, name: str, parent = None ):
        self.name = name
        self.parent = parent

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __str__(self) -> str:
        return f'{self.name} <- {self.parent}'
    

def path(O: Node):
    print(O.name, end=' ')
    if O.parent is not None:
        path(O.parent)
    return

def BFS(S: Node, T: Node):
    global Open, Close, data
    Open += [S]
    while True:
        if len(Open) == 0:
            print('Not Found!')
            return
        
        # lấy node đầu tiên trong tập biên ra cho vào tập đóng để xét
        O = Open.pop(0)
        Close += [O]

        # nếu node đang xét trong tập đóng bằng node đích -> return
        if O == T:
            print('Found!')
            path(O)
            return
        
        # duyệt các node kề với node O đang xét, nếu các node chưa nằm trong tập đóng và tập biên thì thêm nó vào cuối tập biên
        for x in data[O.name]:
            tmp = Node(x, O)
            if (not tmp in Open) and (not tmp in Close):
                Open += [tmp]

if __name__ == '__main__':
    # data = {}
    # data['S'] = ['A', 'B', 'C', 'E']
    # data['A'] = ['D']
    # data['B'] = ['F']
    # data['C'] = ['B', 'F', 'H']
    # data['D'] = ['E']
    # data['E'] = ['G']
    # data['F'] = ['G']
    # data['H'] = ['G']
    # data['G'] = []

    data = {
        'S' : ['A', 'B'],
        'A' : ['C', 'D'],
        'B' : ['D'],
        'C' : ['E', 'F'],
        'D' : ['F'],
        'E' : ['G1'],
        'F' : ['G2'],
        'G1' : [],
        'G2' : []
    }

    # list chứa tập các node mở (nút biên, có thể được mở rộng)
    Open = []
    # list chứa tập các node đóng (nút đã được mở rộng)
    Close = []

    BFS(Node('S'), Node('G2'))