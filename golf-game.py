import random
import logging

class GolfGame:
    """
    Represents the main game logic for a console-based Golf card game.

    The game is played with a standard 52-card deck (without Jokers) for 2 to 4 players.
    The objective is to finish with the lowest possible score after a round.
    """

    def __init__(self, num_players: int = 2, players = None):
        """
        Initializes the game state.

        Args:
            num_players: The number of players in the game (2 to 4).
        """
        if not 2 <= num_players <= 4:
            raise ValueError("The game supports 2 to 4 players.")
        if players is not None and len(players) != num_players:
            raise ValueError(f"Expected {num_players} players, got {len(players)}.")
        elif players is None:
            self.players = [Player(f"Player {i+1}", self) for i in range(num_players)]
        else:
            for player in players:
                if not isinstance(player, Player):
                    raise TypeError("All players must be instances of the Player class.")
            for player in players:
                player.assign_to_game(self)

            self.players = players

        self.deck = self._create_shuffled_deck()
        self.discard_pile = []
        self.is_game_over = False

    def _create_shuffled_deck(self):
        """
        Creates a standard 52-card deck and shuffles it.

        Returns:
            A list representing the shuffled deck.
        """
        card_values = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
        suits = ['H', 'D', 'C', 'S']
        deck = [f"{value}-{suit}" for value in card_values for suit in suits]
        random.shuffle(deck)
        return deck

    def _deal_cards(self):
        """Deals four face-down cards to each player."""
        for player in self.players:
            player.hand = [self.deck.pop() for _ in range(4)]
            # Initially, all cards are face down.
            player.face_up_indices = set()

    def _get_card_value(self, card: str) -> int:
        """
        Calculates the score value of a single card.

        Args:
            card: A string representing the card (e.g., 'K-H').

        Returns:
            The integer score of the card.
        """
        value = card.split('-')[0]
        if value.isdigit():
            return int(value)
        elif value in ['J', 'Q', 'A']:
            return 10
        elif value == 'K':
            return 0
        else:
            return 0  # Should not happen

    def _calculate_score(self, player: 'Player') -> int:
        """
        Calculates the total score for a player's hand.

        Handles the rule where two of the same card cancel out.
        
        Args:
            player: The Player object whose hand is to be scored.

        Returns:
            The total integer score.
        """
        card_values = [card.split('-')[0] for card in player.hand]
        value_counts = {value: card_values.count(value) for value in set(card_values)}
        
        total_score = 0
        for value, count in value_counts.items():
            if count == 2:
                # Two of the same card cancel out to zero.
                continue
            elif count > 2:
                # If there are three or four of a kind, two cancel out.
                # The rest count for their value.
                remaining_cards = count % 2
                if remaining_cards > 0:
                    total_score += self._get_card_value(value + '-X') * remaining_cards
            else:
                total_score += self._get_card_value(value + '-X')

        return total_score

    def play_game(self):
        """Manages the main game loop until a player wins."""
        logging.debug("Welcome to Python Golf!")
        self._deal_cards()

        # Start the discard pile with one card.
        if not self.deck:
            logging.debug("Not enough cards to play.")
            return

        self.discard_pile.append(self.deck.pop())

        turn_count = 0
        while not self.is_game_over:
            turn_count += 1
            logging.debug(f"Round {turn_count}")

            for player in self.players:
                if self.is_game_over:
                    break

                self.is_game_over = player.make_move(self.deck, self.discard_pile)

        return self.end_game()

    def end_game(self):
        """
        Calculates and displays the final scores for all players.
        """
        final_scores = []
        for player in self.players:
            score = self._calculate_score(player)
            final_scores.append((player.name, score))
            logging.debug(f"{player.name}'s final hand: {player.hand}")
            logging.debug(f"{player.name}'s score: {score}")

        final_scores.sort(key=lambda x: x[1])

        return_scores = []
        logging.debug("\n--- Final Results ---")
        for rank, (name, score) in enumerate(final_scores):
            return_scores.append((name, score))
            logging.debug(f"#{rank+1}: {name} with a score of {score}")

        winner_name = final_scores[0][0]
        logging.debug(f"The winner is {winner_name} with the lowest score!")

        return return_scores

