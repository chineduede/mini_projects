#!/usr/bin/env python3
"""
Author: Ede Chinedu
Title: Blackjack
Description: The classic card game also known as 21. (Game has splitting
but no insurance.)
More info at: https://en.wikipedia.org/wiki/Blackjack
Tag: Game
"""

import random, sys, os
from dataclasses import dataclass
from typing import List, Optional

RULES = """
Blackjack, by Ede Chinedu
  Rules:
    -> Try to get as close to 21 without going over.
    -> Kings, Queens and Jacks are woth 10 points.
    -> Aces are worth 1 or 11 points.
    -> Cards 2 through 10 are worth their face value.
    -> In case of a tie, the bet is returned to the player.
    -> The dealer stops hitting at 17.
    
    Commands:
    -> (H)it to take another card.
    -> (S)tand to stop taking cards.
    -> (X)split to form two independent hands and bet exactly the same
        bet on initial hand. Available on first play if both cards are
        equal by rank.
    -> (D)ouble down to increase your bet but must hit exactly one
        more time before standing (available on first play).
	"""


@dataclass(repr=True)
class Suits:
    """A class representing the four types of suits of cards: spade,
    club, hearts, diamonds.
    
    :card_type -> The str representation of the card suite."""
    card_type: str
    

class Card:
    """Class representing a card"""

    def __init__(self, rank: int, suit: Suits, value: int) -> None:
        """Initializes the values of the card.
        
        :rank -> The number value of the card
        :suit -> The suit class: heats, spades, diamonds or clubs
        :value -> The number value the card represents"""

        self.rank = rank
        self.suit = suit
        self.value = value

    def get_string_repr(self) -> str:
        """Returns the string representation of a card."""
        r_ = str(self.rank)
        result = " ___ \n"
        result += f"|{r_.ljust(2)} |\n"
        result += f"| {self.suit} |\n"
        result += f"|_{r_.rjust(2, '_')}|"
        return result

    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit})"


def make_cards() -> list:
    """A function that makes a deck of cards, randomizes and returns it."""
    cards = []          #holds the deck of cards
    suits = [Suits(chr(9824)), Suits(chr(9827)), Suits(chr(9829)), Suits(chr(9830))]        #holds all suits
    for suit in suits:
        for rank in range(2, 11):       
            cards.append(Card(rank, suit.card_type, rank))      #appends appropriate cards to deck
        for rank in ('J', 'Q', 'K'):
            cards.append(Card(rank, suit.card_type, 10))
        cards.append(Card('A', suit.card_type, 1))
    
    random.shuffle(cards)     #randomize cards
    return cards

def roundup(x: int) -> int:
    """Roundup to the next hundred.
    
    :x -> number"""

    return x if x % 100 == 0 else x + 100 - x % 100


class Entity:
    """A base class from which the dealer class and player class inherit
    from. An entity could be a player or dealer."""
    
    def __init__(self, hand: List[Card], limit: int, name: str) -> None:
        """Initializes the class with necessary attributes.
        
        :hand -> The player/dealers hand, initialized with two cards.
        :limit -> Limit above which the entity cannot draw again
        :name -> name of player or "dealer" if entity is a dealer"""

        self.hand = hand        
        self.limit = limit      
        self.name = name        

    def get_hand_value(self) -> int:
        """Returns the value of the cards. Face cards are worth 10, aces are
	    worth 11 or 1 (this function picks the most suitable ace value)."""

        aces_count =  0        #initializes aces_count, used to determine if 10 will be added l8r.
        value = 0              #accumulative value to be returned
        for card in self.hand:
            # loop through each card in the given hand
            # access their value attributes and add to
            # accum. if card is an ace, 'A', increment
            # count.
            if card.rank == 'A':
                aces_count += 1
            value += card.value

        for _ in range(aces_count):
            #loop through the number of aces and 
            #if possible add 10 provided it doesn't
            # go over limit.
            if value + 10 <= self.limit:
                value += 10

        return value

    def show_all_cards(self, hide_first: bool = False) -> str:
        """Utility method used to print the entity's cards to
        the console.
        
        :hide_first -> If True, it shows the value of the first card,
            useful for hiding the dealer's card."""

        hidden_card = " ___ \n|## |\n|###|\n|_##|"      #used for dealer entity to hide card
        # Loop through entity's hand and split according
        # to newline. without that, cards would be printed
        # vertically instead of side-by-side.
        card_split = [ card.get_string_repr().split('\n') 
            for card in self.hand]
        #hide first card if dealer chooses it
        if hide_first: card_split[0] = hidden_card.split('\n')      

        all_cards_str = ''                      #accumulator for total str representation of the entity's hand
        # loop through the no of lines each
        # card string would take
        for i in range(len(card_split[0])):
            #loop through each card in hand
            for card in card_split:
                all_cards_str += card[i] + "  "         #add card line by line seperated by space.
            all_cards_str += '\n'
        return all_cards_str

