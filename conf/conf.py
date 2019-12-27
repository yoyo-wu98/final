#!/usr/bin/env python3

# SSH Configuration
ssh_host = "219.228.135.215"  # 堡垒机ip地址或主机名
ssh_port = 22  # 堡垒机连接mysql服务器的端口号，一般都是22，必须是数字
ssh_user = "hjzou"  # 这是你在堡垒机上的用户名
ssh_password = "981119"  # 这是你在堡垒机上的用户密码

# DataBase description
# # SQL
db_sql_env_sql = "mysql"
db_sql_env_api = "pymysql"
db_sql_username = "root"
db_sql_user_passwd = "123456"
db_sql_ip = "127.0.0.1"
db_sql_port = 3306
db_sql_name = "final"

# # MongoDB
db_mongodb_ip = "127.0.0.1"
db_mongodb_port = 3306
db_mongodb_username = "root"
db_mongodb_user_passwd = "981119"
db_mongodb_name = "final"
db_order_collection = "order"
db_check_collection = "orderToCheck"

# demo_db_arg = conf.db_env_sql + "+" + conf.db_env_api + "://" + conf.db_username + ":" + \
#     conf.db_user_passwd + "@" + conf.db_ip + \
#     ":" + conf.db_port + "/" + conf.db_name

token_key = "secret"

timeDiff = 120
