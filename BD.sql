CREATE TABLE chat_history_ip (
    user_id TEXT,
    role TEXT,
    message TEXT,
    fecha DATE,
    message_id INT,
    nombre_usuario TEXT
);

CREATE TABLE user_feedback (
    user_id TEXT,
    feedback TEXT,
    timestamp DATE,
    message_id INT
);