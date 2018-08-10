from main import *

# Set these values to those used by your database
dbuser = "benjamintzudiker"
dbpass = ""
dbname = "ckd"
dbhost = "localhost"

# Attempts to connect to the database
cursor = connect(dbuser, dbpass, dbname, dbhost)

# Supply information for the tables you'd like to include here
primaryTableWhereStatement = "exists (select 1 from encounter e1 where {alias}patient_id = e1.patient_id and exists (select 1 from diagnosis d1 where d1.encounter_id = e1.encounter_id and ((d1.icd_code like 'N17%' and d1.icd_type = 10) or (d1.icd_code like '584%' and d1.icd_type = 9))))"
setupAddPrimaryTable("patient", columnNames = ["date_of_birth", "gender", "race1", "race2", "mapped_race", "ethnicity", "mapped_ethnicity", "country", "state"], keyColumnName = "patient_id", whereMarkers = [("is_kidney_failure", primaryTableWhereStatement)])
setupAddSecondaryTable("encounter", columnNames = ["encounter_id", "encounter_date"], keyColumnName = "patient_id", parentTableName = "patient", parentKeyColumnName = "patient_id", orderBy = [("encounter_date", False)], limit = 200)
setupAddSecondaryTable("social_history", columnNames = ["encounter_id", "sexually_active", "female_partner", "male_partner", "smoking_status", "tobacco_pack_per_day", "tobacco_use_years", "tobacco_user", "tobacco_type", "smoke_start_date", "smoke_end_date", "alcohol_user", "alcohol_ounce_per_week", "alcohol_comment", "alcohol_type", "iv_drug_user", "illicit_drug_frequency", "illicit_drug_comment"], keyColumnName = "encounter_id", parentTableName = "encounter", parentKeyColumnName = "encounter_id", limit = 1)
setupAddSecondaryTable("lab", columnNames = ["encounter_id", "component_name", "text_results", "numeric_results"], keyColumnName = "encounter_id", parentTableName = "encounter", parentKeyColumnName = "encounter_id", limit = 5)

# Attempts to perform the export with the given table setup
run(mode = "buffered", buffer = 20000)

# Closes the database connection
close()