class Player:
    """
    Represents a generic player in the Golf card game.
    This class is intended to be a base class for specific player types.
    """
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.face_up_indices = set()
        
    def __repr__(self):
        return f"Player(name='{self.name}', hand={self.hand})"
    
    def assign_to_game(self, game: 'GolfGame'):
        """
        Assigns this player to a specific game instance.
        
        Args:
            game: The GolfGame instance to assign this player to.
        """
        self.game = game

    def _display_state(self, top_card: str):
        """Displays the player's current hand and the discard pile."""
        raise NotImplementedError("Subclass must implement abstract method _display_state")

    def make_move(self, deck: list, discard_pile: list) -> bool:
        """Handles the player's turn."""
        raise NotImplementedError("Subclass must implement abstract method make_move")

    def _choose_action(self):
        """Prompts the player to choose an action (e.g., draw, swap)."""
        raise NotImplementedError("Subclass must implement abstract method _choose_action")

    def _draw_or_take_card(self, action: str, deck: list, discard_pile: list):
        """Handles drawing a card from the deck or discard pile."""
        raise NotImplementedError("Subclass must implement abstract method _draw_or_take_card")

    def _choose_swap_or_discard(self, drawn_card: str):
        """Prompts the player to swap the drawn card or discard it."""
        raise NotImplementedError("Subclass must implement abstract method _choose_swap_or_discard")

    def _swap_card(self, drawn_card: str, face_down_indices: list, discard_pile: list):
        """Handles swapping a drawn card with one from the hand."""
        raise NotImplementedError("Subclass must implement abstract method _swap_card")

    def _turn_card_over(self, drawn_card: str, face_down_indices: list, discard_pile: list):
        """Handles turning over a face-down card."""
        raise NotImplementedError("Subclass must implement abstract method _turn_card_over")

class HumanPlayer(Player):
    """
    Represents a human player who interacts via the console.
    """
    def _display_state(self, top_card: str):
        hand_display = []
        for i in range(2):
            if i in self.face_up_indices:
                hand_display.append(f"{self.hand[i]} (up)")
            else:
                hand_display.append(f"{self.hand[i]} (down)")
        print(f"\n--- {self.name}'s Turn ---")
        print(f"Your Hand [0,1]: [{', '.join(hand_display)}]")
        print(f"Stack: {top_card.split('-')[0]}")

    def make_move(self, deck: list, discard_pile: list) -> bool:
        top_card = discard_pile[-1]
        self._display_state(top_card)
        face_down_indices = [i for i in range(4) if i not in self.face_up_indices]

        action = self._choose_action()
        drawn_card = self._draw_or_take_card(action, deck, discard_pile)

        swap_choice = self._choose_swap_or_discard(drawn_card)
        if swap_choice == 's':
            self._swap_card(drawn_card, face_down_indices, discard_pile)
        else:
            self._turn_card_over(drawn_card, face_down_indices, discard_pile)

        print("\n" * 50)
        return len(self.face_up_indices) == 4

    def _choose_action(self):
        action = None
        while action not in ['s', 't', 'd']:
            action = input("Do you want to (s)wap for the current card, "
                           "(d)raw a new one or (t)urn over one of your cards? ").lower()
        return action

    def _draw_or_take_card(self, action, deck, discard_pile):
        if action == 'd':
            if not deck:
                print("Deck is empty. Reshuffling discard pile.")
                deck[:] = discard_pile[:-1]
                random.shuffle(deck)
                discard_pile[:] = [discard_pile[-1]]
            drawn_card = deck.pop()
            print(f"You drew: {drawn_card.split('-')[0]}")
            return drawn_card
        elif action == 's':
            drawn_card = discard_pile.pop()
            print(f"You took from discard pile: {drawn_card.split('-')[0]}")
            return drawn_card
        else:
            return None

    def _choose_swap_or_discard(self, drawn_card):
        if drawn_card:
            swap_choice = input("Do you want to (s)wap with a card in your hand, or (d)iscard the drawn card? ").lower()
        else:
            swap_choice = 'd'
        return swap_choice

    def _swap_card(self, drawn_card, face_down_indices, discard_pile):
        if not face_down_indices:
            print("All your cards are already face up. You must discard.")
            discard_pile.append(drawn_card)
            return
        print("Your face-down card positions are:")
        for idx in face_down_indices:
            if idx < 2:
                print(f"{idx}: {self.hand[idx]}")
            else:
                print(f"{idx} : ???")
        swap_idx = -1
        while swap_idx not in face_down_indices:
            try:
                swap_idx = int(input("Enter the position (0-3) of the card you want to turn over and swap: "))
                if swap_idx not in range(4):
                    raise ValueError
                if swap_idx not in face_down_indices:
                    print("That card is already face up. Choose a face-down card.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter a valid card position.")
        discarded_card = self.hand[swap_idx]
        self.hand[swap_idx] = drawn_card
        discard_pile.append(discarded_card)
        self.face_up_indices.add(swap_idx)

    def _turn_card_over(self, drawn_card, face_down_indices, discard_pile):
        if not face_down_indices:
            print("All your cards are already face up. You can't turn another one up.")
            if drawn_card:
                discard_pile.append(drawn_card)
            return
        print("Your face-down card positions are:")
        for idx in face_down_indices:
            if idx < 2:
                print(f"{idx}: {self.hand[idx]}")
            else:
                print(f"{idx} : ???")
        swap_idx = -1
  
        while swap_idx not in face_down_indices:
            try:
                swap_idx = int(input("Enter the position (0-3) of the card you want to turn over: "))
                if swap_idx not in range(4):
                    raise ValueError
                if swap_idx not in face_down_indices:
                    print("That card is already face up. Choose a face-down card.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter a valid card position.")
  
        self.face_up_indices.add(swap_idx)
        if drawn_card:
            discard_pile.append(drawn_card)

