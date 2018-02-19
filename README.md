# smrpg_web_randomizer

New Web-based randomizer for Super Mario RPG based on the [Gentle Beauty and Raw Power](https://github.com/abyssonym/smrpg_gbarp) randomizer by abyssonym.

This web version is a Django-powered site.  It is assumed you know how to deploy Django to use this.

If you came here just looking to use the randomizer to generate games, head to [the official community website](http://randomizer.smrpgspeedruns.com) where we host this for everyone.  This repository is only needed if you want to contribute to the development of the randomizer.

## Installing required packages

```> pip install -r requirements.txt```

## Setting up

1. Make a copy of `example_local.py` and call it `local_settings.py`. This is where you will enter any deployment-specific settings for your instance of the website.

   ```> cp example_local.py local_settings.py```

1. Change `local_settings.py` as needed.  Generally the only thing that would be different in your deployment is the database settings.  The default is a local SQLite file, but I recommend something more robust, ex. PostgreSQL.

1. Run all migrations for your database:

   ```> python manage.py migrate```

1. Collect all the static files as per standard Django deployment:

   ```> python manage.py collectstatic```

1. Set up your Django web server however you prefer.  There are plenty of resources out there on this topic.
