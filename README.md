<div id="top"></div>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">milk discord bot</h3>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Running</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

Milk is basic discord bot that responds to basic commands.

## Structure

The code is organized in `controllers` each of which implement a particular set of methods. 
This is done by extending `AbstractController`.

On startup, the bot listens for messages and reactions. By itself, the bot does nothing. 
Its job is to pass the message/reaction content to its controllers.
As expected, each controller should override `process_message` if it should respond to messages, `process_reaction` for reactions. 

Each controller is a self-contained module that responds to the messages as it sees fit.
This allows for functionality to be added without changing any current code.

Also, at startup, a background thread is created to allow controllers to run tasks continuously.
Once again, this is done by each controller independently.

## Features

* Twitch - periodically checks twitch for the status of a particular stream and sets the bot state as "streaming".
* Music Player - streams music using ffmpeg to the current discord voice channel.
* GuildActivity - stores events on a database. This is still being experimented with.
* PornHub - using keywords as query, searches and sends a message with the title of a random video from PornHub.

## Getting Started
### Prerequisites

Install `python`, on the target system.
* Arch Linux
  ```sh
  # pacman -S python
  ```

### Running
1. Setup environment variables
* DISCORD_TOKEN - your discord app token
* TWITCH_CLIENT_ID -  your twitch app client id
* TWITCH_CLIENT_SECRET - your twitch app client secret
* TWITCH_STREAM_NAME - the name of the twitch stream that should be checked
* TWITCH_STREAM_URL - the url to watch the stream

2. Run `Milk.py` file
  ```sh
  # python Milk.py
  ```
<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
