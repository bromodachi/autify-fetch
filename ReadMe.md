# Autify - Backend engineer test - fetch

## Running the program

1. Build the docker image:<br>`docker build -t fetch-html-pages .`
2. Next, run it! Example:<br>
`docker run --rm -v $(pwd):/fetch fetch-html-pages --metadata https://www.google.com https://autify.com https://www.w3schools.com`

## Introduction

A really simple python script that just downloads the HTML page using requests and beautifulsoup.
We also attempt to save the assets but this isn't perfect. It will attempt to save images, scripts, and css only.
Some images, the url can be of base64. We try to decrypt this and write the content but this isn't always perfect.

The main objective is to complete everything within 2-4 hours. Hence, there are bugs around and lack of test cases.