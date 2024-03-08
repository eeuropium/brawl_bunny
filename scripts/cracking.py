import math
import random
import time
from queue import Queue # for BFS
from scripts.managers import LimitTimer
from scripts.constants import *


# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class DSU:
    def __init__(self, n):
        self.p = [i for i in range(n)]
        self.sz = [1 for i in range(n)]

    def get(self, a):
        if self.p[a] == a:
            return a
        else:
            self.p[a] = self.get(self.p[a])
            return self.p[a]

    def same(self, a, b):
        return self.get(a) == self.get(b)

    def unite(self, a, b):
        if self.same(a, b):
            return

        a = self.get(a)
        b = self.get(b)

        if (self.sz[a] > self.sz[b]):
            a, b = b, a

        self.p[a] = b


def cartesian_to_polar(center_x, center_y, x, y):
    x -= center_x
    y -= center_y

    rho = math.sqrt(x**2 + y**2)
    phi = math.atan2(y, x)

    return phi, rho

def polar_to_cartesian(center_x, center_y, angle_degrees, distance):
    angle_radians = math.radians(angle_degrees)
    x = center_x + distance * math.cos(angle_radians)
    y = center_y + distance * math.sin(angle_radians)
    return int(x), int(y)

class Node():
    def __init__(self, type, arg1, arg2, index):
        if type == "polar":
            self.angle, self.radius = arg1, arg2
            self.x, self.y = polar_to_cartesian(0, 0, self.angle, self.radius)

        elif type == "cartesian":
            self.x, self.y = arg1, arg2
            self.angle, self.radius = cartesian_to_polar(0, 0, self.x, self.y)

        self.index = index
        self.pos = (self.x, self.y)

        self.adj = set()
        self.alive = True

    def dist(self, node):
        return (self.x - node.x) ** 2 + (self.y - node.y) ** 2

    def add_neighbour(self, node):
        self.adj.add(node)

    def get_scaled_pos(self, scale_factor):
        return polar_to_cartesian(0, 0, self.angle, self.radius * scale_factor)

