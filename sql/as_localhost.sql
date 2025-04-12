SELECT
--    analysis.id,
--    analysis.link,
--    "current".id,
--    "current".link,
--    "current".sport_name,
--    "current".match_date,
    "current".match_time,
    COALESCE("current".country, '') || '/' || COALESCE("current".tournament, '') || '/' || COALESCE("current".tour, '') AS "COUNTRY(TOURNAMENT)",
    "current".team1,
    "current".team2,
    "current".kf1,
    "current".kf2,
--    analysis.by_coefficient,
--    analysis.by_position_table,
--    analysis.by_series,
    COALESCE(analysis.by_coefficient, 0) || '/' || COALESCE(analysis.by_position_table, 0) || '/' || COALESCE(analysis.by_series, 0) AS "kf,table,series",
    COALESCE(analysis.who_must_win, 0) || '/' || COALESCE(analysis.who_now_win, 0)  AS "who must/now",
    analysis.status,
    analysis."result",
    analysis."comment"
--    "current".score1,
--    "current".score2,
--    "current".match_status,
--    "current".position1,
--    "current".position2,
--    "current".position_total,
--    "current".num_games1,
--    "current".num_games2,
--    "current".points1,
--    "current".points2,
--    "current".series1,
--    "current".series2,
--    "current".status
FROM flashscore.analysis
left join flashscore."current"
on "current".link = analysis.link
where "current".match_date='13.04.2025'
order by "current".match_time