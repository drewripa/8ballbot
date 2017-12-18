# 8ballbot

Simple bot with classic '8 Ball' answers from Wikipedia.

For working bot needs:
	- add file config.py to folder with bot.py
	- in *nix use /8ballbot folder for project (service run from root)
	- config.py should include 2 lines:
		token = 'TELEGRAM_TOKEN_FROM_BOTFATHER'
		host = 'IP_OR_DOMAIN_NAME_OF_SERVER'
  - create db and name it 8ball.db with:
      1 table called 'users':
          'userid' Integer, Not null, Unique
          'rertycount' (yes, misspelling) Integer
          'stats_yes', 'stats_no', 'stats_mb' all Integer
    and place it in db folder
		
Commands:
	/stats - user stats for yes/no/mb choose
	/usersstats - info about total users of this bot from Dinosaurs to current date and time
	
*Work in progress but still working bot*
