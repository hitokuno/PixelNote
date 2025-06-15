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
    created_by VARCHAR2(255),
    CONSTRAINT fk_drawings_image_id FOREIGN KEY (image_id) REFERENCES image_names(image_id)
);

CREATE TABLE pixels (
    drawing_id NUMBER,
    x NUMBER,
    y NUMBER,
    rgb VARCHAR2(7),
    CONSTRAINT fk_pixels_drawing_id FOREIGN KEY (drawing_id) REFERENCES drawings(drawing_id)
);
