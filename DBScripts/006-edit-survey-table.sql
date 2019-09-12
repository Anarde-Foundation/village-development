BEGIN;
--
-- Add field kobo_form_id to survey
--
ALTER TABLE `sur_survey` ADD COLUMN `kobo_form_id` integer DEFAULT 0 NOT NULL;
ALTER TABLE `sur_survey` ALTER COLUMN `kobo_form_id` DROP DEFAULT;
COMMIT;

insert into zzz_db_script values('006-edit-survey-table.sql', now());