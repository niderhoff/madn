import random
import operator


class Player:
    last_roll = None
    base = [1, 1, 1, 1]
    rolls = 0

    def __init__(self, id=None):
        if id is None:
            raise ValueError("no player id given")
        else:
            self.id = id

    def roll(self):
        roll = random.randint(1, 6)
        print(f"player {self.id} rolled a {roll}.")
        self.last_roll = roll
        self.rolls += 1
        return roll

    def move_out(self) -> bool:
        try:
            next_one = operator.indexOf(self.base, 1)
            self.base[next_one] = 0
            return True
        except ValueError:
            return False

    def move_back(self) -> bool:
        if sum(self.base) == 4:
            raise KeyError("Error starting area is already full.")
        else:
            next_one = operator.indexOf(self.base, 1)
            self.base[next_one - 1] = 1
            print(f"player {self.id}'s token is moved back to base.")
            return True


class Game:
    fields = [-1] * 40
    active_player = 0

    def print_field(self):
        for i in range(0, len(self.fields)):
            print(self.fields[i] if self.fields[i] != -1 else "O", end=" ")
            if i in [9, 19, 29, 39]:
                print("|", end="\n")
        print("\n")

    def move(self, player_id, fromidx, toidx):
        self.fields[fromidx] = -1
        old = self.fields[toidx]
        self.fields[toidx] = player_id
        print(f"player {player_id} moved a token from {fromidx} to {toidx}.")
        return old

    def automove(self, player: Player, rolled: int) -> bool:
        # reverse order so we try the best ones (closest to goal) first
        avail_tokens = reversed(
            [i for i, x in enumerate(self.fields) if x == player.id]
        )
        for idx in avail_tokens:
            # TODO: here insert check if we can go into the goal
            if self.fields[idx + rolled] != player.id:
                # field is empty or we can throw someone out
                thrown_out = self.move(player.id, idx, idx + rolled)
                print(f"player {player.id} is moving token {idx} to field {idx+rolled}")
                if thrown_out != -1:
                    print(
                        f"player {player.id} has thrown out a token of player {thrown_out}"
                    )
                    self.players[thrown_out].move_back()
                return True
            else:
                # try 2nd best token
                continue
        # no sucess yet? I guess nothing we can do.
        return False

    def has_moved_out(self, player: Player) -> bool:
        player_startfield = 10 * (player.id)
        # if our starting field is free, we try to move out
        if self.fields[player_startfield] == -1:
            print(f"{player_startfield} is free. moving out.")
            move_out = player.move_out()
            if move_out:
                self.fields[player_startfield] = player.id
            return move_out
        else:
            print(f"startfield occupied, cannot move out.")
            return False

    def __init__(self):
        pass

    def start(self):
        print("game started")
        self.print_field()
        self.players = [Player(id) for id in range(0, 4)]
        self.last_player = 0
        self.isrunning = True

    def turnlogic(self):
        print(f"player {self.active_player}'s move.")
        player = self.players[self.active_player]
        rolled = player.roll()
        # try to move out first
        if rolled == 6:
            print(f"player {self.active_player} trying to move out")
            moved = self.has_moved_out(player)
        else:
            moved = False
        # starting field was not free or we had no token in the start zone
        # try to move best existing token on the field instead
        if not moved:
            print(
                f"player {self.active_player} could not move out, trying to move existing token."
            )
            moved = self.automove(player, rolled)
        # cannot move or no token on the field
        # reroll, but we get punished for it
        if not moved and player.rolls <= 3:
            print(
                f"player {self.active_player} could not move existing token. re-roll."
            )
            print(f"player attemping reroll #{player.rolls}")
            player.rolls += 1
            self.turnlogic()
            # max rolls hit so we just end the turn here
            return
        if moved and rolled == 6:
            # since we have a 6 we are allowed a 2nd turn
            print(f"player {player.id} allowed another roll because they had a 6.")
            self.turnlogic()
        # unfortunately we couldn't do anything
        print(f"player {player.id} could not move.")
        return

    def turn(self):
        player = self.players[self.active_player]
        print(f"it's player {player.id}'s turn now.")
        self.turnlogic()
        # we are done, reset attempts
        player.rolls = 0
        # and move to next player
        if self.active_player < len(self.players) - 1:
            self.active_player += 1
        else:
            self.active_player = 0
        # and print the status
        self.print_field()


def main():
    game = Game()
    game.start()
    while game.isrunning:
        game.turn()
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
