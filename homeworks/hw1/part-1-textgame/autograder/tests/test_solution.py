import unittest
from gradescope_utils.autograder_utils.decorators import weight, visibility, tags
import action_castle as X
from action_castle import game as G
from text_adventure_games import games, things, actions, blocks

class ActionCastle(games.Game):
    def __init__(
        self, start_at: things.Location, player: things.Character, characters=None,
        custom_actions=None
    ):
        super().__init__(start_at, player, characters=characters, custom_actions=custom_actions)

    def is_won(self) -> bool:
        """ 
        Checks whether the game has been won. For Action Castle, the game is won
        once any character is sitting on the throne (has the property is_reigning).
        """
        for name, character in self.characters.items():
            if character.get_property("is_reigning"):
                msg = "{name} is now reigns in ACTION CASTLE! {name} has won the game!"
                self.parser.ok(msg.format(name=character.name.title()), self)
                return True
        return False
# Actions
class Unlock_Door(actions.Action):
    ACTION_NAME = "unlock door"
    ACTION_DESCRIPTION = "Unlock a door with a key"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.key = self.parser.match_item(
            "key", self.parser.get_items_in_scope(self.character)
        )
        self.door = self.parser.match_item(
            "door", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a door
        * The character must be at the same location as the door
        * The door must be locked
        * There must be a door
        * The character must have the key in their inventory
        """
        if not self.was_matched(self.door, "There's no door here."):
            return False
        if not self.loc_has_item(self.character.location, self.door):
            return False
        if not self.has_property(self.door, "is_locked", "The door is not locked."):
            return False
        if not self.was_matched(
            self.key, "{name} does not have the key.".format(name=self.character.name)
        ):
            return False
        if not self.is_in_inventory(self.character, self.key):
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * Unlocks the door
        """
        self.door.set_property("is_locked", False)
        description = "{character_name} unlocked the door".format(
            character_name=self.character.name
        )
        self.parser.ok(description)


class Read_Runes(actions.Action):
    """
    Reading the runes on the candle with strange runes on it will banish the
    ghost from the dungeon, and cause it to drop the crown.
    """

    ACTION_NAME = "read runes"
    ACTION_DESCRIPTION = "Read runes off of the candle"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.candle = self.parser.match_item(
            "candle", self.parser.get_items_in_scope(self.character)
        )
        self.ghost = self.parser.get_character("ghost")

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a candle with strange runes on it
        * The character must have the candle in their inventory
        * the ghost must be in this location
        * The candle must be lit
        """
        if not self.was_matched(self.candle, "You don't see runes on anything here."):
            return False
        if not self.is_in_inventory(self.character, self.candle):
            return False
        if not self.was_matched(
            self.ghost,
            "The runes seem be a banishment spell, but there is nothing to banish here.",
        ):
            return False
        if not self.at(
            self.ghost,
            self.character.location,
            "The runes seem be a banishment spell, but there is nothing to banish here.",
        ):
            return False
        if not self.has_property(
            self.candle,
            "is_lit",
            "Nothing happens. Perhaps if you light the candle first?",
        ):
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * Banishes the ghost, causing it to drop its inventory.
        """
        description = "{character_name} holds aloft the glowing candle cofered in strange runes. ".format(
            character_name=self.character.name.capitalize()
        )
        description += "The odd runes are an exorcism ritual to dispel evil spirits."
        self.parser.ok(description)

        # the ghost drops its inventory
        items = list(self.ghost.inventory.keys())
        for item_name in items:
            item = self.ghost.inventory[item_name]
            command = f"{self.ghost.name} drops {item.name}"
            drop = actions.Drop(self.game, command)
            if drop.check_preconditions():
                drop.apply_effects()

        # the ghost is banished
        self.ghost.set_property("is_banished", True)
        description = "{ghost} is banished".format(ghost=self.ghost.name)
        self.parser.ok(description)
        # remove the ghost from the scene
        self.ghost.location.remove_character(self.ghost)


class Propose(actions.Action):
    """
    Mawwige is whut bwings us togevveh today.
    """

    ACTION_NAME = "propose marriage"
    ACTION_DESCRIPTION = "Propose marriage to someone"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        keyword = "propose marriage"
        (before_keyword, after_keyword) = self.parser.split_command(command, keyword)
        self.proposer = self.parser.get_character(before_keyword)
        self.propositioned = self.parser.get_character(after_keyword)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The two characters must be in the same place
        * Neither can be married yet
        * Both must be happy
        """
        if not self.was_matched(self.proposer, "They aren't here."):
            return False
        if not self.was_matched(self.propositioned, "They aren't here."):
            return False
        if not self.at(
            self.propositioned,
            self.proposer.location,
            "{name_1} and {name_2} aren't in the same location.".format(
                name_1=self.propositioned.name, name_2=self.proposer.name
            ),
        ):
            return False
        if not self.property_equals(self.proposer, "emotional_state", "happy"):
            return False
        if not self.property_equals(self.propositioned, "emotional_state", "happy"):
            return False
        if self.has_property(
            self.proposer,
            "is_married",
            "{name} is already married".format(name=self.proposer.name),
            display_message_upon=True,
        ):
            return False
        if self.has_property(
            self.propositioned,
            "is_married",
            "{name} is already married".format(name=self.propositioned.name),
            display_message_upon=True,
        ):
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * They said "Yes!"
        * They are married.
        * If one is a royal, they are now both royals
        """
        description = "{name} says YES!".format(
            name=self.propositioned.name.capitalize()
        )
        self.parser.ok(description)
        self.proposer.set_property("is_married", True)
        self.propositioned.set_property("is_married", True)
        description = "{name_1} and {name_2} are now married.".format(
            name_1=self.propositioned.name, name_2=self.proposer.name
        )
        self.parser.ok(description)
        if self.proposer.get_property("is_royal") or self.propositioned.get_property(
            "is_royal"
        ):
            self.proposer.set_property("is_royal", True)
            self.propositioned.set_property("is_royal", True)


class Wear_Crown(actions.Action):
    ACTION_NAME = "wear crown"
    ACTION_DESCRIPTION = "Put a crown in your inventory atop your head"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.crown = self.parser.match_item(
            "crown", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The crown must be in the character's inventory
        * The the character must be a royal
        """
        if not self.was_matched(self.crown, "I don't see it."):
            return False
        if not self.is_in_inventory(self.character, self.crown):
            return False
        if not self.has_property(
            self.character, "is_royal", "Only a royal may wear the crown."
        ):
            return False
        return True

    def apply_effects(self):
        """
        The character is crowned.
        """

        description = "{character_name} has been crowned as the monarch.  They may now take their rightful seat on the throne.".format(
            character_name=self.character.name.capitalize()
        )
        self.parser.ok(description)
        self.character.set_property("is_crowned", True)


class Sit_On_Throne(actions.Action):
    ACTION_NAME = "sit on throne"
    ACTION_DESCRIPTION = "Sit on the throne, if you are the crowned monarch."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.throne = self.parser.match_item(
            "throne", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The character must be in same location as the throne
        * The the character must be crowned
        """
        if not self.was_matched(self.character, "The character wasn't matched."):
            return False
        if not self.was_matched(self.throne, "The throne couldn't be found."):
            return False
        if not self.at(self.throne, self.character.location, "The throne isn't here."):
            return False
        if not self.has_property(
            self.character,
            "is_crowned",
            "Only the crowned monarch may sit upon the throne",
        ):
            return False
        return True

    def apply_effects(self):
        """
        The character who sits on the throne is reigning.
        """
        self.character.set_property("is_reigning", True)
        description = (
            "{name} now sits upon the throne. The reign of {name} has begun!".format(
                name=self.character.name.title()
            )
        )
        self.parser.ok(description)


# Blocks
class Troll_Block(blocks.Block):
    """
    Blocks progress in this direction until the troll is no longer hungry, or
    leaves, or is unconscious, or dead.
    """

    def __init__(self, location: things.Location, troll: things.Character):
        super().__init__("A troll blocks your way", "A hungry troll blocks your way")
        self.location = location
        self.troll = troll

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * There is a troll here
        # * The troll is alive and conscious
        # * The troll is still hungry
        if self.troll:
            if not self.location.here(self.troll):
                return False
            if self.troll.get_property("is_dead"):
                return False
            if self.troll.get_property("is_unconscious"):
                return False
            if self.troll.get_property("is_hungry"):
                return True
        return False


class Guard_Block(blocks.Block):
    """
    Blocks progress in this direction until the guard is no longer suspicious, or
    leaves, or is unconscious, or dead.
    """

    def __init__(self, location: things.Location, guard: things.Character):
        super().__init__(
            "A guard blocks your way", "The guard refuses to let you pass."
        )
        self.guard = guard
        self.location = location

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * There is a guard here
        # * The guard is alive and conscious
        # * The guard is suspicious

        if self.guard:
            if not self.location.here(self.guard):
                return False
            if self.guard.get_property("is_dead"):
                return False
            if self.guard.get_property("is_unconscious"):
                return False
            if self.guard.get_property("is_suspicious"):
                return True
        return False


class Darkness(blocks.Block):
    """
    Blocks progress in this direction unless the character has something that lights the way.
    """

    def __init__(self, location: things.Location, skeleton=False):
        super().__init__("Darkness blocks your way", "It's too dark to go that way.")
        self.location = location
        self.location.set_property("is_dark", True)

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * The location is dark
        # * Unblocked if any character at the location is carrying a lit item (like a lamp or candle)

        if not self.location.get_property("is_dark"):
            return False
        for character_name in self.location.characters:
            character = self.location.characters[character_name]
            for item_name in character.inventory:
                item = character.inventory[item_name]
                if item.get_property("is_lit"):
                    return False
        return True

class Door_Block(blocks.Block):
    """
    Blocks progress in this direction until the character unlocks the door.
    """

    def __init__(self, location: things.Location, door: things.Item):
        super().__init__("A locked door blocks your way", "The door ahead is locked.")
        self.door = door
        self.location = location

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * The door is locked
        if self.door:
            if not self.location.here(self.door):
                return False
            if self.door.get_property("is_locked"):
                return True
        return False

def build_game():
    cottage = things.Location(
        "Cottage",
        "You are standing in a small cottage."
    )
    garden_path = things.Location(
        "Garden Path",
        "You are standing on a lush garden path. There is a cottage here.",
    )
    fishing_pond = things.Location(
        "Fishing Pond",
        "You are at the edge of a small fishing pond."
    )
    winding_path = things.Location(
        "Winding Path",
        "You are walking along a winding path. There is a tall tree here.",
    )
    top_of_tree = things.Location(
        "Top of the Tall Tree",
        "You are the top of the tall tree."
    )
    drawbridge = things.Location(
        "Drawbridge",
        "You are standing on one side of a drawbridge leading to ACTION CASTLE.",
    )
    courtyard = things.Location(
        "Courtyard",
        "You are in the courtyard of ACTION CASTLE."
    )
    tower_stairs = things.Location(
        "Tower Stairs",
        "You are climbing the stairs to the tower. There is a locked door here.",
    )
    tower = things.Location(
        "Tower",
        "You are inside a tower."
    )
    dungeon_stairs = things.Location(
        "Dungeon Stairs",
        "You are climbing the stairs down to the dungeon."
    )
    dungeon = things.Location(
        "Dungeon",
        "You are in the dungeon. There is a spooky ghost here."
    )
    feasting_hall = things.Location(
        "Great Feasting Hall",
        "You stand inside the Great Feasting Hall."
    )
    throne_room = things.Location(
        "Throne Room",
        "This is the throne room of ACTION CASTLE."
    )
    death = things.Location(
        "The Afterlife",
        "You are dead. GAME OVER."
    )
    death.set_property("game_over", True)


    # Map of Locations
    cottage.add_connection("out", garden_path)
    garden_path.add_connection("south", fishing_pond)
    garden_path.add_connection("north", winding_path)
    winding_path.add_connection("up", top_of_tree)
    winding_path.add_connection("east", drawbridge)
    top_of_tree.add_connection("jump", death)
    drawbridge.add_connection("east", courtyard)
    courtyard.add_connection("up", tower_stairs)
    courtyard.add_connection("down", dungeon_stairs)
    courtyard.add_connection("east", feasting_hall)
    tower_stairs.add_connection("up", tower)
    dungeon_stairs.add_connection("down", dungeon)
    feasting_hall.add_connection("east", throne_room)

    # Put a fishing pole at the cottage
    fishing_pole = things.Item(
        "pole",
        "a fishing pole",
        "A SIMPLE FISHING POLE.",
    )
    cottage.add_item(fishing_pole)


    # Put a branch in a tree that could be used as a weapon
    branch = things.Item(
        "branch",
        "a stout, dead branch",
        "IT LOOKS LIKE IT WOULD MAKE A GOOD CLUB.",
    )
    branch.set_property("is_weapon", True)
    branch.set_property("is_fragile", True)
    top_of_tree.add_item(branch)


    # Put a candle in the feasting hall
    candle = things.Item(
        "candle",
        "a strange candle",
        "THE CANDLE IS COVERED IN STARGE RUNES.",
    )
    candle.set_property("is_lightable", True)
    candle.set_property("is_lit", False)
    candle.add_command_hint("light candle")
    candle.add_command_hint("read runes")
    feasting_hall.add_item(candle)
    # Put an actual pond at the fishing location
    pond = things.Item(
        "pond",
        "a small fishing pond",
        "THERE ARE FISH IN THE POND.",
    )
    pond.set_property("gettable", False)
    pond.set_property("has_fish", True)
    pond.add_command_hint("catch fish")
    pond.add_command_hint("catch fish with pole")
    fishing_pond.add_item(pond)


    # A nice rosebush for the garden path
    rosebush = things.Item(
        "rosebush",
        "a rosebush",
        "THE ROSEBUSH CONTAINS A SINGLE RED ROSE.  IT IS BEAUTIFUL.",
    )
    rosebush.set_property("gettable", False)
    rosebush.set_property("has_rose", True)
    rosebush.add_command_hint("pick rose")
    garden_path.add_item(rosebush)


    # Throne room wouldn't be that impressive without a throne
    throne = things.Item(
        "throne",
        "An ornate golden throne."
    )
    throne.set_property("gettable", False)
    throne.add_command_hint("sit on throne")
    throne_room.add_item(throne)


    # A door that leads to the tower stairs
    door = things.Item(
        "door",
        "a door",
        "THE DOOR IS SECURELY LOCKED."
    )
    door.set_property("gettable", False)
    door.set_property("is_locked", True)
    door.add_command_hint("unlock door")
    tower_stairs.add_item(door)

    # Player
    player = things.Character(
        name="The player",
        description="You are a simple peasant destined for greatness.",
        persona="I am on an adventure.",
    )

    # Player's lamp
    lamp = things.Item("lamp", "a lamp", "A LAMself.")
    lamp.set_property("is_lightable", True)
    lamp.set_property("is_lit", False)
    lamp.add_command_hint("light lamp")
    player.add_to_inventory(lamp)

    # A Troll at the drawbridge
    troll = things.Character(
        name="troll",
        description="A mean troll",
        persona="I am hungry. The guard promised to feed me if I guard the drawbridge and keep people out of the castle.",
    )
    troll.set_property("is_hungry", True)
    troll.set_property("character_type", "troll")
    drawbridge.add_character(troll)


    # A guard in the courtyard
    guard = things.Character(
        name="guard",
        description="A castle guard",
        persona="I am suspicious of anyone trying to enter the castle. I will prevent keep people from entering and learning the castle's dark secrets.",
    )
    guard.set_property("is_conscious", True)
    guard.set_property("is_suspicious", True)
    guard.set_property("character_type", "human")
    courtyard.add_character(guard)

    # Guard has a key
    key = things.Item("key", "a brass key", "THIS LOOKS USEFUL")
    guard.add_to_inventory(key)

    # Guard has a sword
    sword = things.Item("sword", "a short sword", "A SHARP SHORT SWORD.")
    sword.set_property("is_weapon", True)
    guard.add_to_inventory(sword)


    # A Princess in the tower
    princess = things.Character(
        name="princess",
        description="A princess who is beautiful and lonely. She awaits her non-gender-stereotypical soulmate.",
        persona="I am the princess. I am grieving my father's death. I feel alone.",
    )
    princess.set_property("is_royal", True)
    princess.set_property("emotional_state", "sad and lonely")
    princess.set_property("is_married", False)
    princess.set_property("character_type", "human")
    tower.add_character(princess)


    # A ghost in the dungeon
    ghost = things.Character(
        name="ghost",
        description="A ghost with bony, claw-like fingers and who is wearing a crown.",
        persona="I was murdered by the guard. I will haunt this castle until banished. If you linger before my apparition, I will plunge my ghostly hand inside you and stop your heart",
    )
    ghost.set_property("character_type", "ghost")
    ghost.set_property("is_dead", True)
    ghost.set_property("is_banished", False)
    dungeon.add_character(ghost)

    # Ghost's crown
    crown = things.Item("crown", "a crown", "A CROWN FIT FOR A KING.")
    crown.add_command_hint("wear crown")
    ghost.add_to_inventory(crown)

    # Solution

    troll_block = Troll_Block(drawbridge, troll)
    drawbridge.add_block("east", troll_block)
    guard_block = Guard_Block(courtyard, guard)
    courtyard.add_block("east", guard_block)
    darkness_block = Darkness(dungeon_stairs)
    dungeon_stairs.add_block("down", darkness_block)
    locked_door_block = Door_Block(tower_stairs, door)
    tower_stairs.add_block("up", locked_door_block)
    
    characters = [troll, guard, princess, ghost]
    custom_actions = [Unlock_Door, Read_Runes, Propose, Wear_Crown, Sit_On_Throne]

    # The Game
    game = ActionCastle(cottage, player, characters=characters, custom_actions=custom_actions)
    return game


class TestSolution(unittest.TestCase):

############################################################
# Section 1: Actions
############################################################

# Section 1.1: Unlock_Door

    # @weight(1)
    # def test_unlock_door_init(self):
    #     game = build_game()
    #     a = X.Unlock_Door(game, "unlock door")
    #     self.assertEqual(a.character is None, False, "self.character is not assigned")
    #     self.assertEqual(a.door is None, True, "self.door is not None when door is not in scope")
    #     self.assertEqual(a.key is None, True, "self.key is not None when key is not in scope")
    #     before_unlock = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up"
    #     game.parser.parse_command(before_unlock)
    #     a = X.Unlock_Door(game, "unlock door")
    #     self.assertEqual(a.door is None, False, "self.door is None when door is in scope")
    #     self.assertEqual(a.key is None, False, "self.key is None when key is in scope")


    @weight(1)
    def test_unlock_door_check_preconditions(self):
        game = build_game()
        a = X.Unlock_Door(game, "unlock door")
        self.assertEqual(a.check_preconditions(), False, "If there is no door here, it should return False")

        before_unlock = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up"
        game.parser.parse_command(before_unlock)
        a = X.Unlock_Door(game, "unlock door")
        self.assertEqual(a.check_preconditions(), True, "All preconditions are met, it should return True")

        game.parser.parse_command("unlock door")
        a = X.Unlock_Door(game, "unlock door")
        self.assertEqual(a.check_preconditions(), False, "The door is already unlocked, it should return False")
    
        game = build_game()
        no_key = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up"
        game.parser.parse_command(no_key)
        a = X.Unlock_Door(game, "unlock door")
        self.assertEqual(a.check_preconditions(), False, "The player doesn't have the key, it should return False")


    @weight(1)
    def test_unlock_door_apply_effects(self):
        game = build_game()
        before_unlock = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up"
        game.parser.parse_command(before_unlock)
        a = X.Unlock_Door(game, "unlock door")
        self.assertEqual(a.door.get_property("is_locked"), True, "Be sure to set the door's is_locked property to be True at the start of the game")

        X.Unlock_Door(game, "unlock door").apply_effects()
        a = X.Unlock_Door(game, "unlock door")
        self.assertEqual(a.door.get_property("is_locked"), False, "Be sure to set the door's is_locked property to be False after unlocking the door")


# Section 1.2: Read_Runes
        
    # @weight(1)
    # def test_read_runes_init(self):
    #     game = build_game()
    #     a = X.Read_Runes(game, "read runes")
    #     self.assertEqual(a.character is None, False, "self.character is not assigned")
    #     self.assertEqual(a.candle is None, True, "self.candle is not None when candle is not in scope")
    #     self.assertEqual(a.ghost is None, False, "self.ghost is not assigned")

    #     before_read = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle"
    #     game.parser.parse_command(before_read)
    #     a = X.Read_Runes(game, "read runes")
    #     self.assertEqual(a.candle is None, False)
    #     self.assertEqual(a.ghost is None, False)


    @weight(1)
    def test_read_runes_check_preconditions(self):
        game = build_game()
        a = X.Read_Runes(game, "read runes")
        self.assertEqual(a.check_preconditions(), False, "If there is no candle/ghost here, it should return False")

        not_lit = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down"
        game.parser.parse_command(not_lit)
        a = X.Read_Runes(game, "read runes")
        self.assertEqual(a.check_preconditions(), False, "If candle is not lit, it should return False")

        game.parser.parse_command("light candle")
        a = X.Read_Runes(game, "read runes")
        self.assertEqual(a.check_preconditions(), True, "All preconditions are met, it should return True")

        # game.parser.parse_command("read runes")
        # a = X.Read_Runes(game, "read runes")
        # self.assertEqual(a.check_preconditions(), False, "return True when the player has already read the runes")
   
        game = build_game()
        no_candle = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, go west, go down, light lamp, go down"
        game.parser.parse_command(no_candle)
        a = X.Read_Runes(game, "read runes")
        self.assertEqual(a.check_preconditions(), False, "If the player doesn't have the candle, it should return False")


    @weight(1)
    def test_read_runes_apply_effects(self):
        game = build_game()
        before_read = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle"
        game.parser.parse_command(before_read)
        a = X.Read_Runes(game, "read runes")
        self.assertEqual("crown" in a.character.location.items, False, "There shouldn't be a crown here before reading runes")

        X.Read_Runes(game, "read runes").apply_effects()
        a = X.Read_Runes(game, "read runes")
        self.assertEqual("crown" in a.character.location.items, True, "The crown should be dropped here after reading runes")

# Section 1.3: Propose
        
    # @weight(1)
    # def test_propose_init(self):
    #     game = build_game()
    #     a = X.Propose(game, "")
    #     self.assertEqual(a.proposer is None, False)
    #     self.assertEqual(a.propositioned is None, False)
    #     self.assertEqual(a.proposer.name == "The player", True)
    #     self.assertEqual(a.propositioned.name == "princess", False)
    #     a = X.Propose(game, "propose to the princess")
    #     self.assertEqual(a.proposer.name == "The player", True)
    #     self.assertEqual(a.propositioned.name == "princess", True)


    @weight(1)
    def test_propose_check_preconditions(self):
        game = build_game()
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.check_preconditions(), False, "The player cannot propose when the princess is not here")

        didnt_smell_rose = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess"
        game.parser.parse_command(didnt_smell_rose)
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.check_preconditions(), False, "If the player has not smell the rose, then the player is not happy and should not be able to propose")

        game = build_game()
        didnt_give_rose = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up"
        game.parser.parse_command(didnt_give_rose)
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.check_preconditions(), False, "If the princess has not received the rose, she is not happy and cannot be proposed")
        
        game.parser.parse_command("give rose to the princess")
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.check_preconditions(), True, "All preconditions are met, it should return True")

        game.parser.parse_command("propose marriage to the princess")
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.check_preconditions(), False, "If already married, the player cannot propose again")


    @weight(1)
    def test_propose_apply_effects(self):
        game = build_game()
        before_propose = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess"
        game.parser.parse_command(before_propose)
        
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.proposer.get_property("is_married") is True, False, "the player's is_married property should be False before getting married")
        self.assertEqual(a.propositioned.get_property("is_married") is True, False, "the princess's is_married property should be False before getting married")
        self.assertEqual(a.proposer.get_property("is_royal") is True, False, "the player's is_royal property should be False before getting married")

        X.Propose(game, "propose marriage to the princess").apply_effects()
        a = X.Propose(game, "propose marriage to the princess")
        self.assertEqual(a.proposer.get_property("is_married") is True, True, "the player's is_married property should be True after getting married")
        self.assertEqual(a.propositioned.get_property("is_married") is True, True, "the princess's is_married property should be True after getting married")
        self.assertEqual(a.proposer.get_property("is_royal") is True, True, "the player's is_royal property should be True after getting married")
        

