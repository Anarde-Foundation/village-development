BEGIN;
--
-- Create model domain
--
CREATE TABLE `com_domain` (`domain_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `domain_name` varchar(255) NOT NULL, `description` longtext NULL, `created_on` datetime(6) NOT NULL, `modified_on` datetime(6) NOT NULL, `created_by` integer NULL, `modified_by` integer NULL);
ALTER TABLE `com_domain` ADD CONSTRAINT `com_domain_created_by_fk_auth_user_id` FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `com_domain` ADD CONSTRAINT `com_domain_modified_by_fk_auth_user_id` FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`);
COMMIT;


insert into zzz_db_script values('009-domain-table-create.sql', now());