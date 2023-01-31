import random
import operator


class Player:
    def __init__(self, id=None):
        self.goal_zone = [0, 0, 0, 0]
        self.last_roll = None
        self.base = [1, 1, 1, 1]
        self.rolls = 0
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
            try:
                next_one = operator.indexOf(self.base, 1)
            except ValueError:
                # base is empty, so put the token in the back
                next_one = len(self.base)
            self.base[next_one - 1] = 1
            print(f"player {self.id}'s token is moved back to base.")
            return True


class Game:

    def print_field(self):
        for i, p in enumerate(self.players):
            print(f"[{i}]", end=" ")
            for j in p.base:
                print(f"{j}", end=" ")
            print("|", end=" ")
            for k in range(i, i + 10):
                field_value = self.fields[k] if self.fields[k] != -1 else "X"
                print(f"{field_value}", end=" ")
            print("|", end=" ")
            goal_player = i + 1 - 4 * int(i == 3)
            for m in self.players[goal_player].goal_zone:
                print(f"{m} ", end=" ")
            print("\n")
        print("\n")

    def move(self, player_id, fromidx, toidx):
        self.fields[fromidx] = -1
        old = self.fields[toidx]
        self.fields[toidx] = player_id
        print(f"player {player_id} moved a token from {fromidx} to {toidx}.")
        return old

    def check_finish(self, player: Player, avail_token: int, rolled: int) -> bool:
        id = player.id
        # get the index of the last field the player can possibly move to
        last_field_map = {0: 39, 1: 9, 2: 19, 3: 29}
        last_field_idx = last_field_map[id]
        # if the the move would move us out of the playing field, we can access
        # the goal zone
        overflow = avail_token + rolled - last_field_idx
        # we check if we can enter goal zone (overflow > 0)
        # but the goal zone is actually only 4 fields wide it must fit (<=4)
        if overflow > 0 and overflow <= 4:
            print(f"we have overflow! {overflow}")
            # hey we are moving off the board. let's check if it is a valid move
            # we have to -1 because it takes 1 move to actually get into the goal zone
            # from the last field and
            if player.goal_zone[overflow - 1] == 0:
                print(f"player {player.id} moved token {avail_token} into goalzone.")
                player.goal_zone[overflow - 1] = 1
                self.fields[avail_token] = -1
                return True
            else:
                print(
                    f"player {player.id} goalzone occupied by other token. this token cannot move out."
                )
                return False
        else:
            return False

    def moveup_goalzone(self, player: Player, rolled: int) -> bool:
        if rolled <= 4:
            for i in range(0, 4 - rolled):
                if player.goal_zone[i] == 1 and player.goal_zone[i + rolled] == 0:
                    print(
                        f"player {player.id} moving up token from {i} to {i+rolled} in goal zone."
                    )
                    player.goal_zone[i + rolled] = 1
                    player.goal_zone[i] = 0
                    return True
        return False

    def automove(self, player: Player, rolled: int) -> bool:
        # reverse order so we try the best ones (closest to goal) first
        avail_tokens = reversed(
            [i for i, x in enumerate(self.fields) if x == player.id]
        )
        for idx in avail_tokens:
            print(f"analyzing token {idx} for player {player.id}")
            # check if we can move any token to the goal zone and do it immediately
            if self.check_finish(player, idx, rolled):
                return True
            # continue with normal move of token, unless we are at the last field
            # but only if the field we want to move to is not occupied by *our own token*
            if idx + rolled < 40 and self.fields[idx + rolled] != player.id:
                # field is empty or we can throw someone out
                thrown_out = self.move(player.id, idx, idx + rolled)
                if thrown_out != -1:
                    print(
                        f"player {player.id} has thrown out a token of player {thrown_out}"
                    )
                    self.players[thrown_out].move_back()
                return True
            else:
                # try 2nd best token
                continue
        # try to clean up goal zone
        if self.moveup_goalzone(player, rolled):
            return True
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
            print("startfield occupied, cannot move out.")
            return False

    def __init__(self):
        # [0,9] = player 4 zone
        # [10,19] = player 3 zone
        # [20,29] = player 2 zone
        # [30, 39] = player 1 zone
        self.turns = 0
        self.fields = [-1] * 40
        self.active_player = 0

    def start(self):
        print("game started")
        self.players = [Player(id) for id in range(0, 4)]
        self.last_player = 0
        self.isrunning = True
        self.print_field()

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
        if moved:
            return
        else:
            print(
                f"player {self.active_player} could not move out, trying to move existing token."
            )
            moved = self.automove(player, rolled)
        if moved:
            return
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

    def check_win_condition(self):
        for i, p in enumerate(self.players):
            if sum(p.goal_zone) == 4:
                print(f"player {i} has won.")
                print(f"game finished after {self.turns} turns.")
                self.isrunning = False

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
        self.check_win_condition()
        self.turns += 1


def main():
    game = Game()
    game.start()
    while game.isrunning:
        game.turn()
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
