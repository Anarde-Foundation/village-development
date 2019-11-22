insert into com_code_group values(101, 'Image Type', now(), now());

insert into com_code (code_id, code_name, display_order, `comment`, created_on, modified_on, code_group_id)
select 101001, 'Before Program was conducted', 2, '', now(), now(), 101 union
select 101002, 'After Program was conducted', 2, '', now(), now(), 101;

insert into zzz_db_script values('020-com-code-insert-image-types.sql', now());