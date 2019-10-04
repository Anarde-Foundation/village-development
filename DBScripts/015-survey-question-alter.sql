BEGIN;
--
-- Add field question_type to survey_question
--
ALTER TABLE `sur_survey_question` ADD COLUMN `question_type` varchar(50) DEFAULT ' ' NOT NULL;
ALTER TABLE `sur_survey_question` ALTER COLUMN `question_type` DROP DEFAULT;
COMMIT;

insert into zzz_db_script values('015-survey-question-alter.sql', now());