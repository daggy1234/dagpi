# Dagpi

A fast, and easy to use API. Enjoy powerful image manipulation, high quality datasets with reliability and security.

## About

This repo is a central hub for all of the dagpi repos. It houses info like the API schema, as well as a link to other repo's and explanations about their functions.

## Repos

In a nutshell Dagpi consists of the following repos

### Dagpi-Image

Source: [dagpi-image](https://github.com/daggy1234/dagpi-image)

This is the core of dagpi's image manipulation system. This microservice houses all of the code that takes in Image URL's and outputs processed images as files. Users can leverage a wide varity of filters, effects and memes. 

### Dagpi-Data

Source: [dagpi-data](https://github.com/daggy1234/dagpi-data)

This is used by dagpi to serve pre-prepared json datasets with a high speed service. It also takes advantage of powerful libraries to allow text search for certain datasets.


### Dagpi-Auth

Source: [dagpi-auth](https://github.com/daggy1234/dagpi-auth)

The central brain of dagpi, all token access, authorization and stat collection/processing is done by dagpi-auth. It connects to the postgres db's and interfaces, to provide a restful management for each component of the dagpi infra.

### Dagpi-Dashboard

Source: [dagpi-dashboard](https://github.com/daggy1234/dagpi-dashboard)

Every app needs a nice UI so users and devs alike can enjoy using our service. In order to alleviate troublesome managment, dagpi-dashboard creates an asthetic and responsive dashboard with advanced metric visualization.

### Dagpi-Central

Source: [dagpi-central](https://github.com/daggy1234/dagpi-central)

Rather than running sensitive stuff in our website, or exposing the critical dagpi-auth to the world, dagpi-central wraps dagpi-auth along with project management and admin features for dagpi-stadd.

### Dagpi-Cli

Source: [dagpi-cli](https://github.com/daggy1234/dagpi-cli)

A command line interface for managing your dagpi app. Built in rust and easy to use.

## Deployment

In order to minimize cost dagpi uses a powerful VPS running linux with docker engine. However, to distribute load in case of failure, other key infra runs everywhere.

Mentioned below is infra that does not run on the main server

- Website is deployed on vercel
- Dagpi-central deployed for availability
- Dagpi-Cdn (AWS s3 + cloudfront)
- AWS cloudfront
- AWS glacier backups
- Dagpi-Reset (AWS lambda)
- Dagpi-Central-db (AWS RDS)
- Stripe Checkout (premium checkout + donations)
- PayPal Checkout (donations)

Server Items, are all run using docker and networked via docker-compose

- Dagpi-auth
- dagpi-data
- dagpi-image
- postgresql (auth)
- timescale (statdb)
- nginx
- cadvisor
- prometheus
- grafana
- postgres-exporter
- postgres-backup

For a guide on how to deploy, its coming soon!

## API Blueprint

This repo contains the API blueprint, a manual schema to dagpi. Feel free to PR changes.

## API Issues

This repo can be used to communicate/ suggest issues for dagpi

## License

All rights reserved.
