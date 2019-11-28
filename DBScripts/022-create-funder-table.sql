BEGIN;
--
-- Create model funder
--
CREATE TABLE `fun_funder` (`funder_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                           `organization_name` varchar(255) NOT NULL,
                           `funding_amount` integer NULL,
                           `funding_date` date NOT NULL,
                           `created_on` datetime(6) NOT NULL,
                           `modified_on` datetime(6) NOT NULL,
                           `created_by` integer NULL,
                           `modified_by` integer NULL,
                           `user_id` integer NOT NULL);
ALTER TABLE `fun_funder` ADD CONSTRAINT `fun_funder_created_by_fk_auth_user_id`
                         FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `fun_funder` ADD CONSTRAINT `fun_funder_modified_by_fk_auth_user_id`
                         FOREIGN KEY (`modified_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `fun_funder` ADD CONSTRAINT `fun_funder_user_id_fk_auth_user_id`
                         FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

insert into zzz_db_script values('022-create-funder-table.sql', now());