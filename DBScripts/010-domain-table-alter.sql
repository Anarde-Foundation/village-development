BEGIN;
--
-- Add field kobo_group_key to domain
--
ALTER TABLE `com_domain` ADD COLUMN `kobo_group_key` varchar(255) DEFAULT 'health' NOT NULL;
ALTER TABLE `com_domain` ALTER COLUMN `kobo_group_key` DROP DEFAULT;
COMMIT;

insert into zzz_db_script values('010-doamin-table-alter', now());