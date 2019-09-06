insert into auth_group (id, name)
select 1, 'Admin' union
select 2, 'Anarde_user ' union
select 3, 'Anganwadi_worker 'union
select 4, 'Funder';


CREATE TABLE `zzz_db_script` (
  `script_file_name` VARCHAR(255) NOT NULL,
  `migrated_on` TIMESTAMP(6) NOT NULL);
