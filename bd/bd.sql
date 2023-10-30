CREATE TABLE activos (
    idactivo INT PRIMARY KEY,
    idacorriente INT,
    idotroactivo INT,
    -- Otros campos de activos
    FOREIGN KEY (idacorriente) REFERENCES acorrientes(idacorriente),
    FOREIGN KEY (idotroactivo) REFERENCES otroactivos(idotroactivo)
);
-- Crear la tabla "acorrientes" con relación 1 a muchos dependiente con "clientes"
CREATE TABLE acorrientes (
    idacorriente INT PRIMARY KEY,
    idotroactivo INT,
    -- Otros campos de acorrientes
    FOREIGN KEY (idotroactivo) REFERENCES otroactivos(idotroactivo)
);
CREATE TABLE otroactivos (
    idotroactivo INT PRIMARY KEY,
    gndevengado FLOAT,
);
-- Añadir una columna idcliente en la tabla "acorrientes" que será una clave foránea hacia la tabla "clientes"
ALTER TABLE clientes
ADD idactivo INT;
ADD idacorriente INT;
ADD idotroactivo INT;



-- Establecer la clave foránea en la tabla "acorrientes"
ALTER TABLE clientes
ADD CONSTRAINT 
FOREIGN KEY (idactivo) REFERENCES activos(idactivo),
FOREIGN KEY (idacorriente) REFERENCES acorrientes(idacorriente),
FOREIGN KEY (idotroactivo) REFERENCES otroactivos(idotroactivo)