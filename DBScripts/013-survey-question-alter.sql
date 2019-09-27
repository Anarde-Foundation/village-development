BEGIN;
--
-- Alter field domain_id on survey_question
--
ALTER TABLE `sur_survey_question` DROP FOREIGN KEY `sur_survey_question_domain_id_fk_com_domain_domain_id`;
ALTER TABLE `sur_survey_question` ADD CONSTRAINT `sur_survey_question_domain_id_fk_com_domain_domain_id` FOREIGN KEY (`domain_id`) REFERENCES `com_domain` (`domain_id`);
COMMIT;

insert into zzz_db_script values('013-survey-question-alter.sql', now());
