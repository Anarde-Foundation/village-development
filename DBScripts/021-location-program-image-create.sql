BEGIN;
--
-- Create model location_program_image
--
CREATE TABLE `loc_location_program_image` (`location_program_image_id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                                           `image_name` varchar(255) NOT NULL,
                                           `created_on` datetime(6) NOT NULL,
                                           `created_by` integer NULL,
                                           `image_type_code_id` integer NOT NULL,
                                           `location_program_id` bigint NOT NULL);
ALTER TABLE `loc_location_program_image` ADD CONSTRAINT `loc_location_program_image_created_by_fk_auth_user_id`
             FOREIGN KEY (`created_by`) REFERENCES `auth_user` (`id`);
ALTER TABLE `loc_location_program_image` ADD CONSTRAINT `loc_location_program_image_type_code_id_fk_com_code_`
             FOREIGN KEY (`image_type_code_id`) REFERENCES `com_code` (`code_id`);
ALTER TABLE `loc_location_program_image` ADD CONSTRAINT `loc_location_program_location_program_id_fk_loc_locat`
             FOREIGN KEY (`location_program_id`) REFERENCES `loc_location_program` (`location_program_id`);
COMMIT;

insert into zzz_db_script values('021-location-program-image-create.sql', now());