def get_centroid(points):
    n = len(points)

    x_sum = 0
    y_sum = 0

    for point in points:
        x_sum += point[0]
        y_sum += point[1]

    return (x_sum // n, y_sum // n)

# for scaling all points
def g(x):
    return x ** (1/3)

# for ease towards centroid
def f(x):
    return x ** 3

def ease(point1, point2, t_value):
    x1, y1 = point1
    x2, y2 = point2

    return (x1 + f(t_value) * (x2 - x1), y1 + f(t_value) * (y2 - y1))



class Crack():
    def __init__(self):
        '''
        # org values
        RADIUS = 400
        POINTS_INSIDE = 100
        POINTS_CIRCUM = 20
        '''

        self.timer = LimitTimer(0.8)
        self.faces = []

        self.x, self.y = 0, 0


    # if clicked, start
    def start(self, x, y, orb_radius):
        if not self.timer.is_active():
            self.timer.start()

        self.faces = self.get_graph(orb_radius)

        self.x, self.y = x, y

    def get_graph(self, radius):
        # RADIUS = 100
        RADIUS = 25 * radius
        POINTS_INSIDE = 100
        POINTS_CIRCUM = 20

        TOTAL_POINTS = POINTS_CIRCUM + POINTS_INSIDE
        dsu = DSU(TOTAL_POINTS)

        tree_edges = []
        all_edges = []

        # random points inside circle
        # the - 0.25 * RADIUS ensures that the graph is planar (no intersections)
        nodes = [Node("polar", random.uniform(0, 360), random.uniform(0, RADIUS - 0.25 * RADIUS), i) for i in range(POINTS_INSIDE)]

        RANDOM_DEVIATION = 5

        # random points on circumference
        circum_angles = sorted([(i * 360 / POINTS_CIRCUM) + random.uniform(-RANDOM_DEVIATION, RANDOM_DEVIATION) for i in range(POINTS_CIRCUM)])
        circum_nodes = [Node("polar", circum_angles[i], RADIUS, i + POINTS_INSIDE) for i in range(POINTS_CIRCUM)]
        nodes.extend(circum_nodes)

        # pointer for sort of linked list approach of circum point
        left_pointer, right_pointer = {}, {}

        # join all points on circumference
        if POINTS_CIRCUM > 0:
            all_edges.append((circum_nodes[0], circum_nodes[-1]))

            left_pointer[circum_nodes[0].index] = circum_nodes[-1].index
            right_pointer[circum_nodes[-1].index] = circum_nodes[0].index


        for i in range(1, POINTS_CIRCUM):
            all_edges.append((circum_nodes[i], circum_nodes[i-1]))

            left_pointer[circum_nodes[i].index] = circum_nodes[i-1].index
            right_pointer[circum_nodes[i-1].index] = circum_nodes[i].index

        # construct tree_edges for inside points
        tree_edges = []

        for node1 in nodes:
            for node2 in nodes:
                if node1.index != node2.index:
                    tree_edges.append((node1.dist(node2), node1.index, node2.index))

        tree_edges.sort()

        # Kruskals algorithm
        for w, u, v in tree_edges:
            if not dsu.same(u, v):
                dsu.unite(u, v)
                all_edges.append((nodes[u], nodes[v]))

        # remove leaf nodes
        leaf_exist = True

        while leaf_exist:
            outdegree = [0 for i in range(TOTAL_POINTS)]

            leaf_exist = False

            for u, v in all_edges:
                if u.alive and v.alive:
                    outdegree[u.index] += 1
                    outdegree[v.index] += 1

            for node in nodes:
                if outdegree[node.index] == 1:
                    node.alive = False
                    leaf_exist = True

        new_all_edges = []

        for u, v in all_edges:
            if u.alive and v.alive:
                new_all_edges.append((u, v))
                u.add_neighbour(v)
                v.add_neighbour(u)

                # some edges in all_edges are constructed from both circum_points joining and minimum spanning tree,
                # but using a set in the add_neighbour eliminates this issue

        all_edges = new_all_edges
        faces = []

        for start_node in nodes:
            if len(start_node.adj) == 3 and start_node.radius == RADIUS and [node.radius for node in start_node.adj].count(RADIUS) == 2:

                for neighbour in start_node.adj:
                    if neighbour.radius != RADIUS:
                        start_neighbour = neighbour
                    # elif (neighbour.index == TOTAL_POINTS and neighbour.index < end_node.index) or (neighbour.index != TOTAL_POINTS  and neighbour.index > end_node.index):
                    #     end_node = neighbour

                end_node = nodes[right_pointer[start_node.index]]
                end_path = [end_node]

                # finding the correct end_node as some edge segments consist of more than 2 circum points
                while len(end_node.adj) != 3:
                    end_node = nodes[right_pointer[end_node.index]]
                    end_path.append(end_node)


                backtrack = [0 for i in range(TOTAL_POINTS)] # to trace back cycle path after BFS
                visited = [False for i in range(TOTAL_POINTS)]

                backtrack[start_neighbour.index] = start_node.index

                # BFS to find cycle
                queue = Queue()
                visited[start_node.index] = True
                queue.put(start_neighbour)

                while not queue.empty():
                    u = queue.get()

                    if u == end_node:
                        break

                    visited[u.index] = True

                    for v in u.adj:
                        if not visited[v.index] and (v == end_node or v.radius != RADIUS):
                            queue.put(v)
                            backtrack[v.index] = u.index

                # backtracking to get cycle path
                cycle_path = end_path
                current_node_index = end_node.index

                while current_node_index != start_node.index:
                    current_node_index = backtrack[current_node_index]
                    cycle_path.append(nodes[current_node_index])

                faces.append(cycle_path)
                # cycle_path does not have duplicate nodes eg: cycle path is represented as [1, 2, 3] instead of [1, 2, 3, 1]
        return faces

    def get_center(self):
        return (self.x, self.y)

    def get_faces(self):
        # for event in pygame.event.get():
        #     if event.type == pygame.MOUSEBUTTONDOWN:
        #         all_edges, faces = get_graph()
        #         animation_started = True
        #         start_time = time.time()
        # print(self.faces)

        if self.timer.is_active():
            scale_factor = g(self.timer.get_t_value())

            if scale_factor >= 1:
                self.timer.end()
                return []


            new_faces = []

            for j, face in enumerate(self.faces):

                org_polygon_points = [node.get_scaled_pos(scale_factor) for node in face]

                centroid_point = get_centroid(org_polygon_points)
                shrinked_polygon_points = [ease(point, centroid_point, scale_factor) for point in org_polygon_points]

                # change the origin of the points to the center of explosion
                # offset_points = [(x + self.x, y + self.y) for x, y in shrinked_polygon_points]

                # new_faces.append(offset_points)

                new_faces.append(shrinked_polygon_points) # center of explosion is (0, 0)

            return new_faces

        else:
            return []
