# Scrapy settings for iClose project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'iClose'

SPIDER_MODULES = ['iClose.spiders']
NEWSPIDER_MODULE = 'iClose.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'iClose (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'iClose.middlewares.IcloseSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'iClose.middlewares.IcloseDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'iClose.pipelines.IclosePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


citys_list = [
    'dwight', 'haliburton', 'palmerston', 'scomberg', 'sundridge', 'city', 'springwater', 'omemee', 'sault', 'cobden', 'pickering', 
    'falls', 'newmarket', 'alexandria', 'centre', 'island', 'coburg', 'alban', 'hawkesbury', 'gananoque', 'acton', 'niagara-on-the-lake', 
    'fenelon', 'halton', 'exeter', '(milton)', 'huntsville', 'straffordville', 'jordan', 'pefferlaw', 'port', 'wilberforce', 'newcastle', 
    'spencerville', 'vaughan', 'schomberg', 'gwillimbury', 'barie', 'bolsover', 'ottawa', 'woodstock', 'kawartha', 'cannington', 'brights', 
    'st.', 'sunderland', 'honey', 'petersburg', 'forest', 'smithville', 'mitchell', 'mattawa', 'thorold', 'lively', 'moorefield', 'dundalk', 
    'southampton', 'mcnicoll', 'mallorytown', 'bay', 'ingersoll', 'kapuskasing', 'carp', 'kinmount', 'thornton', 'chelmsford', 'apsley', 
    'bancroft', 'winchester', 'sauble', 'station', 'arthur', 'davids', 'gower', 'greely', 'trent', 'windsor', 'cumberland', 'denfield', 
    'sandfield', 'madoc', 'freelton', 'scotland', 'janetille', 'thamesford', 'algonquin', 'aylmer', 'melancthon', 'brockville', 'spring', 
    'casselman', 'cheltenham', 'george', 'morrisburg', 'wellington', 'stoney', 'coldwater', 'hasting', 'st.catharines', 'wiarton', 'york', 
    'smiths', 'bluffs', 'sudbury', 'ancaster', 'sioux', 'smith', 'qwillimbury', 'concord', 'ste', 'dorset', 'kleinburg', 'britain', 
    'rockwood', 'valley', 'bellevillle', 'mountains', 'sydney', 'tilbury', 'south', 'kearney', 'niagara', 'chapleau', 'seguin', 'long', 
    'market', 'tillsonburg', 'severn', 'mulmur', 'princeton', 'portland', 'sutton', 'marmora', 'woodslee', 'dundas', 'baden', 'midland', 
    'wainfleet', 'selkirk', 'vaughn', 'parkhill', 'mckellar', 'hamburg', 'alliston', 'bruce', 'ridgetown', 'millbrook', 'catharines', 'whitby', 
    'georgetown', 'hills', 'brussels', 'angus', 'lucan', 'lombardy', 'hill', 'codrington', 'franks', 'gormley', 'petawawa', 'blue', 'simcoe', 
    'watford', 'temiskaming', 'swastika', 'charles', 'lucknow', 'timmins', 'stanley', 'aurora', 'barrie', 'bowmanville', 'elora', 'thornbury', 
    'oxford', 'east', 'river', 'uxbridge', 'tara', 'lisle', 'braceridge', 'newtonville', 'maple', 'thorndale', 'kincardine', 'cornwall', 
    'manitock', 'oro-medonte', 'pinelake', 'erin', 'carling', 'lake', 'lookout', 'lorne', 'kirkland', 'bend', 'cambridge', 'northbrook', 
    'pauls', 'king', 'janetville', 'delhi', 'inglewood', 'point', 'erie', 'oak', 'bramalea', 'ste.', 'gilmour', 'shores', 'ridges', 'beaverton', 
    'creek', 'thornhill', 'elmwood', 'komoka', 'hastings', 'tweed', 'northern', 'coe', 'nepean', 'campbellville', 'stayner', 'napanee', 'cavan', 
    'elgin', 'brantford', 'burks', 'cochrane', 'thamesville', 'ottawa-(nepean)', 'caledonia', 'langton', 'mississuaga', 'sherkston', 'muskoka', 
    'elmvale', 'amherstburg', 'kent', 'russell', 'mansfield', 'new', 'nobleton', 'streetsville', 'dover', 'dunrobin', 'havelock', 'norland', 
    'chatham', 'little', 'noelville', 'gore', 'iroquois', 'lak', 'dryden', 'st', 'perth', 'scugog', 'nestor', 'minden', 'drayton', 'bond', 
    'gooderham', 'balderson', 'orleans', 'essex', 'breslau', 'restoule', 'ayr', 'cookstown', 'thomas', 'oshawa', 'brighton', 'dutton', 'burlington', 
    'puslinch', 'albert', 'goulais', 'sharbot', 'st.catherines', 'elliot', 'frontenac', 'fort', 'kanata', 'marathon', 'stratford', 'innerkip', 
    'paterborough', 'vankleek', 'chesterville', 'hanover', 'dashwood', 'township', 'on', 'minesing', 'thedford', 'colbourne', 'town)', 
    'sound', 'beach', 'selwyn', 'inverary', 'narrows', 'marys', 'scarborough', 'cobourg', 'killaloe', 'hanmer', 'shelburne', 'brydges', '-lake', 
    'petrolia', 'london', 'arva', 'ingleside', 'kleinberg', 'waterdown', 'brampton', 'thessalon', 'rockland', 'caledon', 'gravenhurst', 
    'welland', 'limoges', 'cherry', 'kimberley', 'jackson', 'therese', 'place', 'hannon', 'bracebridge', 'oakville', 'kilworthy', 'harrow', 'balm', 
    'rosseau', 'lasalle', 'ashton', 'markham', 'stittsville', 'campbellford', 'harbour', 'mactier', 'almonte', 'ridgeway', 'fergus', "burk's", 
    'creemore', 'norwood', 'val', 'highlands', 'harriston', 'deseronto', 'camlachie', 'stouffville', 'kingston', 'windham', 'blind', 'strathroy', 
    'goderich', 'perkinsfield', 'lindsay', 'otterville', 'kitchener', 'bayfield', 'wingham', 'ripley', 'newboro', 'keswick', 'howe', 'owen', 
    'belle', 'bacebridge', 'mount', 'tiny', 'eganville', 'thunder', 'durham', 'dunnville', 'everett', 'the', 'palgrave', 'ennismore', 'goodwood', 
    'ridgeville', 'lakefield', 'innisfill', 'walkerton', 'espanola', 'vittoria', "barry's", 'liskeard', 'athens', 'englehart', 'kirkfield', 
    'madawaska', 'rowan', 'markdale', 'borden', 'loring', 'orangeville', 'baysville', 'ajax', 'west', 'delaware', 'wasaga', 'midhurst', 
    'keewatin', 'shallow', 'paris', 'caledon/cheltenham', 'innisfil', 'collingwood', 'georgian', 'maitland', 'dorchester', 'toronto', 'embrun', 
    'head', 'elmira', "l'orignal", 'tottenham', 'hamilton', 'etobicoke', 'courtice', 'ypres', 'seaforth', 'richmond', 'clark', 'lynden', 
    'stroud', 'pakenham', 'red', 'ave', 'peterborough', 'bridgenorth', 'roseneath', 'carleton', 'clearview', 'flesherton', 'waterloo', 
    'bradford', 'perry', 'fonthill', 'beeton', 'temagami', 'calabogie', 'lakeshore', 'gloucester', 'paisley', 'meaford', "mary's", 'jacksons', 
    'bala', 'glencoe', 'trenton', 'bolton', '(cope', 'beamsville', 'chesley', 'grimsby', 'frances', 'tobermory', 'merrickville', 'mississauga', 
    'tecumseth', 'warkworth', 'lions', 'north', 'catherines', 'tecumseh', 'hope', 'amaranth', 'parry', 'powassan', 'sarnia', 'deep', 
    'niagara-on-the', 'manotick', 'bewdley', 'cameron', 'bramptom', 'mississagua', 'castleton', 'glenburnie', 'emsdale', 'waterford', 
    'kenora', 'williamstown', 'norwich', 'wallaceburg', 'bobcaygeon', 'marie', 'kemptville', 'unionville', 'lancaster', 'mills', '1058', 
    'leamington', 'lefroy', 'sturgeon', 'magnetawan', 'listowel', 'charlton-dack', 'virgil', 'westport', 'morriston', 'woodbridge', 
    'orillia', 'milton', 'utterson', 'renfrew', 'zurich', 'arnprior', 'heidelberg', 'mono', 'kingsville', 'kars', 'brechin', 'buckhorn', 
    'hamiton', 'penetanguishene', 'metcalfe', 'washago', 'craighurst', 'roches', 'grand', 'grove', 'picton', 'callander', 'cavan-monaghan', 
    'corunna', 'current', 'colborne', 'prescott', 'pembroke', "lion's", 'belleville', 'ganaoque', 'edward', 'clinton', 'guelph', 'wyevale', 
    'blenheim', 'coboconk', 'peninsula', 'brooklin', 'whitchurch-stouffville', 'lakes'
]