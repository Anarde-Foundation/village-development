BEGIN;
--
-- Create model survey
--
CREATE TABLE `sur_survey`( `survey_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                           `survey_name` varchar(255) NOT NULL,
                           `survey_type_code_id` integer NOT NULL,
                           `location_name` varchar(255) NOT NULL,
                           `publish_date` date NOT NULL,
                           `created_on` datetime(6) NOT NULL,
                           `modified_on` datetime(6) NOT NULL,
                           `created_by` integer NULL,
                           `modified_by` integer NULL);

ALTER TABLE `sur_survey` ADD CONSTRAINT `sur_survey_created_by_fk_auth_user_id`
                         FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);

ALTER TABLE `sur_survey` ADD CONSTRAINT `sur_survey_modified_by_fk_auth_user_id`
                         FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`);

ALTER TABLE `sur_survey` ADD CONSTRAINT `sur_survey_survey_type_code_id_fk_com_code_code_id`
                         FOREIGN KEY (`survey_type_code_id`) REFERENCES `com_code` (`code_id`);

COMMIT;

insert into zzz_db_script values('004-create-survey-table.sql', now());