# Section 1.4: Wear_Crown
        
    # @weight(1)
    # def test_wear_crown_init(self):
    #     game = build_game()
    #     a = X.Wear_Crown(game, "wear crown")
    #     self.assertEqual(a.character is None, False)
    #     self.assertEqual(a.crown is None, True)

    #     before_wear = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess, propose to the princess"
    #     game.parser.parse_command(before_wear)
    #     a = X.Wear_Crown(game, "wear crown")
    #     self.assertEqual(a.crown is None, False)


    @weight(1)
    def test_wear_crown_check_preconditions(self):
        game = build_game()
        a = X.Wear_Crown(game, "wear crown")
        self.assertEqual(a.check_preconditions(), False, "If there is no crown here, it should return False")

        before_propose = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess"
        game.parser.parse_command(before_propose)
        a = X.Wear_Crown(game, "wear crown")
        self.assertEqual(a.check_preconditions(), False, "If the player is not yet married to the princess, it should return False")

        game.parser.parse_command("propose marriage to the princess")
        a = X.Wear_Crown(game, "wear crown")
        self.assertEqual(a.check_preconditions(), True, "All preconditions are met, it should return True")

        game = build_game()
        no_crown = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, go up, go up, go up, unlock door, go up, give rose to the princess, propose marriage to the princess"
        game.parser.parse_command(no_crown)
        a = X.Wear_Crown(game, "wear crown")
        self.assertEqual(a.check_preconditions(), False, "If the player doesn't have the crown, it should return False")


    # @weight(1)
    # def test_wear_crown_apply_effects(self):
    #     game = build_game()
    #     before_wear = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess, propose marriage to the princess"
    #     game.parser.parse_command(before_wear)
    #     a = X.Wear_Crown(game, "wear crown")
    #     self.assertEqual(a.character.get_property("is_crowned") is True, False, "the player is crowned before wearing the crown")

    #     X.Wear_Crown(game, "wear crown").apply_effects()
    #     a = X.Wear_Crown(game, "wear crown")
    #     self.assertEqual(a.character.get_property("is_crowned") is True, True, "the player is not crowned after wearing the crown")


