CREATE OR REPLACE  view vw_survey_locationwise_aggregate_data as
select A.* from (
SELECT SQ.survey_id AS survey_id, SQ.domain_id,
    SQ.survey_question_id AS survey_question_id,
    SQ.question_label AS question_label,
    SQ.question_name AS question_name,
    REPLACE(
        REPLACE(SQ.question_label,
            'Count of members - ',
            ''),
        'who are',
        '') AS label,
     '' as option_name,
     0 as survey_question_options_id,
    SUM(RD.survey_response_value) AS response
FROM sur_survey_response_detail RD
JOIN sur_survey_question SQ ON RD.survey_question_id = SQ.survey_question_id
WHERE	SQ.question_type = 'integer'
GROUP 	BY SQ.survey_id , SQ.survey_question_id , SQ.question_label , SQ.question_name, SQ.question_label,SQ.domain_id, option_name, survey_question_options_id

UNION

Select VQO.*
,COUNT(RD.survey_response_value) AS response
from
(SELECT SQ.survey_id AS survey_id,SQ.domain_id,
    SQ.survey_question_id AS survey_question_id,
    SQ.question_label AS question_label,
    SQ.question_name AS question_name,
    QO.option_label AS option_label,
    QO.option_name as option_name,
    QO.survey_question_options_id as survey_question_options_id
FROM sur_survey_question SQ
RIGHT JOIN	sur_survey_question_options QO on QO.survey_question_id = SQ.survey_question_id
WHERE	SQ.question_type in('select all that apply', 'select one')
Order by QO.survey_question_options_id
) as VQO
LEFT JOIN sur_survey_response_detail RD on VQO.option_name = RD.survey_response_value
and RD.survey_question_id = VQO.survey_question_id
GROUP 	BY VQO.survey_id , VQO.survey_question_id , VQO.question_label , VQO.question_name, VQO.option_label,option_name,
        VQO.survey_question_options_id, VQO.domain_id
       )  A
Order by A.option_name
;
insert into zzz_db_script values('024-vw_survey_locationwise_aggregate_data_alter.sql', now());

