CREATE TABLE image_names (
    image_id VARCHAR2(36) PRIMARY KEY,
    image_name VARCHAR2(255),
    last_modified_by VARCHAR2(255),
    last_modified_at TIMESTAMP
);

CREATE TABLE drawings (
    drawing_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    image_id VARCHAR2(36),
    version NUMBER,
    created_at TIMESTAMP,
    created_by VARCHAR2(255)
);

CREATE TABLE pixels (
    drawing_id NUMBER,
    x INTEGER,
    y INTEGER,
    rgb VARCHAR2(7)
);
