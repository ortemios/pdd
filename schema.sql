DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    menu_state VARCHAR(64),
    quiz_category_id INT,
    question_index INT,
    scheduled_category_id INT,
    scheduled_frequency INT,
);