# Section 1.5: Sit_On_Throne
        
    # @weight(1)
    # def test_sit_on_throne_init(self):
    #     game = build_game()
    #     a = X.Sit_On_Throne(game, "sit on throne")
    #     self.assertEqual(a.character is None, False)
    #     self.assertEqual(a.throne is None, True)

    #     before_sit = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess, propose to the princess, wear crown, down, down, east, east"
    #     game.parser.parse_command(before_sit)
    #     a = X.Sit_On_Throne(game, "sit on throne")
    #     self.assertEqual(a.throne is None, False)


    @weight(1)
    def test_sit_on_throne_check_preconditions(self):
        game = build_game()
        a = X.Sit_On_Throne(game, "sit on throne")
        self.assertEqual(a.check_preconditions(), False, "If there is no throne here, it should return False")

        not_crowned = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess, propose marriage to the princess, down, down, east, east"
        game.parser.parse_command(not_crowned)
        a = X.Sit_On_Throne(game, "sit on throne")
        self.assertEqual(a.check_preconditions(), False, "If the player is not wearing the crown, it should return False")

        # game.parser.parse_command("wear crown")
        # a = X.Sit_On_Throne(game, "sit on throne")
        # self.assertEqual(a.check_preconditions(), True, "All preconditions are met, it should return True")


    @weight(1)
    def test_sit_on_throne_apply_effects(self):
        game = build_game()
        before_sit = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up, unlock door, go up, give rose to the princess, propose marriage to the princess, wear crown, down, down, east, east"
        game.parser.parse_command(before_sit)
        a = X.Sit_On_Throne(game, "sit on throne")
        self.assertEqual(a.character.get_property("is_reigning") is True, False, "The player's is_reigning property should not be True before sitting on the throne")

        X.Sit_On_Throne(game, "sit on throne").apply_effects()
        a = X.Sit_On_Throne(game, "sit on throne")
        self.assertEqual(a.character.get_property("is_reigning") is True, True, "The player's is_reigning property should be True after sitting on the throne")


