SELECT
--    analysis.id,
    analysis.link,
--    analysis.by_coefficient,
--    analysis.by_series,
--    analysis.by_position_table,
--    analysis.who_must_win,
--    analysis.who_now_win,
    analysis."comment",
    analysis.status
--    analysis."result",
--    "current".id,
--    "current".link,
--    "current".sport_name,
--    "current".match_date,
--    "current".match_time,
--    "current".country,
--    "current".tournament,
--    "current".tour,
--    "current".team1,
--    "current".team2,
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
--    "current".kf1,
--    "current".kf2,
--    "current".status
FROM flashscore.analysis
left join flashscore."current"
on "current".link = analysis.link
where "current".match_date='12.04.2025'
--and analysis.status not in ('Завершен', 'Будет доигран позже', 'Неявка', 'Послеовертайма', 'Перенесен')