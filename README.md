# Super Mario RPG Open World Randomizer

New web-based randomizer for Super Mario RPG based on the original command line [Gentle Beauty and Raw Power](https://github.com/abyssonym/smrpg_gbarp) randomizer by abyssonym.

This web version is a Django-powered site in a Docker container.  It is assumed you know how to deploy Django and Docker to use this.

If you came here just looking to use the randomizer to generate games, head to [the official community website](http://randomizer.smrpgspeedruns.com) where we host this for everyone.  This repository is only needed if you want to contribute to the development of the randomizer.

## Install Docker

You will need to install Docker on your system.  Instructions for this are available on the [official Docker site](https://docs.docker.com/get-docker/).

## Developing locally

Once you've installed Docker (either the desktop client or command line interface), run the main `docker-compose.yml` file to build and run the development container:

```> docker compose up --build```

The development environment files are `.env.dev` and `.env.dev.db`.  These are set up to use testing values and run the Django development server on localhost port 8000.  You can change these as needed.

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
