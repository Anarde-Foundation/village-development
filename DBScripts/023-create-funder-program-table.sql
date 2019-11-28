BEGIN;
--
-- Create model funder_program
--
CREATE TABLE `fun_funder_program` (`funder_program_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                                   `funding_amount` integer NOT NULL,
                                   `funder_id` bigint NOT NULL,
                                   `location_program_id` bigint NOT NULL);
ALTER TABLE `fun_funder_program` ADD CONSTRAINT `fun_funder_program_funder_id_fk_fun_funder_funder_id`
                                 FOREIGN KEY (`funder_id`) REFERENCES `fun_funder` (`funder_id`);
ALTER TABLE `fun_funder_program` ADD CONSTRAINT `fun_funder_program_location_program_id_fk_loc_locat`
                                 FOREIGN KEY (`location_program_id`) REFERENCES `loc_location_program` (`location_program_id`);
COMMIT;

insert into zzz_db_script values('023-create-funder-program-table.sql', now());