############################################################
# Section 2: Blocks
############################################################



# Section 2.1: Guard_Block
        
    # @weight(1)
    # def test_guard_block_init(self):
    #     game = build_game()
    #     before_hit = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east"
    #     game.parser.parse_command(before_hit)
    #     b = game.player.location.blocks["east"]
    #     self.assertEqual(b.guard is None, False)
    #     self.assertEqual(b.location is None, False)


    @weight(1)
    def test_guard_block_is_blocked(self):
        game = build_game()
        before_hit = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east"
        game.parser.parse_command(before_hit)
        b = game.player.location.blocks["east"]
        self.assertEqual(b.is_blocked(), True, "The guard should block you from going east")

        game.parser.parse_command("hit guard with branch")
        b = game.player.location.blocks["east"]
        self.assertEqual(b.is_blocked(), False, "The guard should no longer prevent you from going east")

# Section 2.2: Darkness
        
    # @weight(1)
    # def test_darkness_init(self):
    #     game = build_game()
    #     before_light = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down"
    #     game.parser.parse_command(before_light)
    #     b = game.player.location.blocks["down"]
    #     self.assertEqual(b.location is None, False)
    #     self.assertEqual(b.location.get_property("is_dark"), True)


    @weight(1)
    def test_darkness_is_blocked(self):
        game = build_game()
        before_light = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down"
        game.parser.parse_command(before_light)
        b = game.player.location.blocks["down"]
        self.assertEqual(b.is_blocked(), True, "The darkness should block you from going down")

        game.parser.parse_command("light lamp")
        b = game.player.location.blocks["down"]
        self.assertEqual(b.is_blocked(), False, "The darkness should no longer prevent you from going down")

