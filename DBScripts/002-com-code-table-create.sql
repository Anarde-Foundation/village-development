BEGIN;
--
-- Create model code
--

CREATE TABLE `com_code` (`code_id` integer NOT NULL PRIMARY KEY, `code_name` varchar(255) NOT NULL, `display_order` integer NULL, `comment` varchar(255) NULL, `created_on` datetime(6) NOT NULL, `modified_on` datetime(6) NOT NULL);
--
-- Create model code_group
--
CREATE TABLE `com_code_group` (`code_group_id` integer NOT NULL PRIMARY KEY, `code_group_name` varchar(255) NOT NULL UNIQUE, `created_on` datetime(6) NOT NULL, `modified_on` datetime(6) NOT NULL);
--
-- Add field code_group to code
--
ALTER TABLE `com_code` ADD COLUMN `code_group_id` integer NOT NULL;
ALTER TABLE `com_code` ADD CONSTRAINT `com_code_code_group_id_fk_com_code_group_code_group_id` FOREIGN KEY (`code_group_id`) REFERENCES `com_code_group` (`code_group_id`);
COMMIT;

insert into zzz_db_script values('002_com_code_table_create.sql', now());