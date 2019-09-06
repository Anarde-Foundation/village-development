BEGIN;
--
-- Create model location
--
CREATE TABLE `loc_location` (`location_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `location_name` varchar(255) NOT NULL, `date_of_intervention` date NOT NULL, `exit_date` date NULL, `created_on` datetime(6) NOT NULL, `modified_on` datetime(6) NOT NULL, `created_by` integer NULL, `modified_by` integer NULL);
ALTER TABLE `loc_location` ADD CONSTRAINT `loc_location_created_by_2b3876e7_fk_auth_user_id` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `loc_location` ADD CONSTRAINT `loc_location_modified_by_a9c1c8f3_fk_auth_user_id` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`);
COMMIT;

insert into zzz_db_script values('003_location_table_create.sql', now());