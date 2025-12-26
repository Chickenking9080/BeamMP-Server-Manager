# BeamMP-Server-Manager
BeamMP Neon is a web-based control center designed for administrators hosting BeamMP (BeamNG.drive Multiplayer) servers on Linux. Built with a focus on speed, security, and aesthetics, it eliminates the need for manual CLI management by providing a centralized dashboard for all server operations.
Core Capabilities:

    Real-Time Monitoring: Live telemetry tracking CPU and RAM consumption to maintain optimal server performance.

    Dynamic Mod Management: Dedicated interface to upload, track, and delete Client and Server resources without using FTP.

    Integrated Web Console: A live-streamed terminal window providing instant feedback from the server logs.

    Kinda Secure Design: Local password encryption and a "Connection Lost" fail-safe overlay to prevent unauthorized or accidental interactions during network instability.

    Automated Systems: One-click updates  and "Start on Boot" logic to ensure maximum uptime.

Tech Stack:

    Backend: Python 3 (Flask, Psutil)

    Frontend: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript

    Compatibility: Made for Ubuntu 24.04 LTS - Untested on other distrobutions

How To Install:

    Download The Latest BeamMP Neon Build

    Add it into a folder called BeamMP-Server in your user home directory

    Unzip the files you just downloaded into that folder

    Install Dependancies using this command - sudo apt update && sudo apt install -y python3-flask python3-psutil python3-requests python3-werkzeug liblua5.3-0

    Run this command while you are in your terminal opened in the BeamMP-Server folder - python3 app.py

    To access your management panel, open your web browser and enter the following into the address bar: http://YOUR_SERVER_IP:5000

    It should come up with a create password prompt, Create your password then log in with it, press the update button to download the latest ubuntu 24.04 server files then wn prompted restart

    After that you can go into the config editor and add in your Authentication key which you can get from the beammp keymaster and then change your beammp map to the one you want after that you are done! add in your ip to the direct connect field on beammp (or search up your set name in the search field) (has to be set in the config)

    Enjoy!

    PS: only tested on Ubuntu Server 24.04 I cannot say it will work on anything else but you can always try! :)
