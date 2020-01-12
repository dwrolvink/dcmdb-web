

import os
root = os.path.dirname(__file__)

config = {}
config["database_file"] = root+"/database.db"
config["verbosity"] = 3 # 0 = no printing, 1 = errors only, 2 = steps, 3 = debug