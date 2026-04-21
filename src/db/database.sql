CREATE TABLE "Rol" (
	"idRol" SERIAL,
	"nombre" VARCHAR(50) NOT NULL,
	PRIMARY KEY("idRol")
);

CREATE TABLE "Area" (
	"idArea" SERIAL,
	"nombre" VARCHAR(100) NOT NULL,
	"descripcion" VARCHAR(255),
	PRIMARY KEY("idArea")
);

CREATE TABLE "Usuario" (
	"idUsuario" SERIAL,
	"nombre" VARCHAR(100),
	"apellido" VARCHAR(100),
	"username" VARCHAR(100) NOT NULL UNIQUE,
	"email" VARCHAR(150) UNIQUE,
	"password_hash" TEXT NOT NULL,
	-- Solo para fines demostrativos, no incluir en produccion
	"password_salt" CHAR(32) NOT NULL,
	"idArea" INTEGER,
	"activo" BOOLEAN DEFAULT true,
	"idRol" INTEGER,
	PRIMARY KEY("idUsuario")
);


CREATE TABLE "ContactoExterno" (
	"idContactoExterno" SERIAL,
	"nombre" VARCHAR(150),
	"telefono" VARCHAR(50),
	"correo" VARCHAR(150),
	"empresa" VARCHAR(150),
	PRIMARY KEY("idContactoExterno")
);

CREATE TABLE "Adquisicion" (
	"idAdquisicion" SERIAL,
	"tipo" VARCHAR(20) NOT NULL,
	"fecha" DATE,
	"proveedor" VARCHAR(150),
	"donante" VARCHAR(150),
	"documentoReferencia" VARCHAR(100),
	"costoTotal" NUMERIC(12,2),
	"notas" TEXT,
	PRIMARY KEY("idAdquisicion")
);

CREATE TABLE "Equipo" (
	"idEquipo" SERIAL,
	"nombre" VARCHAR(150),
	"marca" VARCHAR(100),
	"modelo" VARCHAR(100),
	"funcion" VARCHAR(150),
	"clasificacion" VARCHAR(100),
	"tiempoVidaEstimado" TEXT,
	PRIMARY KEY("idEquipo")
);

CREATE TABLE "EquipoInstalado" (
	"idEquipoInstalado" SERIAL,
	"idEquipo" INTEGER NOT NULL,
	"numeroSerie" VARCHAR(100) NOT NULL UNIQUE,
    "estado" VARCHAR(50) NOT NULL CHECK("estado" IN ('activo', 'en_mantenimiento', 'fuera_de_servicio', 'dado_de_baja')),
	"fechaIngreso" DATE,
	"idArea" INTEGER,
	"garantia" BOOLEAN,
	"expiracionGarantia" DATE,
	"ubicacion" VARCHAR(150),
	"fechaBaja" DATE,
	"dadoDeBajaPor" INTEGER,
	"motivoBaja" TEXT,
	"idAdquisicion" INTEGER,
	PRIMARY KEY("idEquipoInstalado")
);

CREATE TABLE "EventoInventario" (
	"idEvento" SERIAL,
	"idEquipoInstalado" INTEGER,
	"tipoEvento" VARCHAR(50),
	"descripcion" TEXT,
	"fecha" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"idUsuario" INTEGER,
	PRIMARY KEY("idEvento")
);

CREATE TABLE "OrdenTrabajo" (
	"idOrden" SERIAL,
	"idEquipoInstalado" INTEGER,
	"descripcionFallo" TEXT,
	"prioridad" VARCHAR(20),
	"estado" VARCHAR(20),
	"fechaSolicitud" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"fechaInicio" TIMESTAMP,
	"fechaFin" TIMESTAMP,
	"asignadoA" INTEGER,
	"creadoPorUsuario" INTEGER,
	"creadoPorExterno" INTEGER,
	PRIMARY KEY("idOrden"),
    CONSTRAINT chk_creado_por CHECK ("creadoPorUsuario" IS NOT NULL OR "creadoPorExterno" IS NOT NULL)
);

CREATE TABLE "Mantenimiento" (
	"idMantenimiento" SERIAL,
	"idOrden" INTEGER,
	"tipo" VARCHAR(50),
	"fechaInicio" TIMESTAMP,
	"fechaFin" TIMESTAMP,
	"realizadoPor" INTEGER,
	"verificadoPor" INTEGER,
	"externo" BOOLEAN,
	"descripcionTrabajo" TEXT,
	"realizadoPorExterno" INTEGER,
	PRIMARY KEY("idMantenimiento")
);

CREATE TABLE "PlanMantenimiento" (
	"idPlan" SERIAL,
	"idEquipoInstalado" INTEGER,
	"tipo" VARCHAR(50),
	"frecuenciaDias" INTEGER,
	"ultimaEjecucion" DATE,
	"proximaEjecucion" DATE,
	PRIMARY KEY("idPlan")
);

