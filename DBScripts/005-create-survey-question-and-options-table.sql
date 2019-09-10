BEGIN;
--
-- Create model survey_question
--
CREATE TABLE `sur_survey_question` (`survey_question_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                                    `survey_id` bigint NOT NULL,
                                    `section_id` varchar(255) NULL,
                                    `question_name` varchar(255) NOT NULL);
--
-- Create model survey_question_options
--
CREATE TABLE `sur_survey_question_options` (`survey_question_options_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                                            `option_name` varchar(255) NOT NULL,
                                            `survey_question_id` bigint NOT NULL);

ALTER TABLE `sur_survey_question` ADD CONSTRAINT `sur_survey_question_survey_id_fk_sur_survey_survey_id`
                                  FOREIGN KEY (`survey_id`)
                                  REFERENCES `sur_survey` (`survey_id`);

ALTER TABLE `sur_survey_question_options` ADD CONSTRAINT `sur_survey_question__survey_question_id_fk_sur_surve`
                                          FOREIGN KEY (`survey_question_id`)
                                          REFERENCES `sur_survey_question` (`survey_question_id`);

COMMIT;

insert into zzz_db_script values('005-create-survey-question-and-options-table.sql', now());