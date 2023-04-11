# Tiamat

The idea behind the Tiamat project is to provide a simple, easy to use, and ergonomic gaming keyboard.
For the moment the project is in a very early stage, but it is already possible to use it.
To spice things up, the Tiamat has an integrated display that doubles as the microcontroller.

<picture>
   <source media="(prefers-color-scheme: light)" srcset="https://github.com/Mqxx/GitHub-Markdown/blob/main/blockquotes/badge/light-theme/warning.svg">
   <img alt="Warning" src="https://github.com/Mqxx/GitHub-Markdown/blob/main/blockquotes/badge/dark-theme/warning.svg">
</picture><br>

| This is still a very early prototype and the files are constantly changing. It is best to use this repository as a reference instead of a ready to use project. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|

## Features

#### Keyboard features : 

- Ortholinear layout
- Anti Ghosting
- Collumn stagger of the modifier to accomodate for the pinkie
- Thumb cluster for the most used keys
- Smaller spacebar for a better ergonomics
- Stacked numbers and symbols rows for an easier access
- Only the most commonly used keys for gaming
- Hotswap sockets for MX switches

- 240x240 Pin Badge LCD display with backlight that doubles as the microcontroller
- Hotswap sockets for the display

#### Firmware features :

- CircuitPython based firmware
- KMK
- Highly customizable


## Gallery

<p align="center" width="100%">
    <img src="05_Assets/img0.png">
</p>

<p align="center" width="100%">
    <img src="05_Assets/img1.png">
</p>

<p align="center" width="100%">
    <img src="05_Assets/img2.png">
</p>

## Pin Display

### Polar coordinate snake Game

Complete Snake minigame that uses the polar coordinate system to make the best of the rounded display
Featuring :

- Completely autonomous game, no need to connect the keyboard to a computer only a power source ( you will still need to connect to the Tiamat or another keyboard to play)
- Multiple working menus
- Leaderboard and a highscore system ( stored on the display )
- Screenshot system ( stored on the display )
- And much more ! 

**Click to see on YouTube**
<p align="center" width="100%">
    <a href="https://youtu.be/_snwv8szKXo" target="_blank">
     <img src="https://img.youtube.com/vi/_snwv8szKXo/maxresdefault.jpg" alt="Mt. Choc Glitch Effect"/>
    </a>
</p>

### Animated Wolf

Logo with toggleable animation 

<p align="center" width="100%">
    <img src="05_Assets/wolf_animated.gif">
</p>

### Gyroscope controlled balls

Gyroscope controlled balls that will are physically simulated and collide with each other as well as the display borders

<p align="center" width="100%">
    <img src="05_Assets/gyroscope_balls.gif">
</p>


## Hardware

**WIP**

Display : https://www.waveshare.com/wiki/RP2040-LCD-1.28

## Build

**SOON**

## Firmware

**SOON**


## Credits

- Heavily inspired by Sonal Pinto and his [Mt-Choc](https://github.com/SonalPinto/mt-choc) project and all the ressources he provided
- Aedile for his [CircuitPython Implementation](https://github.com/aedile/circuit_python_wsRP2040128) of the Waveshare RP2040-LCD-1.28 that helped me a lot