CREATE TABLE "Refaccion" (
	"idRefaccion" SERIAL,
	"nombre" VARCHAR(150),
	"marca" VARCHAR(100),
	"modelo" VARCHAR(100),
	"descripcion" TEXT,
	PRIMARY KEY("idRefaccion")
);

CREATE TABLE "StockRefaccion" (
	"idStock" SERIAL,
	"idRefaccion" INTEGER,
	"cantidad" INTEGER NOT NULL DEFAULT 0,
	"stockMinimo" INTEGER,
	"ubicacion" VARCHAR(100),
	PRIMARY KEY("idStock")
);

CREATE TABLE "CompraRefaccion" (
	"idCompra" SERIAL,
	"idRefaccion" INTEGER,
	"cantidad" INTEGER,
	"costo" NUMERIC(12,2),
	"fechaCompra" DATE,
	"proveedor" VARCHAR(150),
	"lote" VARCHAR(100),
	PRIMARY KEY("idCompra")
);

CREATE TABLE "UsoRefaccion" (
	"idUso" SERIAL,
	"idMantenimiento" INTEGER,
	"idRefaccion" INTEGER,
	"cantidad" INTEGER,
	PRIMARY KEY("idUso")
);

CREATE TABLE "EquipoRefaccion" (
	"idEquipo" INTEGER,
	"idRefaccion" INTEGER,
	PRIMARY KEY("idEquipo", "idRefaccion")
);

CREATE TABLE "Archivo" (
	"idArchivo" SERIAL,
	"ruta" VARCHAR(255),
	"tipo" VARCHAR(50),
	"mime_type" VARCHAR(100),
	"idEquipoInstalado" INTEGER,
	"idOrden" INTEGER,
	"subidoPor" INTEGER,
	"fechaSubida" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"idMantenimiento" INTEGER,
	PRIMARY KEY("idArchivo")
);

CREATE TABLE "Notificacion" (
	"idNotificacion" SERIAL,
	"idUsuario" INTEGER,
	"mensaje" TEXT,
	"leida" BOOLEAN DEFAULT false,
	"fechaCreacion" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"tipo" VARCHAR(50),
	"referenciaId" INTEGER,
	PRIMARY KEY("idNotificacion")
);

ALTER TABLE "Usuario"
ADD FOREIGN KEY("idRol") REFERENCES "Rol"("idRol")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Usuario"
ADD FOREIGN KEY("idArea") REFERENCES "Area"("idArea")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EquipoInstalado"
ADD FOREIGN KEY("idEquipo") REFERENCES "Equipo"("idEquipo")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EquipoInstalado"
ADD FOREIGN KEY("idArea") REFERENCES "Area"("idArea")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EventoInventario"
ADD FOREIGN KEY("idEquipoInstalado") REFERENCES "EquipoInstalado"("idEquipoInstalado")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EventoInventario"
ADD FOREIGN KEY("idUsuario") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "OrdenTrabajo"
ADD FOREIGN KEY("idEquipoInstalado") REFERENCES "EquipoInstalado"("idEquipoInstalado")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "OrdenTrabajo"
ADD FOREIGN KEY("asignadoA") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "OrdenTrabajo"
ADD FOREIGN KEY("creadoPorUsuario") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "OrdenTrabajo"
ADD FOREIGN KEY("creadoPorExterno") REFERENCES "ContactoExterno"("idContactoExterno")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Mantenimiento"
ADD FOREIGN KEY("idOrden") REFERENCES "OrdenTrabajo"("idOrden")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Mantenimiento"
ADD FOREIGN KEY("realizadoPor") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Mantenimiento"
ADD FOREIGN KEY("verificadoPor") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "PlanMantenimiento"
ADD FOREIGN KEY("idEquipoInstalado") REFERENCES "EquipoInstalado"("idEquipoInstalado")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "StockRefaccion"
ADD FOREIGN KEY("idRefaccion") REFERENCES "Refaccion"("idRefaccion")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "CompraRefaccion"
ADD FOREIGN KEY("idRefaccion") REFERENCES "Refaccion"("idRefaccion")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "UsoRefaccion"
ADD FOREIGN KEY("idMantenimiento") REFERENCES "Mantenimiento"("idMantenimiento")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "UsoRefaccion"
ADD FOREIGN KEY("idRefaccion") REFERENCES "Refaccion"("idRefaccion")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EquipoRefaccion"
ADD FOREIGN KEY("idEquipo") REFERENCES "Equipo"("idEquipo")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EquipoRefaccion"
ADD FOREIGN KEY("idRefaccion") REFERENCES "Refaccion"("idRefaccion")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Archivo"
ADD FOREIGN KEY("idEquipoInstalado") REFERENCES "EquipoInstalado"("idEquipoInstalado")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Archivo"
ADD FOREIGN KEY("idOrden") REFERENCES "OrdenTrabajo"("idOrden")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Archivo"
ADD FOREIGN KEY("subidoPor") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Notificacion"
ADD FOREIGN KEY("idUsuario") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Archivo"
ADD FOREIGN KEY("idMantenimiento") REFERENCES "Mantenimiento"("idMantenimiento")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EquipoInstalado"
ADD FOREIGN KEY("idAdquisicion") REFERENCES "Adquisicion"("idAdquisicion")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "EquipoInstalado"
ADD FOREIGN KEY("dadoDeBajaPor") REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE "Mantenimiento"
ADD FOREIGN KEY("realizadoPorExterno") REFERENCES "ContactoExterno"("idContactoExterno")
ON UPDATE NO ACTION ON DELETE NO ACTION;

