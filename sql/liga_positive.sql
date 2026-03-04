 WITH stats AS (
    SELECT
        "current".sport_name,
        "current".country,
        "current".tournament,
        COUNT(*) FILTER (WHERE
            analysis.who_must_win IS NOT NULL
            AND analysis.who_now_win IS NOT NULL
            AND analysis.who_must_win = analysis.who_now_win
        ) AS plus_count,
        COUNT(*) FILTER (WHERE
            analysis.who_must_win IS NOT NULL
            AND analysis.who_now_win IS NOT NULL
            AND analysis.who_must_win != analysis.who_now_win
        ) AS minus_count,
        COUNT(*) AS total
    FROM flashscore.analysis
    LEFT JOIN flashscore."current" ON "current".link = analysis.link
    WHERE analysis.status = 'ЗАВЕРШЕН'
    GROUP BY
        "current".sport_name,
        "current".country,
        "current".tournament
)
SELECT
    sport_name,
    country,
    tournament,
    plus_count,
    minus_count,
    total,
    ROUND(plus_count * 100.0 / NULLIF(total, 0)) AS plus_percent,
    ROUND(minus_count * 100.0 / NULLIF(total, 0)) AS minus_percent
FROM stats
where minus_count > 1 and plus_count > 1
ORDER BY plus_percent DESC;