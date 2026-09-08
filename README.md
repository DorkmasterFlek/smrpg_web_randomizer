# Super Mario RPG Open World Randomizer

New web-based randomizer for Super Mario RPG based on the original command line [Gentle Beauty and Raw Power](https://github.com/abyssonym/smrpg_gbarp) randomizer by abyssonym.

This web version is a Django-powered site in a Docker container.  It is assumed you know how to deploy Django and Docker to use this.

If you came here just looking to use the randomizer to generate games, head to [the official community website](http://randomizer.smrpgspeedruns.com) where we host this for everyone.  This repository is only needed if you want to contribute to the development of the randomizer.

## Install git

You will need this to do anything with this repository. [Download here](https://git-scm.com/install/) and then clone the repo.

**Windows users**: When installing Git for Windows, during setup there is a screen labelled "Configuring the line ending conversion".  On this screen, select "Checkout as-is, commit as-is" (bottom option).  This should prevent Git on Windows from changing the line endings of the code files, which apparently can cause issues with Docker on Windows. If you already installed Git and did not do this during installation, you should run the command `git config --global core.autocrlf false` before cloning this repository to get the same effect.

## Install Docker

You will need to install Docker on your system.  Instructions for this are available on the [official Docker site](https://docs.docker.com/get-docker/).

## Developing locally

Once you've installed Docker (either the desktop client or command line interface), run the main `docker-compose.yml` file to build and run the development container:

```> docker compose up --build```

The development environment files are `.env.dev` and `.env.dev.db`.  These are set up to use testing values and run the Django development server on localhost:8000.  You can change these as needed.

When you get it up and running in your browser, open your browser's development console and disable caching (in Chrome this is a checkbox in the Network tab).

## Updating the base patch

To add fundamental changes to how the game works, i.e. ASM patches, patch randomizer/patches/open_mode.ips to a vanilla unheadered copy of SMRPG (you can use any IPS patching tool for this, including [web tools](https://www.marcrobledo.com/RomPatcher.js/)).  
Then make your changes however you like, i.e. in a [hex editor](https://www.heaventools.com/download-hex-editor.htm).  
Then, using the IPS patcher again, create a new open_mode.ips patch against a vanilla unheadered copy of SMRPG (this is "creator mode" in the patch web tool).  
Replace the old open_mode.ips file and then run `python3 randomizer/patches/build_json.py`.  
Restart the container. You may need to delete site data in your browser's development console to see the new version of the file.

## Debugging

- The "Debug Mode" checkbox maxes out your party stats.
- The "Generate Debug BPS Patches" checkbox creates indivudual patches of different data types (one for event scripts, one for spells, one for palettes, one for sprites, etc). Use these to help isolate the root cause of a broken ROM, but be warned it makes seed generation much slower.
  - Patches will go in the ./debug_patches folder, which is gitignored.
  - You must have a vanilla SMRPG rom named "smrpg.sfc" in the root directory of the randomizer, which is also gitignored. **DO NOT EVER** git commit a rom file!
- You can pre-assign certain items to certain locations, or put items in your starting inventory, using randomizer/debug/config.yml. This will only work if "Debug Mode" is enabled.
  - For starting inventory items, use the item class name in randomizer/data/items.py.
  - For pre-assigning prizes to checks, use the location and prize names from randomizer/progression/prizelocations/ and randomizer/progression/prizes/ (one class per file)
- You can use [Lazy Shell](https://github.com/Yakibomb/LAZYSHELL-UPDATED/releases) and [FlexHEX](https://www.heaventools.com/download-hex-editor.htm) to debug your randomized/patched ROM. Both are compatible with Wine with a little finagling.
  - I've added a `lazyshell` directory in this repo that includes a randomizer-compatible custom build executable (aka it can read from the randomizer's adjusted sprite data ranges, moved partition banks, can understand flexibly-written battle animations, can support 256 packets and ~1400 NPCs, includes custom event script commands, knows all the sprite/packet/eventscript/actionscript names). This is moderately compatible with wine.
  - You won't be able to view battle events in Lazy Shell. This is normal, unfortunately.

## Nuke and restart container

For when you suspect you're having a problem with cached old data.  
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && find . -type f -name "*.pyc" -delete && docker compose down -v && docker system prune -af && docker compose build --no-cache && docker compose up
```


## Deploying to production

1. Make a copy of the example production environment files:

   ```> cp example.env.prod .env.prod```

   ```> cp example.env.prod.db .env.prod.db```

   ```> cp example.env.prod.nginx .env.prod.nginx```

1. Change the production environment settings as needed.  You should generate a proper Django secret value and more secure database password at the very least.

1. Run the `docker-compose.prod.yml` file to build and run the production container:

   ```> docker compose -f docker-compose.prod.yml up --build -d```

This will run the production server in detached mode.  You can check the logs with:

```> docker compose -f docker-compose.prod.yml logs -f```

This will run a production Nginx web server on port 80 which forwards to the Django app using gunicorn, and also serves the static files through the web server.  You can change this in the `.env.prod.nginx` file if needed.

## Space optimization

The randomizer's patcher will attempt to allocate any unused space left over after encoding dialogs, event scripts, action scripts, battle events, or monster AI and repurpose it for sprite animation data. This is to make more room for sprite tiles.

Bank 0x35 for battle animations is also tightly packed, so adding new animations is difficult due to lack of space.

Some helpful commands you can run:
- `python manage.py analyze_repeated_sequences` - This will show you a list of command sequences in battle animation banks 0x35xxxx and 0x3Axxxx that are repeated in multiple places and would encode to 3 or more bytes. Consider giving the first command in one such instance a unique identifier, and replace all other instances with a `Jmp` to that identifier (which is 3 bytes). This will free up battle animation space. (If the sequence does not already end in `ReturnSubroutine` or `ReturnSpriteQueue`, you may have to extract the sequence elsewhere, end it it a return command, replace all original instances with a `Jmp` to your moved sequence, and test your ROM thoroughly to make sure it is not breaking anything. SMRPG can be volatile about nested subroutines.) Produces `repeated_sequences_report.txt`
- `python manage.py show_3a_free_space` - This details how much space in each script within animation data bank 0x3Axxxx is actually being used by animation code. Consider moving code around between scripts to create as many large contiguous empty blocks as possible to be repurposed for sprite code.
- `python manage.py find_referenced_empty_dialogs` - This will find dialogs that are used in event scripts but have no content. Use this to fix dialog bugs.
- `python manage.py find_unreferenced_dialogs_with_content` - This will find dialogs that are not used anywhere but have non-empty content, and do not share data with dialogs that are used somewhere. Produces `unreferenced_dialogs.txt`
- `python manage.py empty_dialog <dialog_ids...>` - Run this against a dialog ID that you know is not used anywhere (usually the results of `find_unreferenced_dialogs_with_content`). It will empty the dialog's data and replace it with `[await]`. Be careful not to run it against unused dialogs that share data with used dialogs. Be careful not to delete any dialogs that are referenced by `RunDialog(dialog_id=PRIMARY_TEMP_7000)` (these are denoted by comments in `dialog_pointers.py`).
- `python manage.py compress_dialogs --apply` - Removes every empty `[await]` dialog in your dialog table data files and shifts dialog pointers accordingly. Each `[await]` is a single byte, and this adds up when there are a lot of them, so this will condense your dialog data such that it leaves a large contiguous empty block at the end to be repurposed for sprite code. Run without `--apply` for a preview that does not change the files.
- `python manage.py fix_dialog_order` - Dialog IDs should have their data index pointer higher or equal to the previous dialog ID. If you want to add dialogs, run this after making your additions to make sure the data stays in order.
- `python manage.py sprite_pixel_shift <sprite_id> <dx> <dy> [--molds 0,1,5]` - Shifts all pixel data in a gridplane sprite's molds by the specified offset. Outputs new subtile_bytes that can be copied into the sprite file. This is useful for when you have converted a small tilemap sprite into a gridplane but need to fix its centering within the grid. Use `--molds` with comma-separated indices to target specific molds instead of all. Use `--visualize <mold_index>` to preview a specific mold before/after shifting.


## Adding user submissions

Make sure you've installed the GitHub CLI and authed to it.

### Wish Text

```bash
python manage.py add_submission --type wish --issue GITHUB_ISSUE_ID
```

### Quiz questions (SMRPG-related)

```bash
python manage.py add_submission --type quiz --issue GITHUB_ISSUE_ID
```

### Quiz questions (non-SMRPG, extended pool only)

```bash
python manage.py add_submission --type quiz --issue GITHUB_ISSUE_ID --non-smrpg
```

### Ship passwords
```bash
python manage.py add_submission --type password --issue GITHUB_ISSUE_ID
```

### Melody Bay songs
```bash
python manage.py add_submission --type song --issue GITHUB_ISSUE_ID
```

### Palettes
```bash
python manage.py add_submission --type palette --issue GITHUB_ISSUE_ID
```  
(You don't need to export screenshots of new palettes for the UI preview. Either run `python manage.py generate_palette_previews` or simply let the Github Actions CI automatically derive an image from the palette data.)

### Dry run (parse only, don't modify files)
```bash
python manage.py add_submission --type TYPE --issue GITHUB_ISSUE_ID --dry-run
```

### Presets

Not supported, just copy paste the text.