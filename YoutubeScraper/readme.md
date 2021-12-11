# Setup Virtual-env
 - Create a new folder (give it a name) and place the given zip file content into it.
 - Create a virtual-env by typing `virtualenv youtube_scraper-env`
 - Activate the virtual-env `source youtube_scraper-env/bin/activate`
 - Navigate to the folder where `requirment.txt` is placed.
 - Enter the following command: `pip install -r requirment.txt`

`your Setup is now complete.`

# Configurations
 - Navigate to `YoutubeScraper` folder and create a file named `.env`
 - Content of the file will be: `API_KEY=[your youtube api key]`

> NOTE: Create your youtube api key from the google developer console (search on google)

# Running the Code
For running the script the `virtual-env` must be activated.
Navigate to the folder where `YoutubeScraper` is placed.

Type the following command: 

`scrapy crawl youtube-crawler -a search_key=[query] -a language=[en-US] -a region=[US]`


> NOTE: We will be using python3.5+ here
