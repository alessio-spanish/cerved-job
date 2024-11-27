import xml.etree.ElementTree as ET
import pyodbc

# Conf
file_path = "example.xml"  # Percorso del file XML
connection_string = """ Driver={ODBC Driver 17 for SQL Server};
                        Server=DESKTOP-CGCL2TS;
                        Database=xmlToDb;
                        Trusted_connection=no;
                        UID=user;
                        PWD=pass"""
table_name = "dbo.Books"  # Nome della tabella nel database

def parse_and_insert_xml(file_path, connection_string, table_name):
    """
    Legge un file XML e inserisce i dati in un database MSSQL.
    :param file_path: Percorso del file XML
    :param connection_string: Stringa di connessione MSSQL
    :param table_name: Nome della tabella dove inserire i dati
    """
    try:
        # Connessione al database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Parsing del file XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        print(f"Inserendo dati nella tabella '{table_name}'...")
        
        # Itera sui nodi XML e inserisce i dati nel database
        for child in root:
            # Estrai i dati dagli elementi XML
            id_value = child.attrib.get("id", None)
            author = child.find("author").text if child.find("author") is not None else None
            title = child.find("title").text if child.find("title") is not None else None
            genre = child.find("genre").text if child.find("genre") is not None else None
            price = child.find("price").text if child.find("price") is not None else None
            publish_date = child.find("publish_date").text if child.find("publish_date") is not None else None

            # Inserisce i dati nel database
            insert_query = f"""
            INSERT INTO {table_name} (id, author, title, genre, price, publish_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (id_value, author, title, genre, price, publish_date))

        # Commit delle modifiche
        conn.commit()
        print("Dati inseriti con successo!")
    except ET.ParseError as e:
        print(f"Errore di parsing XML: {e}")
    except pyodbc.Error as e:
        print(f"Errore di database: {e}")
    except Exception as e:
        print(f"Errore sconosciuto: {e}")
    finally:
        # Chiudi la connessione al database
        cursor.close()
        conn.close()


# Esegui la funzione
parse_and_insert_xml(file_path, connection_string, table_name)