class RandomPlayer(Player):
    """
    Represents a player that makes random decisions.
    This is useful for testing the game mechanics without human input.
    """
    def _display_state(self, top_card: str):
        logging.debug(f"\n--- {self.name}'s Turn ---")
        logging.debug(f"Your Hand: {self.hand}")
        logging.debug(f"Stack: {top_card.split('-')[0]}")

    def make_move(self, deck: list, discard_pile: list) -> bool:
        top_card = discard_pile[-1]
        self._display_state(top_card)
        face_down_indices = [i for i in range(4) if i not in self.face_up_indices]

        action = random.choice(['s', 'd', 't'])
        drawn_card = self._draw_or_take_card(action, deck, discard_pile)

        swap_choice = random.choice(['s', 'd'])
        if swap_choice == 's':
            self._swap_card(drawn_card, face_down_indices, discard_pile)
        else:
            self._turn_card_over(drawn_card, face_down_indices, discard_pile)

        return len(self.face_up_indices) == 4

    def _choose_action(self):
        return random.choice(['s', 'd', 't'])

    def _draw_or_take_card(self, action, deck, discard_pile):
        if action == 'd':
            if not deck:
                logging.debug("Deck is empty. Reshuffling discard pile.")
                deck[:] = discard_pile[:-1]
                random.shuffle(deck)
                discard_pile[:] = [discard_pile[-1]]
            drawn_card = deck.pop()
            logging.debug(f"{self.name} drew: {drawn_card.split('-')[0]}")
            return drawn_card
        elif action == 's':
            drawn_card = discard_pile.pop()
            logging.debug(f"{self.name} took from discard pile: {drawn_card.split('-')[0]}")
            return drawn_card
        else:
            return None

    def _choose_swap_or_discard(self, drawn_card):
        return random.choice(['s', 'd'])

    def _swap_card(self, drawn_card, face_down_indices, discard_pile):
        if not face_down_indices:
            logging.debug("All cards are face up. Discarding drawn card.")
            discard_pile.append(drawn_card)
            return
        if not drawn_card:
            return
        
        swap_idx = random.choice(face_down_indices)
        discarded_card = self.hand[swap_idx]
        self.hand[swap_idx] = drawn_card
        discard_pile.append(discarded_card)
        self.face_up_indices.add(swap_idx)

    def _turn_card_over(self, drawn_card, face_down_indices, discard_pile):
        if not face_down_indices:
            logging.debug("All cards are face up. Discarding drawn card.")
            if drawn_card:
                discard_pile.append(drawn_card)
            return
        
        swap_idx = random.choice(face_down_indices)
        self.face_up_indices.add(swap_idx)
        if drawn_card:
            discard_pile.append(drawn_card)
        logging.debug(f"{self.name} turned over card at position {swap_idx}.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)    
    scores = []
    for i in range(100000):
        players = [RandomPlayer("Alice"), RandomPlayer("Bob")]
        game = GolfGame(num_players=2, players=players)

        scores.append(game.play_game())
    
    alice_score = sum(score for pair in scores for player_name, score in pair if player_name == 'Alice') / len(scores)
    bob_score = sum(score for pair in scores for player_name, score in pair if player_name == 'Bob') / len(scores)
    
    logging.info(f"Average score for Alice: {alice_score}")
    logging.info(f"Average score for Bob: {bob_score}")
    logging.info("Game simulation complete.")