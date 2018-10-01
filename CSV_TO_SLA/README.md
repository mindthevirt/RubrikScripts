# Create Rubrik SLAs from a CSV file
This script allows you to create multiple Rubrik SLAs from a CSV file.
CSV_TO_SLA comes in handy when creating large number of SLAs in a cluster.

## Requirements
Before running the script, please download requirements.txt and install the required modules

`pip install -r requirements.txt`

## Usage
`python csvtosla.py <csv-file>`

You'll also need to provide the DNS or IP of the Rubrik Cluster, a username and password.

## Template.csv explained
Take a look at template.csv for the required CSV formatting.
The columns are explained below:

**SLA_NAME** - Specifies the name of the SLA

**EVERY_X_HOURS** - Take a backup every x hours

**KEEP_HOURLY_FOR_X_DAYS** - Keep hourly backups for x days

**EVERY_X_DAYS** - Take a backup every x days

**KEEP_DAILY_FOR_X_DAYS** - Keep daily backup for x days

**EVERY_X_MONTHS** - Take a backup ever x months

**KEEP_MONTHLY_FOR_X_YEARS** - Keep monthly backup for x years

**EVERY_X_YEARS** - Take a backup every x years

**KEEP_YEARLY_FOR_X_YEARS** - Keep yearly backups for x years

**ARCHIVE_LOCATION** - Specify archive location name

**ARCHIVE_AFTER_X_DAYS** - Archive after x days

**REPLICATION_TARGET** - Specify replication target name

**REPLICATE_FOR_X_DAYS** - Replicated x days to another Rubrik cluster
