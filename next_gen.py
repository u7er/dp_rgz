import networkx as nx
import matplotlib.pyplot as plt
import random
import math


# implementation of welsh_powell algorithm
def welsh_powell(G):
    # sorting the nodes based on it's valency
    node_list = sorted(G.nodes(), key=lambda x: G.neighbors(x))
    col_val = {}  # dictionary to store the colors assigned to each node
    col_val[node_list[0]] = 0  # assign the first color to the first node
    # Assign colors to remaining N-1 nodes
    for node in node_list[1:]:
        available = [True] * len(G.nodes())  # boolean list[i] contains false if the node color 'i' is not available

        # iterates through all the adjacent nodes and marks it's color as unavailable, if it's color has been set already
        for adj_node in G.neighbors(node):
            if adj_node in col_val.keys():
                col = col_val[adj_node]
                available[col] = False
        clr = 0
        for clr in range(len(available)):
            if available[clr] == True:
                break
        col_val[node] = clr
    # print col_val
    return col_val


graph_edge_list = []


# takes input from the file and creates a undirected graph
def CreateGraph(our, fr, to):
    if fr > to:
        tmp = fr
        fr = to
        to = tmp
    if fr < 0 or to < 0:
        print("Error. Range is not correct.")
        return False

    if our:
        G = nx.Graph()
        f = open('input.txt')
        n = int(f.readline())
        for i in range(n):
            graph_edge = f.readline().split()
            G.add_edge(graph_edge[0], graph_edge[1])
            graph_edge_list.append(graph_edge[0])
            graph_edge_list.append(graph_edge[1])
    else:
        # G = nx.random_geometric_graph(random.randint(fr, to), 0.2, p=1, seed=random.randint(1, 10))
        # G = nx.lollipop_graph(random.randint(fr, to), to)
        # G = nx.full_rary_tree(10, 40)
        G = nx.balanced_tree(2, 5)
    # G = nx.grid_2d_graph(fr, to)

    return G


# draws the graph and displays the weights on the edges
def DrawGraph(G, col_val):
    pos = nx.spring_layout(G)
    values = [col_val.get(node, 'black') for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_color=values, edge_color='red', width=1,
            alpha=0.7)  # with_labels=true is to show the node number in the output graph


def is_prime(n):
    if n <= 1:
        return False
    if (n & 1) == 0:
        return False
    b = int(math.sqrt(n)) + 2
    for i in range(3, b, 2):
        if (n % i) == 0:
            return False
    return True


def max_prime_rand(maxi):
    prime = 0
    while True:
        prime = random.getrandbits(maxi)
        if is_prime(prime):
            break
    return prime


def powd(number, degree, module):
    answer = 1
    number %= module
    while degree > 0:
        if degree & 1:
            answer = (answer * number) % module
        number = number * number % module
        degree >>= 1
    return answer


def gcd(a, b):
    while b > 0:
        a %= b
        tmp = a
        a = b
        b = tmp
    return a


def test_fermat(p, maxi):
    if p == 2:
        return True
    for i in range(0, 100, 1):
        tmp = random.getrandbits(maxi)
        if gcd(tmp, p) != 1:
            return False
        if powd(tmp, p - 1, p) != 1:
            return False
    return True


def generate_pq(maxi):
    rsa_vars = [0, 0, 0]
    rsa_vars[1] = max_prime_rand(maxi)
    while True:
        rsa_vars[0] = 2 * rsa_vars[1] + 1
        if is_prime(rsa_vars[0]):  # test_fermat(rsa_vars[0], maxi):
            for rsa_vars[2] in range(2, rsa_vars[0], 1):
                if powd(rsa_vars[2], rsa_vars[1], rsa_vars[0]) != 1:
                    return rsa_vars
        rsa_vars[1] = max_prime_rand(maxi)


def gcd_extended(a, b):
    if a < b:
        tmp = a
        a = b
        b = tmp
    u = [a, 1, 0]
    v = [b, 0, 1]
    t = [0, 0, 0]
    while v[0] != 0:
        q = u[0] / v[0]
        t[0] = u[0] % v[0]
        t[1] = u[1] - q * v[1]
        t[2] = u[2] - q * v[2]
        u = list(v)
        v = list(t)
    return u


