BEGIN;
--
-- Add field domain_id to survey_question
--
ALTER TABLE `sur_survey_question` ADD COLUMN `domain_id` bigint NULL;
--
-- Add field question_label to survey_question
--
ALTER TABLE `sur_survey_question` ADD COLUMN `question_label` varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE `sur_survey_question` ALTER COLUMN `question_label` DROP DEFAULT;
--
-- Add field option_label to survey_question_options
--
ALTER TABLE `sur_survey_question_options` ADD COLUMN `option_label` varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE `sur_survey_question_options` ALTER COLUMN `option_label` DROP DEFAULT;
ALTER TABLE `sur_survey_question` ADD CONSTRAINT `sur_survey_question_domain_id_fk_com_domain_domain_id` FOREIGN KEY (`domain_id`) REFERENCES `com_domain` (`domain_id`);
COMMIT;

insert into zzz_db_script values('011-survey-question-alter.sql', now());