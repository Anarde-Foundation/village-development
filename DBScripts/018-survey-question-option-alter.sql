BEGIN;
--
-- Add field question_weightage to survey_question
--
ALTER TABLE `sur_survey_question` ADD COLUMN `question_weightage` integer DEFAULT 1 NOT NULL;
ALTER TABLE `sur_survey_question` ALTER COLUMN `question_weightage` DROP DEFAULT;
--
-- Add field option_weightage to survey_question_options
--
ALTER TABLE `sur_survey_question_options` ADD COLUMN `option_weightage` integer DEFAULT 1 NOT NULL;
ALTER TABLE `sur_survey_question_options` ALTER COLUMN `option_weightage` DROP DEFAULT;
COMMIT;

insert into zzz_db_script values('018-survey-question-option-alter.sql', now());