BEGIN;
--
-- Remove field location_name from survey
--
ALTER TABLE `sur_survey` DROP COLUMN `location_name`;
--
-- Add field location_id to survey
--
ALTER TABLE `sur_survey` ADD COLUMN `location_id` bigint DEFAULT 1 NOT NULL;
ALTER TABLE `sur_survey` ALTER COLUMN `location_id` DROP DEFAULT;
ALTER TABLE `sur_survey` ADD CONSTRAINT `sur_survey_location_id_fk_loc_location_location_id` FOREIGN KEY (`location_id`)
                         REFERENCES `loc_location` (`location_id`);
COMMIT;

insert into zzz_db_script values('008-edit-survey-table.sql', now());