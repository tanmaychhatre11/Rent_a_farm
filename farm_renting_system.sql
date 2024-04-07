-- Table structure for table farms
CREATE TABLE IF NOT EXISTS farms (
  id INTEGER PRIMARY KEY,
  owner_id INTEGER,
  name TEXT,
  location TEXT,
  size INTEGER,
  price INTEGER
);
  
-- Table structure for table users
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT,
  password TEXT,
  full_name TEXT,
  email TEXT,
  contact_number TEXT,
  address TEXT,
  type TEXT
);
