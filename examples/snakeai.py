from desksnake import client, SnakeBot



class NewBot(SnakeBot):
    def __init__(self):
        super().__init__("Nemesis")
        
        
    def move(self):
        self.add_message("Im moving!")
        
        
client.main(bots=[NewBot])