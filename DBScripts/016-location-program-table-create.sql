BEGIN;
--
-- Create model location_program
--
CREATE TABLE `loc_location_program` (`location_program_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `date_of_implementation` date NOT NULL, `notes` longtext NULL, `created_on` datetime(6) NOT NULL, `modified_on` datetime(6) NOT NULL, `created_by` integer NULL, `location_id` bigint NOT NULL, `modified_by` integer NULL, `program_id` bigint NOT NULL);
ALTER TABLE `loc_location_program` ADD CONSTRAINT `loc_location_program_created_by_fk_auth_user_id` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `loc_location_program` ADD CONSTRAINT `loc_location_program_location_id_fk_loc_locat` FOREIGN KEY (`location_id`) REFERENCES `loc_location` (`location_id`);
ALTER TABLE `loc_location_program` ADD CONSTRAINT `loc_location_program_modified_by_fk_auth_user_id` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `loc_location_program` ADD CONSTRAINT `loc_location_program_program_id_fk_com_domai` FOREIGN KEY (`program_id`) REFERENCES `com_domain_program` (`domain_program_id`);
COMMIT;

insert into zzz_db_script values('01-loaction-program-table-create.sql', now());