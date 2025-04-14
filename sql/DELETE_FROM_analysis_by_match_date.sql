DELETE FROM flashscore.analysis
WHERE link IN (
    SELECT "current".link
    FROM flashscore."current"
    WHERE "current".match_date = '14.04.2025'
);