```
 __              __    __     __                                        
|  |__  _____  _/  |_ |  | __|__|                                       
|  |  \ \__  \ \   __\|  |/ /|  |  hatki - Home Assistant To Kindle/HTML
|   |  \ / __ \_|  |  |    \ |  |  v2 (2021-03-13) by Knoe-WG           
|___|__/(______/|__|  |__|__\|__|                                       


```


This Project is intendet to gives old Devices such as a Amazon Kindle a new life by enabeling them to represent Homeassistant enteties. 

This Script will take all placeholders in HTML templates and propegate them with data from the homeassistant API 

```
usage: hatki.py [-h] -u URL [-t TOKENFILE] [-i INPUTFOLDER] [-o OUTPUTFOLDER]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Home Assistant API URL, e.g.
                        https://localhost:8123/api
  -t TOKENFILE, --tokenfile TOKENFILE
                        File that contains the Token for the Home Assistant
                        API. (default value: token.txt)
  -i INPUTFOLDER, --inputfolder INPUTFOLDER
                        Path to the folder that contains the HTML templates.
                        NOTE: Subfolders are NOT supported. (default value:
                        html-templates)
  -o OUTPUTFOLDER, --outputfolder OUTPUTFOLDER
                        Path to the folder where the generated HTML files will
                        be written. (default value: generated-html)
```


Requirements

* API Token for your Homeassistans Instance
* Host to run the hatki.py script and host the generated-html files.
* Device to show the Website (in this case a jailbroken Kindle Touch)

Example for a placeholder:


```
{{media_player.spotify_user1:attributes.media_artist}}
{{sensor.doorbell_triggered:attributes.timestamp}}
{{sensor.esp_temperature:state}}

```

Link to Homeassistant Community post: 
https://community.home-assistant.io/t/hatki-homeassistant-to-kindle-kiosk-dashboard/552843
