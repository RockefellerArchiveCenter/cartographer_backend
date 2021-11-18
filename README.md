# cartographer_backend

An Django application which provides a backend API to manage JSON tree representations of all archival collections, sub-collections, and parts (record group, subgroup, series, subseries, etc.) by a designated agent/creator ("arrangement maps" for short).

cartographer_backend is part of [Project Electron](https://github.com/RockefellerArchiveCenter/project_electron), an initiative to build sustainable, open and user-centered infrastructure for the archival management of digital records at the [Rockefeller Archive Center](http://rockarch.org/).

[![Build Status](https://app.travis-ci.com/RockefellerArchiveCenter/cartographer_backend.svg?branch=base)](https://app.travis-ci.com/RockefellerArchiveCenter/cartographer_backend)

## Local Development

Install [git](https://git-scm.com/) and clone the repository

    $ git clone https://github.com/RockefellerArchiveCenter/cartographer_backend.git

With [Docker](https://store.docker.com/search?type=edition&offering=community) installed, run docker-compose from the root directory

    $ docker-compose up

Once the application starts successfully, you should be able to access the application in your browser at `http://localhost:8000`

When you're done, shut down docker-compose

    $ docker-compose down

Or, if you want to remove all data

    $ docker-compose down -v


## Deploying in production

In order to deploy in production, `cartographer_backend` expects the following environment variables to be set (the values associated with each of these may change):

```
DEBUG=1  # whether or not the application should run in debug mode, 0 is False and 1 is True
SECRET_KEY=^6yxvs8k9czbwt9o8!y^ay)$il4^*9d(eykpo8%u5)-js9n6wfk  # the secret key used by WSGI
DJANGO_ALLOWED_HOSTS=cartographer-backend localhost  # a space-delimited list of allowed hosts
SQL_ENGINE=django.db.backends.postgresql  # The database engine to use
SQL_DATABASE=cartographer_backend_dev  # The database name to connect to
SQL_USER=cartographer_backend  # The database user to connect with
SQL_PASSWORD=cartographer_backend  # The password associated with the database user
SQL_HOST=cartographer-db  # The database host
SQL_PORT=5432  # The port at which the database is avaialble
AS_BASEURL=http://sandbox.archivesspace.org:8089/  # The base URL for an ArchivesSpace instance
AS_USERNAME=admin  # The ArchivesSpace user to connect with
AS_PASSWORD=admin  # The password for the ArchivesSpace user
AS_REPO_ID=2  # The identifier for the ArchivesSpace repository you want to target
CORS_ORIGIN_WHITELIST=http://localhost:3000  # A list of hosts that are allowed to access the API using CORS
```

You can either provide these variables on the command line or in an [env file](https://docs.docker.com/compose/env-file/).


### Routes

| Method | URL | Parameters | Response  | Behavior  |
|--------|-----|---|---|---|
|GET|/maps|`modified_since` - returns only maps modified since the time provided (as a Unix timestamp) <br/>`published` - if present, returns only published maps|200|Returns a list of maps, ordered by most recent first|
|GET|/delete-feed|`deleted_since` - returns only maps deleted since the time provided (as a Unix timestamp)|200|Returns a list of deleted maps, ordered by most recent first|
|GET|/status||200|Returns the status of the application|
|GET|/schema.json||200|Returns the OpenAPI schema for this application|


## Development

This repository contains a configuration file for git [pre-commit](https://pre-commit.com/) hooks which help ensure that code is linted before it is checked into version control. It is strongly recommended that you install these hooks locally by installing pre-commit and running `pre-commit install`.


## License

This code is released under an [MIT License](LICENSE).