-- Tabla de sesion

CREATE TABLE "Sesion" (
	"idSesion" SERIAL PRIMARY KEY,
	"idUsuario" INTEGER NOT NULL,
	"token" TEXT NOT NULL,
	"fechaCreacion" TIMESTAMP NOT NULL DEFAULT NOW(),
	"ultimaActividad" TIMESTAMP NOT NULL DEFAULT NOW(),
	"expiraEn" TIMESTAMP NOT NULL,
	"activa" BOOLEAN NOT NULL DEFAULT TRUE,

	-- Auditoría
	"ipAddress" INET,
	"userAgent" TEXT,
	"dispositivo" VARCHAR(100),
	"fechaCierre" TIMESTAMP,

	-- Restricciones
	CONSTRAINT "uq_Sesion_token" UNIQUE ("token")
);

-- Claves foraneas
ALTER TABLE "Sesion"
ADD CONSTRAINT "fk_Sesion_Usuario"
FOREIGN KEY ("idUsuario")
REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION
ON DELETE NO ACTION;

-- Indices
CREATE INDEX "idx_Sesion_token"
ON "Sesion"("token");

CREATE INDEX "idx_Sesion_usuario"
ON "Sesion"("idUsuario");

CREATE INDEX "idx_Sesion_activa"
ON "Sesion"("activa");

-- test
-- INSERT INTO "Sesion" ("idUsuario", "token", "expiraEn")
-- VALUES (1, 'token_test', NOW() + INTERVAL '30 minutes');

-- Tabla de Logs

CREATE TABLE "LogActividad" (
    "idLog" SERIAL PRIMARY KEY,
    "idUsuario" INTEGER,
    "idSesion" INTEGER,
    "accion" VARCHAR(100) NOT NULL,
    "descripcion" TEXT,
    "ipAddress" INET,
    "userAgent" TEXT,
    "dispositivo" VARCHAR(100),
    "tipoEvento" VARCHAR(50),
    "fecha" TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Relaciones tabla de logs

ALTER TABLE "LogActividad"
ADD CONSTRAINT "fk_LogActividad_Usuario"
FOREIGN KEY ("idUsuario")
REFERENCES "Usuario"("idUsuario")
ON UPDATE NO ACTION
ON DELETE NO ACTION;

ALTER TABLE "LogActividad"
ADD CONSTRAINT "fk_LogActividad_Sesion"
FOREIGN KEY ("idSesion")
REFERENCES "Sesion"("idSesion")
ON UPDATE NO ACTION
ON DELETE NO ACTION;

-- indices

-- CREATE INDEX "idx_LogActividad_usuario" ON "LogActividad"("idUsuario");
-- CREATE INDEX "idx_LogActividad_sesion" ON "LogActividad"("idSesion");
-- CREATE INDEX "idx_LogActividad_fecha" ON "LogActividad"("fecha");
-- CREATE INDEX "idx_LogActividad_accion" ON "LogActividad"("accion");

-- TEST

-- LOGIN EXITOSO
-- INSERT INTO "LogActividad" (
--     "idUsuario",
--     "idSesion",
--     "accion",
--     "descripcion",
--     "ipAddress",
--     "userAgent",
--     "dispositivo",
--     "tipoEvento"
-- ) VALUES (
--     1,
--     4,
--     'LOGIN',
--     'Inicio de sesión exitoso',
--     '192.168.1.15',
--     'Mozilla/5.0 (X11; Linux; x64)',
--     'Desktop',
--     'SEGURIDAD'
-- );

-- -- LOGIN FALLIDO

-- INSERT INTO "LogActividad" (
--     "accion",
--     "descripcion",
--     "ipAddress",
--     "userAgent",
--     "dispositivo",
--     "tipoEvento"
-- ) VALUES (
--     'LOGIN_FAIL',
--     'Usuario o contraseña incorrecta',
--     '192.168.1.10',
--     'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
--     'Desktop',
--     'SEGURIDAD'
-- );

-- -- LOGOUT

-- INSERT INTO "LogActividad" (
--     "idUsuario",
--     "idSesion",
--     "accion",
--     "descripcion",
--     "tipoEvento"
-- ) VALUES (
--     1,
--     4,
--     'LOGOUT',
--     'Cierre de sesión',
--     'OPERACION'
-- );