class Dealer(Entity):
    """A Dealer class which inherits from Entity."""

    def __init__(self, hand: List[Card]) -> None:
        """Initializes necessary variables."""
        super().__init__(hand, limit=17, name = "Dealer")


class Player(Entity):
    """A player class which inherits from Entity."""
    def __init__(self, hand: List[Card], money: int, name: str) -> None:
        """Initializes necessary variables.
        
        :money -> The bet placed by the player"""
        super().__init__(hand, name=name, limit=21)
        self.money = money

    
class BlackJack:
    """A class representing a game of Blackjack."""

    def __init__(self, player_name: str) -> None:
        """Initializes necessary variable.
        
        :player_name -> For a friendlier interface."""
        self.start_amount = roundup(random.randint(1_000, 10_000) )               #randomized amount in $ to start the game
        self.deck = make_cards()                                         #initialize a new deck of cards
        self.player_name = player_name                             
        #Player object that stores player details
        self.player = Player([self.deck.pop(), self.deck.pop()], 0, self.player_name)   
        #Dealer object that stores dealer details
        self.dealer = Dealer([self.deck.pop(), self.deck.pop()])          

        # If player does decide to split his hand, stores second hand
        # Need to look for a better way to achieve this
        self.player_split = Player([], 0, player_name + " hand_two")
        self.split = False                                               #Flag to determine if a player does split.

    def player_or_split(self, entity: Entity) -> bool:
        """Checks if entity is original hand or a split
        hand.
        
        :entity -> The player or second hand."""
        return entity == self.player        

    def entity_hit(self, entity: Entity) -> None:
        """A function that picks a card ((H)its) for the desired
        entity.
        
        entity -> Player/second_hand/dealer."""

        # entity = self.player if self.player_or_split(entity) else self.player_split
        card = self.deck.pop()                  #remove card from top of deck
        print(f"{entity.name} chooses a card\n")
        print(f"{entity.name} draws {card.rank} of {card.suit}\n")
        entity.hand.append(card)                #adds card to entity's hand

        #prints the dealer/player total value of hand
        # and shows the dealer/player's cards.
        self.display_scores()
        # self.print_total(self.dealer)
        # print(self.dealer.show_all_cards(True))
        # self.print_total(entity)
        # print(entity.show_all_cards())



    def entity_bet(self, entity: Entity, amt: int) -> Optional[int]:
        """A function that asks the user to input an amount
        to bet and returns it or quits the game entirely.
        
        :entity -> Player/split_hand.
        :amt: -> The maximum amount allowed to bet."""

        # entity = self.player if self.player_or_split(entity) else self.player_split
        if not isinstance(entity, Player):      #checks if entity is dealer to avoid errors
            return
        while True:                             #loop until player enters a valid amount.
            try:
                print(f"Enter an amount from $1 - ${amt} or press (Q)uit.")
                money_to_bet = input('> ').strip().upper()
                if money_to_bet == 'Q':
                    print("Thanks for playing.")
                    print("..or maybe you can't actually play :)")
                    sys.exit()                  #exits game.

                money_to_bet = int(money_to_bet)
                if 1 <= money_to_bet <= amt:            
                    entity.money = money_to_bet         #money within reasonable range
                    return money_to_bet
                print("Amount not within range.\n")
            except ValueError:
                print("Enter a valid amount.\n")        #Ask again, invalid input

    def entity_stand(self, entity: Entity) -> None:
        """For consistency print's player 'stands down' to console."""
        print(f"{entity.name} chooses to stand down...")

    def entity_double_down(self, entity) -> None:
        """Called when a player chooses to (D)ouble down."""

        # entity = self.player if self.player_or_split(entity) else self.player_split
        print(f"\n{entity.name} chooses to double down...")
        new_bet = entity.money * 2                              
        print(f"{entity.name}'s bet has been increased by ${entity.money} to ${new_bet}.\n")
        entity.money = new_bet              #double the player's bet
        self.entity_hit(entity)             #player has to hit once after doubling down
        if entity.get_hand_value() > 21:
            return
        self.entity_stand(entity)           #player stands down

    def entity_split(self) -> None:
        """Called when a player decides to (X)split"""

        self.split = True                   #sets flag to show player decided to split.
        print(f"{self.player.name} decided to split...")
        card = self.player.hand.pop()               
        # removes one card from the player and adds it
        # to the split hand, also adds a new card to
        # both hands and adds the initial bet to the
        # second hand.
        # Split is only possible if the player can actually
        # double down.
        self.player_split.hand.extend([card, self.deck.pop()]) 
        self.player_split.money = self.player.money
        print(f"\n{self.player_split.name} has bet with ${self.player.money}")
        self.player.hand.append(self.deck.pop())
        print()

    def entity_possible_moves(self, entity: Entity) -> str:
        """A function that returns the players choice.
        The player can choose to (H)it, (S)tand, (X)split or (D)ouble down if available."""

        moves = ['(H)it', '(S)tand']        #moves always available

        # checks if player has enough money to bet
        # and if this is the player's first turn.
        # Also checks if cards have the same rank to
        # determine if player can split.
        # player can only split once.
        if len(entity.hand) == 2 and (self.start_amount - entity.money) \
            >= entity.money and (entity is self.player) and not self.split:
            moves.append('(D)ouble down')                       #player can double down
            if str(entity.hand[0].rank) == str(entity.hand[1].rank):    
                moves.append('(X)split')                        #player can split

        prompt = ', '.join(moves) + '> '
        while True:             #ask player until player returns a valid move.
            player_choice = input(prompt).strip().upper()
            if player_choice in ('H', 'S'):
                return player_choice
            if player_choice == 'D' and '(D)ouble down' in moves:
                return player_choice        #ensures (D)ouble down is possible
            if player_choice == 'X' and '(X)split' in moves:
                return player_choice        #ensures (X)split is possible
            print("Enter a valid choice.")   

    def print_total(self, entity: Entity, show_dealer_tot: bool = False) -> None:
        """A utility function that prints the dealer/player's total.
        
        :entity -> Player/Dealer/Player_spit.
        :show_dealer_tot -> Whether to show the dealer's total score or not.
        """

        if entity.name.lower() == "dealer":
            if not show_dealer_tot:
                print("Dealer hand total: ???")
            else:
                print("Dealer hand total: ", self.dealer.get_hand_value())
        else:
            print(f"{entity.name} hand total: ", entity.get_hand_value())

    def display_scores(self, flag_dealer: bool = False, show_dealer: bool = True,
        show_player_main: bool = True, show_player_split: bool = True) -> None:
        """A utility function to display player score and display
        the cards in each hand.
        
        :flag_dealer -> Determines if dealer shows all cards
            if True show scores and all cards face up.
        :show_one -> Display only player's main hand or second hand."""

        # print dealer's total and print hand
        if show_dealer:
            self.print_total(self.dealer, flag_dealer)
            print(self.dealer.show_all_cards(not flag_dealer))

        # print player's total and print hand
        if show_player_main:
            self.print_total(self.player)
            print(self.player.show_all_cards())

        # print player's split hand total and print hand
        # if it exists
        if show_player_split:
            self.print_total(self.player_split) if self.split == True else None
            print(self.player_split.show_all_cards()) if self.split == True else None

    def dealer_play(self) -> None:
        """Simulates the Dealer's play."""
        while self.dealer.get_hand_value() < 17:    #break if dealer goes above 17
            print("Dealer hits...")
            self.dealer.hand.append(self.deck.pop())    #dealer picks card

            # Display player scores
            self.display_scores()

            # If dealer goes above 21, dealer busts.
            if self.dealer.get_hand_value() > self.dealer.limit + 4:
                return
            input("Press Enter to continue...")
            print('\n')

    def entity_play(self, entity: Entity) -> None:
        """Simulates an entity's play.
        
        :entity -> Player or player's second hand."""
        # entity = self.player if self.player_or_split(entity) else self.player_split
        # check if player chose to (X)split
        # if not and entity is player_split
        # we return
        if not self.player_or_split(entity):
            if not self.split:
                return

        while True:                                         #loop until player busts or (S)tand
            if entity.get_hand_value() > entity.limit:      #player has burst
                return
            print(f"\n----{entity.name} pick a move---\n")
            move = self.entity_possible_moves(self.player)  #get all possible moves
            if move.upper() == "S":                        #player chooses to stand, exit func
                self.entity_stand(entity)
                return
            if move.upper() == 'D':                         #player chooses to (D)ouble down
                self.entity_double_down(entity)             #double down then (ST)tand
                return
            if move.upper() == 'H':                         #player chooses to (H)it
                self.entity_hit(entity)
            if move.upper() == 'X':                         #playeer chooses to (X)split
                self.entity_split()
                self.display_scores()
                if entity is self.player and \
                    self.player.get_hand_value() < self.player.limit:
                    continue
                return

    def check_if_dealer_plays(self) -> None:
        """Utility fuction to check if player has already
        bust. If player has burst, dealer does not need to play."""

        if self.player.get_hand_value() <= self.player.limit:              #player did not burst
            self.dealer_play()                                      
            return 
        # if player (S)plit, hand is less than limit
        # check dealer's hand. Useful because the 
        # player's main hand can go above limit but
        # player's second hand doesn't
        if self.split:                                                     #check if player_split exists                                   
            if self.player_split.get_hand_value() <= self.player_split.limit:
                self.dealer_play()
                return
        return

    def check_who_wins(self, entity: Entity) -> None:
        """A function used to determine which hand/entity won."""

        # Check if player's second hand exists,
        # because we call the function with both the 
        # player's main hand and the second hand, we need
        # to exit early if the player does not actually split.
        flag = self.player_or_split(entity)         #check if player or entiity

        if not self.player_or_split(entity):
            if not self.split:
                return                              #player did not split, exit

        # player and dealer's hand total
        entity_value = entity.get_hand_value()
        dealer_value = self.dealer.get_hand_value()

        # Display player scores
        self.display_scores(True, show_player_main=flag, show_player_split=not flag)

        if entity_value > entity.limit:
            print(f"\n{entity.name} goes bust")
            print(f"{entity.name} lost ${entity.money}!")
            self.start_amount -= entity.money                  
            return
        if dealer_value > 21:
            print(f"Dealer goes bust! {entity.name} wins ${entity.money}")
            self.start_amount += entity.money                  #add to player's total money
        elif entity_value < dealer_value:
            print(f"\nDealer's hand is {dealer_value}, {entity.name}'s hand is {entity_value}\n")
            print(f"{entity.name} lost ${entity.money}!")
            self.start_amount -= entity.money                  #subtract from player's total money
        elif entity_value > dealer_value:
            print(f"{entity.name} won ${entity.money}")
            self.start_amount += entity.money                  #add to player's total money
        elif entity_value == dealer_value:
            print("It's a tie, the bet is returned to you.")


    def reset(self) -> None:
        """Utitlity function that resets the deck of cards and bet
        if player decides to play again."""

        self.deck = make_cards()
        self.player = Player([self.deck.pop(), self.deck.pop()], 0, self.player_name)
        self.dealer = Dealer([self.deck.pop(), self.deck.pop()])
        self.player_split = Player([], 0, self.player_name + " hand_two")
        self.split = False


    def game(self) -> None:
        """Main function that controls the game."""
        print(RULES)                    
        print(f"You have been credited with ${self.start_amount}")

        # main game loop, loop infinitely until
        # player decides to quit or player looses
        # all his/her money
        while True:         
            if self.start_amount < 1:
                print("You've run out of money")
                print("Good thing you weren't using real money.")
                print("Try to seek professional help for your gambling problems.")
                sys.exit()          #player is broke, exit game 

            print(f"Money available: ${self.start_amount}")   

            # Get the amount player wants to stake.
            amt_to_bet = self.entity_bet(self.player, self.start_amount)
            print(f"Player bet ${amt_to_bet}")

            # Display player scores
            self.display_scores()

            # play for both player and player's second
            # hand if he does split
            self.entity_play(self.player)
            self.entity_play(self.player_split)

            # after player busts or (St)ands
            # check if dealer needs to play
            self.check_if_dealer_plays()

            # check which hand - player main or second hand
            # if existent- won.
            self.check_who_wins(self.player)
            self.check_who_wins(self.player_split)

            # start all over again
            input("Press Enter to continue...")
            print('\n')

            # reset stats.
            self.reset()
            # clear console
            os.system('cls') if sys.platform == "win32" else os.system('clear')


if __name__ == '__main__':
    blj = BlackJack("chinedu")
    blj.game()
