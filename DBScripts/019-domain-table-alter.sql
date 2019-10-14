BEGIN;
--
-- Add field metabase_dashboard_id to domain
--
ALTER TABLE `com_domain` ADD COLUMN `metabase_dashboard_id` integer NULL;
COMMIT;

insert into zzz_db_script values('019-domain-table-alter.sql', now());