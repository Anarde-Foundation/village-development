BEGIN;
--
-- Create model survey_response
--
CREATE TABLE `sur_survey_response` (`survey_response_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `kobo_response_id` integer NOT NULL, `survey_id` bigint NOT NULL);
--
-- Create model survey_response_detail
--
CREATE TABLE `sur_survey_response_detail` (`survey_reponse_detail_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `survey_response_value` varchar(255) NOT NULL, `survey_question_id` bigint NOT NULL, `survey_question_options_id` bigint NULL, `survey_response_id` bigint NOT NULL);
ALTER TABLE `sur_survey_response` ADD CONSTRAINT `sur_survey_response_survey_id_fk_sur_survey_survey_id` FOREIGN KEY (`survey_id`) REFERENCES `sur_survey` (`survey_id`);
ALTER TABLE `sur_survey_response_detail` ADD CONSTRAINT `sur_survey_response__survey_question_id_fk_sur_surve` FOREIGN KEY (`survey_question_id`) REFERENCES `sur_survey_question` (`survey_question_id`);
ALTER TABLE `sur_survey_response_detail` ADD CONSTRAINT `sur_survey_response__survey_question_opti_fk_sur_surve` FOREIGN KEY (`survey_question_options_id`) REFERENCES `sur_survey_question_options` (`survey_question_options_id`);
ALTER TABLE `sur_survey_response_detail` ADD CONSTRAINT `sur_survey_response__survey_response_id_fk_sur_surve` FOREIGN KEY (`survey_response_id`) REFERENCES `sur_survey_response` (`survey_response_id`);
COMMIT;

insert into zzz_db_script values('014-create-survey-response.sql', now());