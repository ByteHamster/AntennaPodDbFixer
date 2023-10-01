# AntennaPod Db Fixer 

There are two situations in which the AntennaPod database might get broken:

- In a very old AntennaPod version, there were some issues with the database with all information (episodes, listening states, etc). While the cause is long fixed, your database might have been damaged (even when the app was working without issues). If a recent AntennaPod version makes changes to the damaged parts of the database, these damages may suddenly become a problem.
- AntennaPod runs on a large number of devices and flash memory sometimes just fails.

If AntennaPod detects a broken database, it dumps the broken database to the file `/sdcard/Android/data/de.danoeh.antennapod/CorruptedDatabaseBackup.db`.

This script automates the recovery process, so one does not need to go through [the steps](https://antennapod.org/documentation/bugs-first-aid/database-error) manually.

### License
This script is licensed under the GNU General Public License (GPL-3.0). You can find the license text in the LICENSE file.
