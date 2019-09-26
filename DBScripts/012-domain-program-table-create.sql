BEGIN;
--
-- Create model domain_program
--
CREATE TABLE `com_domain_program` (`domain_program_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `program_name` varchar(255) NOT NULL, `description` longtext NULL, `created_on` datetime(6) NOT NULL, `modified_on` datetime(6) NOT NULL, `created_by` integer NULL, `domain_id` bigint NOT NULL, `modified_by` integer NULL);
ALTER TABLE `com_domain_program` ADD CONSTRAINT `com_domain_program_created_by_fk_auth_user_id` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `com_domain_program` ADD CONSTRAINT `com_domain_program_domain_id_fk_com_domain_domain_id` FOREIGN KEY (`domain_id`) REFERENCES `com_domain` (`domain_id`);
ALTER TABLE `com_domain_program` ADD CONSTRAINT `com_domain_program_modified_by_fk_auth_user_id` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`);
COMMIT;

insert into zzz_db_script values('012-doamin-program-table-create', now());