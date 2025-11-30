#!/bin/python
import subprocess
import json
import shutil
import os
import sys

if len(sys.argv) > 1:
    inputPath = sys.argv[1]
else:
    inputPath = input("Enter file path to your corrupted AntennaPod database: ")

corruptedVersion = subprocess.run(["sqlite3", inputPath, "PRAGMA user_version;"], capture_output=True, text=True).stdout.strip()
if corruptedVersion == "0":
    print("Error: File not found, not a database, or too corrupted for this script.")
    exit()
print("Corrupted file version: " + corruptedVersion)

emptyPath = "empty/" + corruptedVersion + ".db"
if not os.path.isfile(emptyPath):
    emptyPath = input("Enter file path to an EMPTY AntennaPod database with the same version. If needed, you can download old app versions on F-Droid and export an empty database: ")
    emptyVersion = subprocess.run(["sqlite3", emptyPath, "PRAGMA user_version;"], capture_output=True, text=True).stdout.strip()
    print("Empty file version: " + emptyVersion)
    if corruptedVersion != emptyVersion:
        print("Error: Version does not match")
        exit()
print()

outputPath = inputPath + "-repaired.db"
sqlPath = inputPath + ".sql.tmp"
corruptedPath = inputPath + ".tmp"

shutil.copyfile(emptyPath, outputPath, follow_symlinks=True)
if os.path.exists(sqlPath): os.remove(sqlPath)
if os.path.exists(corruptedPath): os.remove(corruptedPath)


# Recover to SQL commands and insert back into a database
print("Recovering database.")
subprocess.run(["sqlite3", inputPath, ".recover --ignore-freelist"], check=True, stdout=open(sqlPath, 'w'))
f = open(sqlPath,'r', encoding='utf-8', errors='ignore')
filedata = f.read()
f.close()
f = open(sqlPath,'w')
f.write(filedata.replace("CREATE TABLE sqlite_sequence(name,seq);","")) # Avoid a warning that could be confusing to users
f.close()
subprocess.run(["sqlite3", corruptedPath], stdin=open(sqlPath, 'r'))
print()


# Insert relevant columns into a new database
def query(db, query):
    result = ""
    try:
        result = subprocess.run(["sqlite3", "-json", db, query], capture_output=True, check=True, text=True).stdout
        return json.loads(result)
    except subprocess.CalledProcessError as err:
        print(err.stderr)
        exit()
    except json.decoder.JSONDecodeError as err:
        return result

tables = query(emptyPath, "SELECT name FROM sqlite_schema WHERE type='table';")
for table in tables:
    table = table["name"]
    print("Copying " + table + "...")
    columns = query(emptyPath, "SELECT GROUP_CONCAT(NAME,',') AS columns FROM PRAGMA_TABLE_INFO('" + table + "')")[0]["columns"]
    
    query(outputPath, "DELETE FROM " + table)
    query(outputPath, "attach '" + corruptedPath + "' AS old; INSERT INTO main." + table + " SELECT " + columns + " from old." + table + ";")
print()

# Cleanup
os.remove(sqlPath)
os.remove(corruptedPath)
print("Done. Output file: " + outputPath)
