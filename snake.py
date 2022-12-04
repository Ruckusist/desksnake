import random, time
from queue import PriorityQueue
from deskapp.server import Server, User


class SnakeUser(User):
    def __init__(self, username, password, session, AI=False):
        self.AI = AI
        self.highscore = 0
        self.snake = None
        super().__init__(username, password, session)


class Snake:
    """The actual Snake"""
    def __init__(self, head:tuple([int,int]), AI:bool=False) -> None:
        self.head = head
        self.max_length  = 4
        self.AI          = AI
        self.dead        = False
        self.filled      = [head]
        self.facing      = random.randint(0,3)
        self.bcs         = []

    def __getstate__(self): 
        return self.__dict__

    @property
    def score(self): 
        return len(self.filled)

    @property
    def length(self): 
        return len(self.filled)

    def check_tile(self, next_tile):
        b,c,s = self.bcs
        if (next_tile in b or
            next_tile[0] < 0 or next_tile[0] >= s[0] or
            next_tile[1] < 0 or next_tile[1] >= s[1]):
            return False
        return True

    def make_path(self, _from, _to):
        b,c,s = self.bcs
        start_coords = _from
        end_coords   = _to
        edge = PriorityQueue()
        edge.put((0, start_coords))
        came_from = dict()
        cost_so_far = dict()
        came_from[start_coords] = None
        cost_so_far[start_coords] = 0
        while not edge.empty():
            x, current = edge.get()
            # grid[current[0]][current[1]] = x  # cost_so_far[current]
            if current == end_coords:
                break
            for next in self.neighbors(current):
                new_cost = cost_so_far[current] +1  # RIGHT HERE!! ADVENT!
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                # if next not in came_from:
                    cost_so_far[next] = new_cost
                    # priority = new_cost
                    priority = self.heuristic(end_coords, next) + new_cost
                    edge.put((priority, next))
                    came_from[next] = current
        prev = came_from[end_coords]
        thepath = [end_coords, prev]
        while True:
            prev = came_from[prev]
            if prev:
                thepath.append(prev)
            else: break
        return thepath

    def neighbors(self, coords):
        UP    = (coords[0]+1, coords[1]  )
        DOWN  = (coords[0]-1, coords[1]  )
        LEFT  = (coords[0],   coords[1]-1)
        RIGHT = (coords[0],   coords[1]+1)
        newlist = []
        for coord in [UP, RIGHT, DOWN, LEFT]:
            if self.check_tile(coord): newlist.append(coord)
        return newlist

    def heuristic(self, start, fin):
        return abs(start[0] - fin[0]) + abs(start[1] - fin[1])

    def basic_move(self, b, c, s):
        self.bcs = (b,c,s)
        dirs = [self.facing]
        x = self.facing + 1
        if x >= 4: x=0
        dirs.append(x)
        x = self.facing - 1
        if x < 0: x=3
        dirs.append(x)

        good_moves = []
        great_moves = []
        # available = []
        for i in dirs:
            UP    = (self.head[0]+1, self.head[1]  )
            DOWN  = (self.head[0]-1, self.head[1]  )
            LEFT  = (self.head[0],   self.head[1]-1)
            RIGHT = (self.head[0],   self.head[1]+1)
            next_tile  = [UP, RIGHT, DOWN, LEFT][i]
            if (next_tile in b or
                next_tile[0] < 0 or next_tile[0] >= s[0] or
                next_tile[1] < 0 or next_tile[1] >= s[1]): 
                    # next tile is in set of bad tiles.
                    continue
            else:
                good_moves.append((i, next_tile))
                if next_tile in c:
                    great_moves.append((i, next_tile))

        # paths = []
        # the_next_path_move = None
        # if not great_moves:
        #     for cherry in c:
        #         try:
        #             path = self.make_path(self.head, cherry)
        #             paths.append((len(path), path))
        #         except Exception as e:
        #             print('here1')
        #             print(e)

        #     thepath = sorted(paths)[0]
        #     the_next_path_move = thepath[0]
        
        if good_moves:
            self.facing = random.choice([x[0] for x in good_moves])

            # if the_next_path_move in [x[1] for x in good_moves]:
            #     try:
            #         x = [x for x in good_moves if x[1]==the_next_path_move]
            #         self.facing = x[0][0]
            #     except Exception as e:
            #         print('here2')
            #         print(e)
        
        if great_moves:
            self.facing = random.choice([x[0] for x in great_moves])
    
    def move(self, blocked, cherries, map_size):
        """This is the AI"""
        # a 1/3 chance to move
        if random.choice([0,0,1]):
            # 1/2 chance to move left or right.
            self.facing += 1 if random.randint(0,1) else -1
            if self.facing >= 4: self.facing = 0
            if self.facing < 0: self.facing = 3


