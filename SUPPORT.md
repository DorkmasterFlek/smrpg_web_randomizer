# Support

## Reporting bugs

Report bugs using [this form](https://github.com/Super-Mario-RPG-Randomizer/smrpg_web_randomizer/issues/new/choose).  
You can also use the `#bug-reports` channel in the [SMRPG discord](https://randomizer-beta.smrpgspeedruns.com/community), but you should use this to ask questions or gain clarity on something you're experiencing and then report it using the aforementioned form.  
There are two different forms for reporting bugs: one for issues that affect gameplay or your ability to complete the seed, and one that is purely cosmetic.

## Examples of what you should report

* Your seed is logically impossible to complete.
* You're able to obtain the same check multiple times.
* The prize you get from a check doesn't match what's in your spoiler log.
* One of your areas is gated by an event, but the area did not unlock when that event happened.
* You get a game over in a fight, but your game world was not restored to the state it was in at your last save (except for party member levels and stats, which persist through game overs).
* You get KOed by an attack that did not deplete your HP.
* A save box isn't glowing.
* You pick up an item that doesn't match the sprite it was rendered as, or the Moleville blue toad sells you an item that doesn't match what he described.
* Anything else that isn't working.

## Examples of things you should check BEFORE submitting a report 

* Don't report a seed as impossible to complete or a check as not working unless you're absolutely certain. You can talk to Frogfucius in Tadpole Pond and he will tell you about a world area with an available check you haven't done yet. You can also cross-reference [this list](https://randomizer-beta.smrpgspeedruns.com/checks) of checks in the game. Always do these things before reporting a seed as not completeable or a check as not working, because chances are you've just missed a prerequisite or forgotten a check.
* Some chests are supposed to open multiple times and should not be reported as bugs. Two of the three mimic fights do this, as do two chests in Nimbus Land, one chest in the Kero Sewers, and all three chests in the Mushroom Kingdom vault.
* The sprite or sale description for your item might not actually be incorrect. Each item's sprite and description is chosen based on what they're named, what they do, what they look like in battle, what their [concept art](https://www.mariowiki.com/Gallery:Super_Mario_RPG:_Legend_of_the_Seven_Stars#Items) looks like, and what graphical assets the original game provides us with. This means some accessories look like coins, the Cricket Jam and a Yoshi Ade look exactly the same, the Moleville blue toad will give you the same description for a Quartz Charm and a Shiny Stone even though only one of those is a key item, etc. 

## Examples of things you should NOT report

* Some sprites, especially treasure chest sprites, look broken in rooms with other gigantic sprites (i.e. Jawful) and you are also playing as Bowser or Peach. Bowser and Peach take up more vram than other characters for some animations which means the vram budget overflows in some rooms that were already low on space.
* Some sprites in battle glitch out when there are too many tiles on the same horizontal row, i.e. Bowser is in your middle slot, Yaridovich attacks your rightmost slot, Bowser temporarily disappears partially from the graphics overflow
* EXP stars in some world areas (particularly areas that didn't originally support EXP stars, like Booster Tower, Forest Maze, etc) freeze you for about a quarter second when activating or deactivating. This is known.
* Any glitch that happens with Crowd Control, which is not officially supported.
* Anything related to transmission of prizes in Archipelago. That should be brought up in the [Archipelago discord server](https://randomizer-beta.smrpgspeedruns.com/community).
* A randomized ship password or Melody Bay tune being too hard to solve. Don't enable these settings if you aren't ready to do some bruteforcing for references you aren't familiar with, the UI already warns you about this.
* Coin sprites and frog coin sprites are staying still and not spinning. This is a vram-sensitive concession that had to be made to allow these items to be shuffled into any prize location.
* Allies transforming into each other temporarily when they use some attacks or spells that they don't normally use in the original game. These animations are not transferrable on their own and have the original character baked into them. If this is a problem, use settings that keep weapons and spell assignments with their original owners.
* Some boss sprites (Mack, Exor, Count Down, etc) don't have a walking animation or can't face northwest/northeast. The animation frames just don't exist for every boss to be able to do this, so some of them are static objects that shift around on the ground.
* Dialogs missing from cutscenes or boss fights. This is on purpose to reduce mashing.