# FIFO
class Node:
    def __init__(self, name: str, parent = None) -> None:
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

def DFS(S: Node, T: Node):
    global Open, Close, data
    Open += [S]
    while True:
        # nếu tập biên rỗng -> return
        if len(Open) == 0:
            print('Not Found!')
            return
        
        # lấy ra node từ tập biên, cho vào tập đóng và xét
        O = Open.pop(0)
        Close += [O]
        # print(O)

        # kiểm tra xem node O có bằng node đích chưa
        if O == T:
            print('Found!')
            path(O)
            return
        
        # nếu chưa thì duyệt các node kề với node O
        lst = []
        for x in data[O.name]:
            tmp = Node(x, O)
            if (not tmp in Close):
                lst += [tmp]
        Open = lst + Open

# def DFS(S: Node, T: Node):
#     global Close, Open, data
#     Close += [S]
#     if S == T:
#         print('Found!')
#         path(S)
#         return
#     for x in data[S.name]:
#         tmp = Node(x, S)
#         if tmp not in Close:
#             DFS(tmp, T)
        

if __name__ == '__main__':
    data = {}
    data['S'] = ['A', 'B', 'C', 'E']
    data['A'] = ['D']
    data['B'] = ['F']
    data['C'] = ['B', 'F', 'H']
    data['D'] = ['E']
    data['E'] = ['G']
    data['F'] = ['G']
    data['H'] = ['G'] 
    data['G'] = []
    data['K'] = []
    # tập các node biên 
    Open = []
    # tập các node đóng
    Close = []

    DFS(Node('S'), Node('G'))