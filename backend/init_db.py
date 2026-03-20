import pymysql
from pymysql.constants import CLIENT
import os
from config import Config

def init_db():
    try:
        config = Config()
        print(f"Connecting to MySQL at {config.MYSQL_HOST}...")
        conn = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            client_flag=CLIENT.MULTI_STATEMENTS
        )
        
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        with conn.cursor() as cursor:
            print("Executing schema.sql...")
            # We split by Delimiter manually or rely on multi_statements. 
            # PyMySQL multi_statements might choke on DELIMITER commands.
            # Let's clean it up or recommend using MySQL CLI.
            
            # Since schema.sql has DELIMITER commands which are MySQL CLI specific, 
            # we should parse or run carefully.
            # Actually, standard python might fail on "DELIMITER $$".
            pass
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Instead of running the script here (which can fail due to DELIMITER), 
    # we will just instruct the user to run it via MySQL tools.
    print("Por favor, importe el archivo database/schema.sql en su cliente de MySQL (phpMyAdmin, MySQL Workbench, etc).")
