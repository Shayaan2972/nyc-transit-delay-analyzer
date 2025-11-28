import psycopg2
import requests
import json
import os
from dotenv import load_dotenv

# Enviornment variables
load_dotenv()

# Connecting to database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname = os.getenv("DB_dbname"),
            user = os.getenv("DB_user"),
            password = os.getenv("DB_password"),
            host = os.getenv("DB_host"),
            port = os.getenv("DB_port")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
# Getting data from the API
def fetch_data_from_api(url, headers=None):
    try:
        response = requests.get(url, headers=headers) # Sending the GET request
        data = response.json() # Parse the JSON
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from API: {e}")
        return None
    

def parse_data(data):
    parsed_delays = []
    entities = data.get('entity', [])
    print (f"Found {len(entities)} entities in API response")

    for i, entity in enumerate(entities):
        try:
            alert = entity['alert']

            # Find train lines with a route id
            train_line = None
            for informed in alert['informed_entity']:
                if 'route_id' in informed:
                    train_line = informed['route_id']
                    break

            # If route id not found
            if not train_line:
                print(f"Skipping entity {i}: No route_id found")
                continue

            alert_message = alert['header_text']['translation'][0]['text']
            alert_type = alert['transit_realtime.mercury_alert']['alert_type']
            created = alert['transit_realtime.mercury_alert']['created_at']
            updated = alert['transit_realtime.mercury_alert']['updated_at']

            parsed_delays.append({
                'train_line': train_line,
                'alert_message': alert_message,
                'alert_type': alert_type,
                'created': created,
                'updated': updated
            })

        except KeyError as e:
            print(f"KeyError parsing entity {i}: missing {e}")
            continue
        except Exception as e:
            print(f"Error parsing entity {i}: {e}")
            continue
    
    print(f"Successfully parsed {len(parsed_delays)} delays")
    return parsed_delays

def insert_data_into_db(conn, data):
    try:
        cursor = conn.cursor() 
        inserted_count = 0

        for delay in data:
            query = """ 
            INSERT INTO subway_delays (train_line, alert_message, alert_type, created, updated)
            VALUES (%s, %s, %s, to_timestamp(%s), to_timestamp(%s))
            ON CONFLICT (train_line, alert_message, created) DO NOTHING
            """

            cursor.execute(query, (
                delay['train_line'],
                delay ['alert_message'],
                delay ['alert_type'],
                delay['created'], 
                delay['updated']))
        
            if cursor.rowcount > 0:
                inserted_count += 1

        conn.commit()
        print(f"Inserted {inserted_count} records")

    except Exception as e:
        print(f"Error inserting into databse: {e}")
        conn.rollback()
    finally:
        cursor.close()
    
# Main function
def main():
    url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"
    
    # Connect to the database 
    conn = connect_to_database()  
    if not conn:  
        print("Failed to connect to database")  
        return
    
    # Fetch the data from the API
    fetched = fetch_data_from_api(url)
    if not fetched:
        print("Failed to fetch from API")
        conn.close()
        return
    print(f"Fetched {len(fetched.get('entity', []))} records")

    # Parse the data
    parsed = parse_data(fetched)
    if not parsed:
        print("Failed to parse data")
        conn.close()
        return
    
    # Insert the data into the database
    insert_data_into_db(conn, parsed)
    
    # Close the connection
    conn.close()
    print("Transfer complete")

if __name__ == "__main__":
    main()