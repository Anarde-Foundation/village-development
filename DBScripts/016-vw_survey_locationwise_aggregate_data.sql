CREATE OR REPLACE  view vw_survey_locationwise_aggregate_data as
SELECT SQ.survey_id AS survey_id,
    SQ.survey_question_id AS survey_question_id,
    SQ.question_label AS question_label,
    SQ.question_name AS question_name,
    REPLACE(
        REPLACE(SQ.question_label,
            'Count of members - ',
            ''),
        'who are',
        '') AS label,
    SUM(RD.survey_response_value) AS response
FROM sur_survey_response_detail RD
JOIN sur_survey_question SQ ON RD.survey_question_id = SQ.survey_question_id
WHERE	SQ.question_type = 'integer'
GROUP 	BY SQ.survey_id , SQ.survey_question_id , SQ.question_label , SQ.question_name, SQ.question_label

UNION

SELECT SQ.survey_id AS survey_id,
    SQ.survey_question_id AS survey_question_id,
    SQ.question_label AS question_label,
    SQ.question_name AS question_name,
    QO.option_label AS label,
    COUNT(RD.survey_response_value) AS response
FROM	sur_survey_response_detail RD
JOIN 	sur_survey_question SQ ON RD.survey_question_id = SQ.survey_question_id
JOIN	sur_survey_question_options QO on QO.survey_question_id = SQ.survey_question_id and
        RD.survey_response_value = QO.option_name
WHERE	SQ.question_type in('select all that apply', 'select one')
GROUP 	BY SQ.survey_id , SQ.survey_question_id , SQ.question_label , SQ.question_name, QO.option_label, QO.survey_question_options_id



insert into zzz_db_script values('016-vw_survey_locationwise_aggregate_data.sql', now());