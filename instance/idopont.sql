PRAGMA foreign_keys = ON;

CREATE TABLE user (
    id              INTEGER PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    name            TEXT NOT NULL,
    phone           TEXT,
    role            TEXT NOT NULL CHECK (role IN ('ADMIN','DOCTOR','PATIENT')),
    active          INTEGER NOT NULL DEFAULT 1,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patient (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE,
    taj         TEXT,            -- TAJ equivalent
    note        TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE doctor (
    id              INTEGER PRIMARY KEY,
    user_id         INTEGER NOT NULL UNIQUE,
    license_number  TEXT,        -- pecset_szam
    bio             TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE clinic (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    address     TEXT NOT NULL,
    floor_room  TEXT
);

CREATE TABLE service (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    base_duration_min   INTEGER NOT NULL,
    base_price          INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE doctor_service (
    doctor_id       INTEGER NOT NULL,
    service_id      INTEGER NOT NULL,
    price           INTEGER,
    duration_min    INTEGER,
    PRIMARY KEY (doctor_id, service_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctor(id)   ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(id)  ON DELETE RESTRICT
);

CREATE TABLE slot (
    id          INTEGER PRIMARY KEY,
    doctor_id   INTEGER NOT NULL,
    clinic_id   INTEGER,
    starts_at   DATETIME NOT NULL,
    ends_at     DATETIME NOT NULL,
    state       TEXT NOT NULL DEFAULT 'FREE',
    UNIQUE (doctor_id, starts_at, ends_at),
    FOREIGN KEY (doctor_id) REFERENCES doctor(id)   ON DELETE CASCADE,
    FOREIGN KEY (clinic_id) REFERENCES clinic(id)
);

CREATE TABLE booking (
    id              INTEGER PRIMARY KEY,
    slot_id         INTEGER NOT NULL UNIQUE,
    patient_id      INTEGER NOT NULL,
    service_id      INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'NEW',
    note            TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (slot_id)    REFERENCES slot(id)       ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patient(id)    ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(id)    ON DELETE RESTRICT
);

CREATE INDEX idx_slot_doctor_start    ON slot(doctor_id, starts_at);
CREATE INDEX idx_booking_patient      ON booking(patient_id, created_at);
CREATE INDEX idx_doctor_service_svc   ON doctor_service(service_id);