# Section 2.3: Door_Block
        
    # @weight(1)
    # def test_door_block_init(self):
    #     game = build_game()
    #     before_unlock = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up"
    #     game.parser.parse_command(before_unlock)
    #     b = game.player.location.blocks["up"]
    #     self.assertEqual(b.location is None, False)
    #     self.assertEqual(b.door is None, False)


    @weight(1)
    def test_door_block_is_blocked(self):
        game = build_game()
        before_unlock = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east, hit guard with branch, get key, go east, get candle, go west, go down, light lamp, go down, light candle, read runes, get crown, go up, go up, go up"
        game.parser.parse_command(before_unlock)
        b = game.player.location.blocks["up"]
        self.assertEqual(b.is_blocked(), True, "The door should block you from going up")

        game.parser.parse_command("unlock door")
        b = game.player.location.blocks["up"]
        self.assertEqual(b.is_blocked(), False, "The door should no longer prevent you from going up")


# Section 3: Add Blocks
    @weight(1)
    def test_add_all_blocks(self):
        game = G
        before_hit = "sequence take pole, go out, go south, catch fish with pole, go north, pick rose, smell rose, go north, go up, get branch, go down, go east, give the troll the fish, go east"
        game.parser.parse_command(before_hit)
        self.assertEqual("east" in game.player.location.blocks, True, "The guard block is not added to the correct direction or location")
        self.assertEqual(game.player.location.blocks['east'].name, "A guard blocks your way", "wrong guard block is added")
        
        guard2darkness = "hit guard with branch, get key, go east, get candle, go west, go down"
        game.parser.parse_command(guard2darkness)
        self.assertEqual("down" in game.player.location.blocks, True, "The darkness is not added to the correct direction or location")
        self.assertEqual(game.player.location.blocks['down'].name, "Darkness blocks your way", "wrong darkness block is added")
        
        darkness2door = "light lamp, go down, light candle, go up, go up, go up"
        game.parser.parse_command(darkness2door)
        self.assertEqual("up" in game.player.location.blocks, True, "The door block is not added to the correct direction or location")
        self.assertEqual(game.player.location.blocks['up'].name, "A locked door blocks your way", "wrong door block is added")


if __name__ == '__main__':
    unittest.main()
