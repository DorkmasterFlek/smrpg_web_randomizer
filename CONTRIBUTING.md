# Contributing

## Basics

If you are new to SMRPG modding, it is strongly recommended to look around the game in the [Lazy Shell editor](https://github.com/Yakibomb/LAZYSHELL-UPDATED/releases). This is a powerful ROM-editing GUI specifically designed for SMRPG that will greatly help you visualize how some of the most important parts of the game work.

Much of the randomizer's foundations are based in the [smrpgpatchbuilder](https://github.com/Super-Mario-RPG-Randomizer/smrpgpatchbuilder) library, which allows you to edit most of the randomizer-relevant game features as Python code and produces the bytes needed to patch those edits to the game. This library was designed to resemble the workflows and verbiage of Lazy Shell as much as possible.

The vast majority of things you will want to edit in this randomizer require no ASM knowledge.

### Settings

All randomizer settings are defined in randomizer/types/flags.py. You can see the breakdown of how different kinds of settings work, i.e. checkboxes vs selecting from a list.

### Tables

Most game data that doesn't affect progression logic is stored in tables, such as enemy stats, shop contents, weapon and armor stats, etc. Most of these things that are relevant to the randomizer are in the data folder. There are individual classes for each item/enemy/ally/etc with properties that represent their shuffle-able attributes, so they are pretty straightforward to interact with. These classes are based on smrpgpatchbuilder types so they have ROM-patching code built-in.

### Script System

Super Mario RPG's internal logic was originally designed around a **script system**. Scripts are artifacts that contain a sequential list of ASM "shortcuts" that allow you do interact with memory in a way that is simple and safe. For example, adding an item to your inventory is just a single script command, `AddToInventory(ITEM_ID)`, which smrpgpatchbuilder encodes as two bytes, `0xFD 0x50`. When this is inside a script, SMRPG's internal script interpreter will it in your randomized ROM and know exactly what to do with it. 

This design choice made it easy for anybody on the original development team to add easter eggs and funny non-required interactions to the game. It also makes it easy for us to mod the game! 

Most of what you will see happening in any world area or any battle is controlled by scripts. There are four kinds of scripts:

* **Event scripts**: These control the logic of just about anything that happens in a world area. Talk to a NPC? That's a script. Go from one room to another? That's a script. A new world area becomes accessible? Scripts did that. Start a boss battle? That's a script. Play Booster's curtain minigame? That's a complex series of scripts.
* **Action scripts**: These control how objects in a room are animated. These can be standalone scripts that are assigned as a property to a NPC, or they might be embedded inside an event script to force something to animate on the fly in response to another action, i.e. being talked to.
* **Monster AI**: These control the decision making of any enemy in battle, such as choosing spells, countering attacks, etc.
* **Battle Animation Scripts**: These control everything else in battle, such as weapon and spell animations, cutscenes, Super Jump logic, etc.

All of the progression logic and prize grants in SMRPG Randomizer are controlled by scripts. You can manipulate the game's contents and internal logic by adding, deleting, or modifying commands in these script artifacts. They're the bread and butter of most of what you see happen in the game, so that's usually what you want to edit if you would like to add a feature that deals with progression logic (i.e. adding conditions to open a world area) or retrofitting exising game features to accommodate various states of the randomizer seed that were not expected in the original game (i.e. adding logic to determine what happens in the Valentina fight if you only have two characters). 

Scripts require no ASM knowledge whatsoever to edit. Many talented SMRPG modders don't know any ASM at all.

To start off learning how to work with these, you can look in `flags.py`, look at the names of a couple of settings, search the codebase for them, and then see if those lead to invocations of methods like `world.event_scripts.replace_command_by_identifier()`, as well as other `event_scripts` class methods, to see how the randomizer adjusts the game's contents to adhere to a certain setting being enabled or disabled.

Edited scripts are assembled into a table and turned into patch bytes by smrpgpatchbuilder. The randomizer does this out-of-the-box, so you don't need to worry about how you're going to patch your script changes to the ROM. All you need to do is modify the script contents, and your changes will make it into the ROM.

### Etc

There are lots of other features in the game that are important to the randomizer, such as level exits, dialogs, etc. Look around in the Lazy Shell editor to see how these work. Most of these things you will find in the randomizer/data folder. It's recommended to explore the codebase for the randomizer a bit to see how these features are interacted with and modified.

### Troubleshooting

Once you get to the point of generating randomized ROMs in your local development environment, you'll find that there are parts of the game you can't look at in Lazy Shell anymore. This is because the randomizer moves some key pieces of the game's data around to areas that the program is not expected to find them. Download [pidge's fork of Lazy Shell](https://github.com/pidgezero-one/LAZYSHELL-UPDATED/releases) which supports randomizer ROMs. When you use it, the first thing you will need to do is open the settings panel (gear icon), flip to the last tab, and load the project database file `/lazyshell/randomizer.lsproj `(within the randomizer codebase). Then you will be able to look at things properly.

## Design Philosophy

Follow these guidelines when developing or suggesting new features for this randomizer:

The experience of playing SMRPG Randomizer should adhere to the experience of playing "the original game but shuffled and opened up" as much as possible, with some concessions in favour of scavenger hunt design. This means working with what the original game already offers us and avoiding adding things it never had. 

These are examples of things that generally should not be done:
* Inventing new spells that didn't exist originally (beyond element swapping)
* Adding prize checks to NPCs that never originally gave you anything
* Adding new characters or new enemies that didn't exist in SMRPG or its remake
* Adding new item concepts that didn't exist in the original game

Adding concepts from the 2023 Switch remake is an exception to all of the above. References to other media in the form of character palettes or NPC dialogs are also completely fine. 

A good way to think about changing what's canon to the original game is to consider bringing some utility to things that would otherwise be underused or never used (think the Ice Arrows in OOT being modified to act like Blue Fire, or the Spoon in FFIV becoming a weapon for Edward) or to restore some importance to items that could become fairly useless in a randomizer setting. In SMRPG Randomizer, there are some examples of this:
* A setting that infuses standard shop armors with specific immunities
* A setting that gives poison mushrooms a 1/8 chance of acting as a Red Essence
* A setting that turns two under-served locales into final boss warps
* A setting that makes the trade quest for the Monstro Town sealed door join the shuffle (as opposed to Shiny Stones being infinitely purchaseable in shops)

The important thing is to make sure these things are optional and disabled by default, so that players expecting the original game's experience will get that, but players who want to add some more depth to underused parts of the game have that choice.

If you are adding or suggesting new options for progression logic, follow these guidelines:
* The overworld map needs to form a complete traversable circle (so nothing like in V8 where gating Bowser's keep just meant you had to go all the way around the world map to get to nimbus land from marios pad, which we want to avoid in V9+). This is the entire basis of the "open world" concept as applied to a game that doesn't have a freely explorable overworld map, so it shouldn't be compromised. 
* There is a setting that removes Bowser's Keep from the overworld map and connects Nimbus Land directly to Vista Hill, and puts Bowser's Keep back in that path when it is unlocked. This can't be done with any other locales because there isn't enough space for more overworld map artifacts.
* Collectibles should be tangible objects and not abstract concepts. World areas themselves should not be standalone collectibles. Recruiting Mallow opens Bandit's Way = ✅, finding the Bandit's Way map dot in a chest = ❌
* No solidity/terrain mods. The level-assembling infrastructure does not support it. This means no doing things like blocking a path by adding solid bushes that get removed upon some condition.
* Adding physical objects ("NPC"s) to gate or block an area is fine as long as it makes sense in-universe and doesn't overflow the room's vram budget. For example, it's not very farfetched for the Nimbus Land trampoline or Land's End cannon be out of order, or for Luigi to be fixing the pipe entrance to Kero Sewers, Pipe Vault, etc.
* It's okay to create new collectibles as long as the collectible is tied to something that actually existed in the original game. For example, the Mario doll, Garro's gold paint, the four pieces of wedding gear, and the pink yoshi's Mushroom Derby cookies are all things that existed in the original game but were not items that can go into your inventory. They have become inventory items in the randomizer to allow for more interesting gating settings. This is as opposed to, for example, creating new keys to unlock rooms that never required key access, which should not be done.
* Event-based gating should be tied to something that happened around that time in the original game, which for example is why there's an option for exchanging the cricket pie to unlock the forest as opposed to i.e. exchanging the three musty fears flags to unlock the forest, or why fighting KGGG is an option to unlock the chapel but fighting the axem rangers is not an option to unlock the chapel, things like that.

## Will players like my idea?

You can bring up the thing you plan to develop in the #snes-rando-feature-discussion channel of https://discord.smrpgspeedruns.com. Although, even if nobody would use the feature except you, you can still add it as long as it adheres to the above guidelines and does not upend any existing features. This randomizer is all about choice.

## AI policy

If you use AI to help you write your code contributions, or if you don't use it, I don't care. This is a contentious topic in the hobbyist development community, but realistically you as a volunteer contributor are not expected nor obligated to spend more time manually working for free than you need to on a project rooted in highly esoteric domain knowledge that is already hurting for development interest. If you *want* to write all your volunteer contributor code by hand for free, please do, but that's your choice. If you do choose to use AI, try to carpool or take the bus to work tomorrow instead of driving or avoid buying animal products on your next grocery run if you want to offset your carbon footprint. 

Don't submit any code if you could not have written it yourself, unless you're _really_ confident in your ability to review that code, and this goes without saying, but never submit any code without thoroughly reviewing it and testing it yourself. If you don't know how to do that, don't submit it; either suggest it as a feature instead for somebody else to build, or work on your own coding skills first and submit it when you are more confident. "Vibe coding" is not a good idea for production code, especially if you have no development or SMRPG modding experience. You will be better off learning your way around the codebase foundations using your own brain first.

Do not commit any agent config files (i.e. .cursorrules, claude.md) to the codebase.

## Crediting

Add yourself to credits.py. This project is a labour of love that nobody gets paid for, everyone who contributes to it deserves recognition. 
* It's hard to tell from code alone how your changes to the credits screen will be aligned, so be sure to test the credits before submitting your PR.
* Only capital letters A-Z, spaces, periods, and underscores are supported. No numbers or other punctuation.
* If you've just developed a new optional feature, i.e. adding Mushroom Boy as a check, add yourself under "Feature Development" list. If you've developed something foundational or transformative to how the randomizer works as a whole, i.e. refactoring room entrances as a shuffler check subclass, add yourself to the "Core Development" list.
* Credit anybody who helped you on the feature whether they contributed code or research.
* If you borrowed code from somebody else's romhack that was not explicitly developed for the randomizer, add them to the "Special Thanks" section.
  * If anybody else besides the developer helped you find such code, add them as well.
  * Exception: Don't add anyone to "Special Thanks" if they are already listed elsewhere in the credits.