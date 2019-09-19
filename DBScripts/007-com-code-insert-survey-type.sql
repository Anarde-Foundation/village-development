insert into com_code_group values(100, 'Survey Type', now(), now());

insert into com_code (code_id, code_name, display_order, `comment`, created_on, modified_on, code_group_id)
select 100001, 'Base Line Survey', 1, '', now(), now(), 100 union
select 100002, 'Six monthly Survey', 1, '', now(), now(), 100;

insert into zzz_db_script values('007-com-code-insert-survey-type.sql', now());