import xml.etree.ElementTree as ET
import pyodbc
import csv

import os
import sys

from typing import TypedDict, List

# Conf
file_name = sys.argv[1]  # Percorso del file XML
connection_string = """ Driver={ODBC Driver 17 for SQL Server};
                        Server=DESKTOP-CGCL2TS;
                        Database=xmlToDb;
                        Trusted_connection=no;
                        UID=user;
                        PWD=pass"""

class DatabaseMappedXML(TypedDict):
    db_table: str
    db_column: str
    data_xml_path: str
    id_xml_path: str
    id_attr: str

class DatabaseMappedData(TypedDict):
    db_table: str
    db_column: str
    data: str
    db_id: str

def get_schema()-> List[DatabaseMappedXML]:
    schema_dict_list: List[DatabaseMappedXML] = list()

    with open('schema.csv', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='|')
        row: DatabaseMappedXML
        for row in csv_reader:
            schema_dict_list.append({
                'data_xml_path' : row['data_xml_path'],
                'db_table' : row['db_table'],
                'db_column' : row['db_column'],
                'id_xml_path': row['id_xml_path'],
                'id_attr': row['id_attr']
            })

    return schema_dict_list
            
def parse_xml_to_data(schema_dict_list: List[DatabaseMappedXML]) -> List[DatabaseMappedData]:
    dict_list: List[DatabaseMappedData] = list()

    item: DatabaseMappedXML
    for item in schema_dict_list:
        # Parsing del file XML
        tree = ET.parse(file_name)
        root = tree.getroot()

        dict_list.append({
            'data': root.find(item['data_xml_path']).text,
            'db_table': item['db_table'],
            'db_column': item['db_column'],
            'db_id': root.find(item['id_xml_path']).attrib.get(item['id_attr'], None),
        })

    return dict_list


def insert_data_to_db(dict_lst: List[DatabaseMappedData]):
    # Database Connection
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    for item in dict_lst:
        update_query =  f"""
                        UPDATE {item['db_table']}
                        SET {item['db_column']} = ?
                        WHERE id = ?
                        """
        
        params = [item['data'], item['db_id'], ]
        cursor.execute(update_query, *params)
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    try:
        schema = get_schema()
        data_schema = parse_xml_to_data(schema)
        insert_data_to_db(data_schema)
        os.replace(file_name, f"./processed/{file_name}")
        return f"{file_name} successfully parsed"
    except:
        os.replace(file_name, f"./error/{file_name}")
        return "error on parsing"
        

sys.stdout.write(main())
sys.stdout.flush()
sys.exit(0)