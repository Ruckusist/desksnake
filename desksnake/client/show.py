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

        # if not self.client.data.get('snake', False): return
        if not self.client.data['snake'].get('grid', False): return
        grid = self.client.data['snake']['grid']
        
        index = 4
        # panel.addstr(4, 4, f"This is working")  # ; self.index+= 1
        hardline = "#" * (len(grid)-1)
        panel.addstr(index, 4, f"{hardline}"); index+= 1
        for line in grid:
            l = ''.join(['*' if x == 99 else (str(x) if x else ' ') for x in line])
            panel.addstr(index, 4, f"#{l}#"); index+= 1
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