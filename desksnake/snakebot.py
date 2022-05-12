import time, threading


class SnakeBot:
    def __init__(self, username='Contra'):
        self.client = None
        self.username = username
        self.name = username
        self.start_coords = (0,0)
        
        self.head_coords = (0,0)
        self.filled = []
        self.heading = 0
        self.lives = 0
        self.high_score = 0
        self.score = 0
        
        
        self.grid = []
        
        self.max_messages = 9
        self.messages = []
        
    def start(self, client):
        self.client = client
        self.id = self.whoami()
        self.thread = threading.Thread(target=self.game_loop, daemon=True)
        self.thread.start()
        
    def add_message(self, value):
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self.messages.append(str(value))

    def whoami(self):
        self.client.send_message(snake=True, respawn=True)
        time.sleep(.5)
        for p in self.client.data['snake']['players_online']:
            if p[1] == self.username:
                return p[0]+1

    def get_score(self):
        for player_data in self.client.data['snake']['players_online']:
            if player_data[1] == self.username:
                self.score = player_data[2]
                # self.add_message(f"Current Score: {self.score}")
                break

    def amidead(self):
        grid = self.client.data['snake']['grid']
        for line in grid:
            if self.id in line:
                return False
        return True

    def movev2(self):
        self.add_message(f"Where am i? {self.head_coords}")
        if random.choice([0,1]):
            # 1/2 chance to move left or right.
            self.heading += 1 if random.randint(0,1) else -1
            if self.heading >= 5: self.heading = 1
            if self.heading < 1: self.heading = 4
            self.send_move(self.heading)
    
    def move(self):
        # self.add_message(f"Where am i? {self.head_coords}")
        # self.add_message(f"Finding the Cherries")
        cherries = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[1])):
                if self.grid[x][y] == '$':
                    cherries.append((x, y))
        self.add_message( f"Found {len(cherries)} Cherries @ {cherries}" )
        self.add_message( f"Whats the Nearest CHerry?" )
        for cherry in cherries:
            self.add_message(f"get from {self.head_coords} to {cherry}")
            break
  
    def send_move(self, direction):
        self.client.send_message(
                snake=True,
                dir_key=direction
            )

    def view(self):
        grid = self.client.data['snake']['grid']
        # return [''.join(x) for x in grid]
        new_grid = []
        for x, line in enumerate(grid):
            new_line = []
            for y, element in enumerate(line):
                # new_grid.append(''.join(line))
                if element > 0:
                    char = '#'
                    if element == 99:
                        char = '$'
                    elif element == self.id:
                        char = '%'
                        if x == self.head_coords[0] and y == self.head_coords[1]:
                            char = ['V', '>','^','<'][self.heading]
                            # char = '!'
                    
                    new_line.append(char)
                else:
                    new_line.append('.')
            new_grid.append(''.join(new_line))

        return new_grid

    def get_extra(self):
        extra_data = self.client.data['snake']['extra_data']
        for d in extra_data:
            if not d: continue
            if d[0] == self.id-1:
                self.head_coords = d[1]
                self.filled = d[2]
                self.heading = d[3] + 1

        if self.heading > 4:
            self.heading = 1
        else:
            self.heading -= 1

    def game_loop(self):
        self.get_score()
        self.get_extra()
        self.grid = self.view()
        while True:
            grid = self.view()
            if grid == self.grid:
                continue
            self.grid = grid
            self.get_score()
            self.get_extra()
            mesg = f"({self.head_coords}) | {len(self.filled)} | -> {['S','E','N','W'][self.heading]}"
            self.add_message(mesg)
            self.move()

            if self.amidead():
                self.lives += 1
                self.add_message(f"Cur Score: {self.score}. I've died {self.lives} times, respawning...")
                time.sleep(1)
                self.client.send_message(snake=True, respawn=True)

