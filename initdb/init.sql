-- สร้างตารางผู้ใช้ (users)
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL
);

-- สร้างตารางบันทึกไดอารี่ (diary)
CREATE TABLE IF NOT EXISTS diary (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    sentiment VARCHAR(3) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email)
);
