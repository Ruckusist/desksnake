import random
import deskapp


ClassID = random.random()
class Show(deskapp.Module):
    name = "Game"

    def __init__(self, app):
        super().__init__(app)
        self.classID = ClassID
        self.app = app
        self.client = app.data['client']['client']
        self.username = app.data['client']['username']
        self.score = 0
        self.index = 1

        self.client.add_sub('snake')

        # LAST THING!
        self.register_module()

    def page(self, panel):
        panel.addstr(self.index, 4, f"DeskSnakes!  -- {self.username} | score: {self.score}", self.frontend.chess_white)
        index = 3
        # if not self.client.data.get('snake', False): return
        if not self.client.data['snake'].get('grid', False): return
        grid = self.client.data['snake']['grid']
        players = self.client.data['snake']['players_online']
        # panel.addstr(index, 4, f"This is the players list: {players}"); index+= 1
        players_list = ['## Players Online ###']
        for player in players:
            player_id = player[0]
            player_name = player[1]
            player_score = player[2]
            if player_name == self.username:
                self.score = player_score
            players_list.append( f"{player_id+1}: {player_name} - {player_score}" )
        
        # panel.addstr(4, 4, f"This is working")  # ; self.index+= 1
        hardline = "#" * (len(grid[1])+2)
        panel.addstr(index, 4, f"{hardline}"); index+= 1
        for line_num in range(len(grid)):
            grid_line = grid[line_num]
            l = ''.join(['*' if x == 99 else (str(x)[-1] if x else ' ') for x in grid_line])
            game_map_line = f"#{l}#"
            
            if line_num in [x for x in range(len(players_list))]:
                player_line = players_list[line_num]
            else:
                player_line = " "*19

            print_line = f"{game_map_line} | {player_line}"
            panel.addstr(index, 4, print_line); index+= 1
        panel.addstr(index, 4, f"{hardline}"); index+= 2
        panel.addstr(index, 4, f"{self.context['text_output']}"); index+= 1
        panel.addstr(index, 4, f"This is a test"); index+= 1

    @deskapp.callback(ClassID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.client.send_message(snake=True, respawn=True)

    @deskapp.callback(ClassID, deskapp.Keys.W)
    def on_W(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=3
        )

    @deskapp.callback(ClassID, deskapp.Keys.A)
    def on_A(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=4
        )

    @deskapp.callback(ClassID, deskapp.Keys.S)
    def on_S(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=1
        )

    @deskapp.callback(ClassID, deskapp.Keys.D)
    def on_D(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=2
        )