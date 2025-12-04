CREATE DATABASE fletes_mudanzas;
USE fletes_mudanzas;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    nombre_item VARCHAR(100),
    cantidad INT DEFAULT 1,
    FOREIGN KEY (email) REFERENCES usuarios(email) ON DELETE CASCADE
);