def generate_rsa_vars(maxi):
    rsa_vars = []
    # P Q N C D
    rsa_vars.append(max_prime_rand(30))
    rsa_vars.append(max_prime_rand(30))
    rsa_vars.append(rsa_vars[0] * rsa_vars[1])
    d = 2
    fi = (rsa_vars[0] - 1) * (rsa_vars[1] - 1)
    while gcd(d, fi) != 1:
        d += 1
    c = gcd_extended(d, fi)[2]
    if c < 0:
        c = c + fi

    rsa_vars.append(c)
    rsa_vars.append(d)
    # P Q N C D
    return rsa_vars


def bitExtracted(number, k, p):
    return ((1 << k) - 1) & (number >> (p - 1))


def mspa(col_val, max_colors):
    for i in range(0, 5 * len(nx.to_edgelist(G)), 1):
        colors = [i for i in range(max_colors)]
        # shuffle colors
        random.shuffle(colors)
        col_val_shuffle = dict(col_val)

        # Alice
        # shuffle our dictionary
        # dict[key] = col[dict[key]]
        for key in col_val_shuffle:
            col_val_shuffle[key] = colors[col_val_shuffle[key]]

        # Alice
        # Generate Ri, shift and change two last bits in sequence on color vertex
        # (for history: # numb_vertex = {key: ((numb_vertex[key] << 2) | col_val_shuffle[key]) for key in numb_vertex})
        R = {key: (((random.getrandbits(31)) << 2) | col_val_shuffle[key]) for key in col_val_shuffle}
        rsa_var = {key: generate_rsa_vars(20) for key in col_val_shuffle}
        # Alice
        # Processing Zv = Rv^Dv % Nv per vertex
        Z = {key: powd(R[key], rsa_var[key][4], rsa_var[key][2]) for key in col_val_shuffle}
        # Move to Bob Nv Dv Zv
        ndz = {key: [rsa_var[key][2], rsa_var[key][4], Z[key]] for key in col_val_shuffle}
        # Get edges from our graph G
        edges = nx.to_edgelist(G)
        # Bob pick one random edge and sent him to Alice
        bob_rand_edges = list(edges)[random.randint(0, len(list(edges)) - 1)]
        # Bob saying to Alice what edges he picked
        # Hi, i'm picked that edges: bob_rand_edges

        # Alice get random picked edges from Bob
        # and sent to Bob Cv1 & Cv2
        rand_edge_from_bob = bob_rand_edges

        # Bob received Cv1 & Cv2
        Cv1 = rsa_var[rand_edge_from_bob[0]][3]
        Cv2 = rsa_var[rand_edge_from_bob[1]][3]
        # print Cv1, " | ", Cv2

        # Bob processing Zv1 & Zv2
        Zv1 = powd(ndz[rand_edge_from_bob[0]][2], Cv1, ndz[rand_edge_from_bob[0]][0])
        Zv2 = powd(ndz[rand_edge_from_bob[1]][2], Cv2, ndz[rand_edge_from_bob[1]][0])
        fcol = Zv1 & 3  # extract first three bits
        scol = Zv2 & 3  # extract first three bits

        if fcol == scol:
            print rand_edge_from_bob[0], ' ', rand_edge_from_bob[1]
            for key in R:
                print R[key] & 3
            print fcol
            print col_val_shuffle
            print "Alice obmanula Bob's"
            return

if __name__ == "__main__":
    # how many we needed generate graph
    variants = 1
    col_val = 0

    for i in range(variants):
        # If you want to generate random graph,
        # use flag False in first parameter in function CreateGraph
        G = CreateGraph(True, 30, 30)
        col_val = welsh_powell(G)
        index_max_color = max(col_val, key=col_val.get)  # Just use 'min' instead of 'max' for minimum.
        max_colors = col_val[index_max_color] + 1

        if max_colors > 3:
            print("Sorry, but graph could't be colored in 3 colors. " + "Needed ", col_val[index_max_color], " colors")
            continue
        else:
            mspa(col_val, max_colors)
            print("Oh yea, graph is could be colored in 3 colors")
    if variants == 1:
        DrawGraph(G, col_val)
        plt.show()
