#!/usr/bin/env python3

# SSH Configuration
# DataBase description
# # SQL
db_sql_env_sql = "mysql"
db_sql_env_api = "pymysql"
db_sql_username = "root"
db_sql_user_passwd = "981119"
db_sql_ip = "127.0.0.1"
db_sql_port = 3306
db_sql_name = "final"

# # MongoDB
db_mongodb_ip = "127.0.0.1"
db_mongodb_port = 27017
db_mongodb_name = "final"
db_order_collection = "order"
db_check_collection = "orderToCheck"

# demo_db_arg = conf.db_env_sql + "+" + conf.db_env_api + "://" + conf.db_username + ":" + \
#     conf.db_user_passwd + "@" + conf.db_ip + \
#     ":" + conf.db_port + "/" + conf.db_name

token_key = "secret"

timeDiff = 120