class Game:
    def __init__(self):
        self.server = Server(USER=SnakeUser)
        self.server.register_callback(self.callback)
        self.map_size = (15, 40)    # training size
        # self.map_size = (24, 21)  # google standard map size.
        # self.map_size = (28, 41)  # ruckus standard map size.

        # GAME STUFF
        self.map = [[0 for _ in range(self.map_size[1])] for _ in range(self.map_size[0])]
        self.players = {}
        self.cherries = []
        self.cherries_max = 5

        # LETS GO
        self.main()

    def callback(self, sess, message):
        username = sess.username
        if message.login:
            if message.logout:
                try:
                    del self.players[username]
                except: pass
                self.server.print(f"Removed {username} from the game")
            else:
                self.players[username] = Snake(self.get_empty())
                self.server.print(f"Added {username} to the game")
        if message.respawn:
            self.players[username] = Snake(self.get_empty())
        if message.dir_key:
            self.players[username].facing = message.dir_key

    def get_empty(self) -> tuple([int,int]):
        while True:
            x = random.randint(0,self.map_size[0]-1)
            y = random.randint(0,self.map_size[1]-1)
            if self.map[x][y] == 0:
                return (x,y)
  
    def advance(self):
        dead = []
        for playerName, snake in self.players.items():
            if snake.AI: snake.basic_move(self.blocked, self.cherries, self.map_size)

            UP    = (snake.head[0]+1, snake.head[1]  )
            DOWN  = (snake.head[0]-1, snake.head[1]  )
            LEFT  = (snake.head[0],   snake.head[1]-1)
            RIGHT = (snake.head[0],   snake.head[1]+1)
            next_tile  = [UP, RIGHT, DOWN, LEFT][snake.facing]

            if (next_tile in self.blocked or  # DEAD
                next_tile[0] < 0 or next_tile[0] >= self.map_size[0] or 
                next_tile[1] < 0 or next_tile[1] >= self.map_size[1]):
                dead.append(playerName)
                continue

            if next_tile in self.cherries:
                self.cherries.remove(next_tile)
                snake.max_length += 1

            snake.head = next_tile
            snake.filled.append(next_tile)
            if snake.length == snake.max_length:
                snake.filled.pop(0)

        for playerName in dead:
            snake = self.players[playerName]
            if snake.AI:
                self.players[playerName] = Snake(self.get_empty(), AI=snake.AI)
            else:
                del self.players[playerName]

    def cherry(self):
        if len(self.cherries) < self.cherries_max:
            x,y = self.get_empty()
            self.cherries.append((x,y))

    def update_map(self) -> list:
        _map = [[0 for _ in range(self.map_size[1])
                ] for _ in range(self.map_size[0])]
        all_blocked = []

        for idx, (_, snake) in enumerate(self.players.items()):
            for (x,y) in snake.filled: 
                _map[x][y] = idx+1
                all_blocked.append((x,y))

        for (x,y) in self.cherries:
            _map[x][y] = 99

        return all_blocked, _map

    def main(self):
        self.server.start()
        bots = ['Zeus', 'Killer', 'Backchannel', 
                'Paul', 'Mary', 'Frodo', 'Sam', 'Merry', 'Pippen']
        for bot in bots: self.players[bot] = Snake(self.get_empty(), AI=True)
        self.blocked, self.map = self.update_map()
        while True:
            try:
                self.cherry()
                self.advance()
                self.blocked, self.map = self.update_map()
                self.server.update_publish(
                    'snake', {
                        'map': self.map,
                        'players': [(x+1,y) for x,y in enumerate(list(self.players))],
                     }
                )
                time.sleep(.2)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
        self.server.end_safely()


def main():
    Game()

if __name__ == "__main__":
    main()