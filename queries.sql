-- 01_unique_sites
SELECT DISTINCT Launch_Site FROM launches ORDER BY Launch_Site;

-- 02_cca_records
SELECT Date, Booster_Version, Launch_Site FROM launches WHERE Launch_Site LIKE 'CCA%' ORDER BY Date LIMIT 5;

-- 03_nasa_payload
SELECT SUM(PAYLOAD_MASS__KG_) AS total_kg FROM launches WHERE Customer='NASA (CRS)';

-- 04_v11_payload
SELECT AVG(PAYLOAD_MASS__KG_) AS average_kg FROM launches WHERE Booster_Version LIKE 'F9 v1.1%';

-- 05_first_ground
SELECT MIN(Date) AS first_ground_success FROM launches WHERE Landing_Outcome='Success (ground pad)';

-- 06_drone_payload
SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE Landing_Outcome='Success (drone ship)' AND PAYLOAD_MASS__KG_>4000 AND PAYLOAD_MASS__KG_<6000;

-- 07_mission_outcomes
SELECT Mission_Outcome, COUNT(*) AS launches FROM launches GROUP BY Mission_Outcome ORDER BY launches DESC;

-- 08_max_payload
SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE PAYLOAD_MASS__KG_=(SELECT MAX(PAYLOAD_MASS__KG_) FROM launches);

-- 09_2015_failures
SELECT substr(Date,6,2) AS month, Landing_Outcome, Booster_Version, Launch_Site FROM launches WHERE substr(Date,1,4)='2015' AND Landing_Outcome='Failure (drone ship)' ORDER BY Date;

-- 10_rank_outcomes
SELECT Landing_Outcome, COUNT(*) AS launches FROM launches WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' GROUP BY Landing_Outcome ORDER BY launches DESC;