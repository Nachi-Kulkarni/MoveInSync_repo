-- Movi Transport Agent Database Schema & Seed Data
-- SQLite database initialization script
-- Run with: sqlite3 database/transport.db < database/init.sql

-- Drop tables if they exist (for clean re-initialization)
DROP TABLE IF EXISTS agent_sessions;
DROP TABLE IF EXISTS deployments;
DROP TABLE IF EXISTS daily_trips;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS paths;
DROP TABLE IF EXISTS stops;

-- ============================================
-- SCHEMA DEFINITIONS
-- ============================================

-- Stops: Geographic locations for pickups/drop-offs
CREATE TABLE stops (
    stop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paths: Ordered sequences of stops
CREATE TABLE paths (
    path_id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_name TEXT NOT NULL UNIQUE,
    ordered_stop_ids TEXT NOT NULL,  -- JSON array: "[1,2,3]"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes: Path + Time combinations (static assets)
CREATE TABLE routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id INTEGER NOT NULL,
    route_display_name TEXT NOT NULL,  -- e.g., "Path2 - 19:45"
    shift_time TEXT NOT NULL,  -- e.g., "19:45"
    direction TEXT CHECK(direction IN ('LOGIN', 'LOGOUT')) NOT NULL,
    start_point TEXT NOT NULL,
    end_point TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'deactivated')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (path_id) REFERENCES paths(path_id)
);

-- Vehicles: Transport assets
CREATE TABLE vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_plate TEXT NOT NULL UNIQUE,
    type TEXT CHECK(type IN ('Bus', 'Cab')) NOT NULL,
    capacity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drivers: Human resources
CREATE TABLE drivers (
    driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily Trips: Daily instances of routes (dynamic operations)
CREATE TABLE daily_trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    display_name TEXT NOT NULL,  -- e.g., "Bulk - 00:01"
    booking_percentage INTEGER DEFAULT 0 CHECK(booking_percentage >= 0 AND booking_percentage <= 100),
    live_status TEXT,  -- e.g., "00:01 IN", "COMPLETED"
    trip_date DATE DEFAULT (date('now')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Deployments: Vehicle-Driver assignments to trips
CREATE TABLE deployments (
    deployment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES daily_trips(trip_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- Agent Sessions: Conversation state persistence (TICKET #5)
CREATE TABLE agent_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    page_context TEXT,
    conversation_history TEXT NOT NULL DEFAULT '[]',  -- JSON array
    current_state TEXT,  -- JSON object (AgentState)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    last_error TEXT
);

CREATE INDEX idx_agent_sessions_user_id ON agent_sessions(user_id);
CREATE INDEX idx_agent_sessions_is_active ON agent_sessions(is_active);

-- ============================================
-- SEED DATA
-- ============================================

-- Stops (8-10 stops matching assignment requirements)
INSERT INTO stops (name, latitude, longitude) VALUES
('Gavipuram', 12.9352, 77.5934),
('Peenya', 13.0358, 77.5200),
('Temple', 12.9716, 77.5946),
('BTM', 12.9165, 77.6101),
('Hebbal', 13.0358, 77.5971),
('Madiwala', 12.9141, 77.6237),
('Jayanagar', 12.9250, 77.5838),
('Koramangala', 12.9352, 77.6245),
('Electronic City', 12.8456, 77.6603),
('Whitefield', 12.9698, 77.7500);

-- Paths (3-4 paths with ordered stop sequences)
INSERT INTO paths (path_name, ordered_stop_ids) VALUES
('Path-1', '[1,3,5,7]'),  -- Gavipuram -> Temple -> Hebbal -> Jayanagar
('Path-2', '[2,4,6,8]'),  -- Peenya -> BTM -> Madiwala -> Koramangala
('Path-3', '[9,8,6,4]'),  -- Electronic City -> Koramangala -> Madiwala -> BTM
('Path-4', '[1,2,3,4]'); -- Gavipuram -> Peenya -> Temple -> BTM

-- Routes (10-15 routes derived from paths)
INSERT INTO routes (path_id, route_display_name, shift_time, direction, start_point, end_point, status) VALUES
(1, 'Path1 - 19:45', '19:45', 'LOGIN', 'Gavipuram', 'Jayanagar', 'active'),
(2, 'Path2 - 22:00', '22:00', 'LOGIN', 'Peenya', 'Koramangala', 'active'),
(3, 'Path3 - 20:00', '20:00', 'LOGIN', 'Electronic City', 'BTM', 'active'),
(1, 'Path1 - 19:00 (SN)', '19:00', 'LOGIN', 'Gavipuram', 'Jayanagar', 'active'),
(2, 'Path1 - 21:00', '21:00', 'LOGOUT', 'Jayanagar', 'Gavipuram', 'active'),
(1, 'Path1 - 17:00', '17:00', 'LOGIN', 'Gavipuram', 'Jayanagar', 'deactivated'),
(4, 'pathto - 03:00', '03:00', 'LOGIN', 'Gavipuram', 'BTM', 'active'),
(3, 'Path1 - 22:00', '22:00', 'LOGOUT', 'BTM', 'Electronic City', 'active'),
(2, 'Path1 - 20:00', '20:00', 'LOGIN', 'Peenya', 'Koramangala', 'active'),
(4, 'Ehco', '03:00', 'LOGOUT', 'BTM', 'Gavipuram', 'active'),
(1, 'Path1 - 00:02', '00:02', 'LOGIN', 'Gavipuram', 'Jayanagar', 'active'),
(2, 'Path2 - 00:03', '00:03', 'LOGIN', 'Peenya', 'Koramangala', 'active');

-- Vehicles (5-6 vehicles)
INSERT INTO vehicles (license_plate, type, capacity) VALUES
('KA-01-AB-1234', 'Bus', 40),
('KA-02-CD-5678', 'Bus', 35),
('KA-03-EF-9012', 'Cab', 7),
('MH-12-GH-3456', 'Cab', 6),
('TN-09-IJ-7890', 'Bus', 45),
('KA-05-KL-2468', 'Cab', 7);

-- Drivers (4-5 drivers)
INSERT INTO drivers (name, phone_number) VALUES
('Amit Kumar', '+91-9876543210'),
('Rajesh Sharma', '+91-9876543211'),
('Priya Patel', '+91-9876543212'),
('Suresh Reddy', '+91-9876543213'),
('Kavita Singh', '+91-9876543214');

-- Daily Trips (8-10 trips, including "Bulk - 00:01" from screenshot)
INSERT INTO daily_trips (route_id, display_name, booking_percentage, live_status) VALUES
(1, 'Bulk - 00:01', 25, '00:01 IN'),  -- Critical: 25% booked for consequence testing
(2, 'Path Path - 00:02', 0, '00:02 IN'),
(3, 'Path Path - 00:10', 0, '00:10 IN'),
(4, 'Ganmanu - 00:39', 0, '00:39 OUT'),
(5, 'ADX - 05:10', 0, '05:15 IN'),
(6, 'Hollilux - BTS - 17:00', 50, 'COMPLETED'),
(7, 'Path Path - 00:03', 10, '00:03 IN'),
(8, 'Tech Loop - 06:00', 0, 'SCHEDULED');

-- Deployments (3-4 deployments - some trips have vehicles, some don't)
INSERT INTO deployments (trip_id, vehicle_id, driver_id) VALUES
(1, 1, 1),  -- Bulk - 00:01 has a vehicle (important for consequence testing)
(6, 2, 2),  -- Hollilux trip
(7, 3, 3);  -- Path Path - 00:03

-- Trips 2, 3, 4, 5, 8 have NO deployments (vehicles not assigned)

-- ============================================
-- EXTENDED SEED DATA (20+ entries per table)
-- ============================================

-- Additional Stops (bringing total to 35+)
INSERT INTO stops (name, latitude, longitude) VALUES
-- Central Bangalore
('Indiranagar', 12.9716, 77.6412),
('MG Road Metro', 12.9758, 77.6065),
('Cunningham Road', 12.9965, 77.5936),
('Shivajinagar', 12.9810, 77.6040),
('Majestic', 12.9767, 77.5713),
('Marathahalli', 12.9591, 77.6970),

-- North Bangalore
('Yelahanka', 13.1007, 77.5963),
('Sahakara Nagar', 13.0382, 77.6177),
('RT Nagar', 13.0217, 77.5971),
('Nagawara', 13.0446, 77.6131),

-- South Bangalore
('JP Nagar', 12.9055, 77.5846),
('Bannerghatta Road', 12.8891, 77.6081),
('HSR Layout', 12.9121, 77.6446),
('Sarjapur Road', 12.9050, 77.6869),

-- East Bangalore
('Whitefield Main Road', 12.9698, 77.7499),
('Brookefield', 12.9610, 77.7130),
('KR Puram', 13.0050, 77.6960),
('Mahadevapura', 12.9919, 77.6971),

-- West Bangalore
('Rajajinagar', 12.9980, 77.5550),
('Basaveshwaranagar', 12.9854, 77.5398),
('Vijayanagar', 12.9716, 77.5350),
('Magadi Road', 12.9600, 77.5250),

-- Tech Parks & Business Hubs
('Manyata Tech Park', 13.0393, 77.6185),
('Bagmane Tech Park', 12.9850, 77.7250),
('Embassy Tech Village', 12.9950, 77.6980),
('RMZ Ecoworld', 12.9870, 77.6450);

-- Additional Paths (bringing total to 20+)
INSERT INTO paths (path_name, ordered_stop_ids) VALUES
-- Morning commute paths (LOGIN)
('Airport-Whitefield', '[17, 35, 10, 36, 26]'),
('Yelahanka-Manyata', '[17, 19, 33]'),
('Sarjapur-Electronic-City', '[24, 9, 26]'),
('Marathahalli-Koramangala', '[16, 23, 8]'),
('HSR-BTM', '[23, 4, 8]'),

-- Evening commute paths (LOGOUT)
('Whitefield-Airport', '[10, 36, 35, 17]'),
('Manyata-Yelahanka', '[33, 19, 17]'),
('Electronic-City-Sarjapur', '[9, 26, 24]'),
('Koramangala-Marathahalli', '[8, 23, 16]'),
('BTM-HSR', '[4, 23]'),

-- Cross-city paths
('North-South-Express', '[17, 13, 15, 1, 8, 21, 9]'),
('East-West-Corridor', '[10, 16, 11, 1, 2, 29, 30]'),
('Outer-Ring-Road', '[5, 16, 9, 24, 23, 4]'),
('Central-Business-District', '[13, 15, 11, 12]'),
('Tech-Park-Shuttle', '[33, 34, 35, 36]'),

-- Specialized routes
('Metro-Feeder-North', '[17, 18, 19, 20, 13]'),
('Metro-Feeder-South', '[21, 22, 8, 23]'),
('Night-Shift-Route', '[2, 10, 26, 34]'),
('Weekend-Special', '[1, 4, 8, 11, 12, 14]');

-- Additional Routes (bringing total to 45+)
INSERT INTO routes (path_id, route_display_name, shift_time, direction, start_point, end_point, status) VALUES
-- Morning shifts (06:00 - 10:00)
(5, 'Airport-WF 06:00', '06:00', 'LOGIN', 'Yelahanka', 'Whitefield', 'active'),
(5, 'Airport-WF 06:30', '06:30', 'LOGIN', 'Yelahanka', 'Whitefield', 'active'),
(6, 'Manyata 07:00', '07:00', 'LOGIN', 'Yelahanka', 'Manyata Tech Park', 'active'),
(6, 'Manyata 07:30', '07:30', 'LOGIN', 'Yelahanka', 'Manyata Tech Park', 'active'),
(7, 'Sarjapur 08:00', '08:00', 'LOGIN', 'Sarjapur Road', 'Electronic City', 'active'),
(7, 'Sarjapur 08:30', '08:30', 'LOGIN', 'Sarjapur Road', 'Electronic City', 'active'),
(8, 'Marathahalli 09:00', '09:00', 'LOGIN', 'Marathahalli', 'Koramangala', 'active'),
(8, 'Marathahalli 09:30', '09:30', 'LOGIN', 'Marathahalli', 'Koramangala', 'active'),
(9, 'HSR-BTM 09:45', '09:45', 'LOGIN', 'HSR Layout', 'BTM', 'active'),

-- Mid-day shifts (10:00 - 16:00)
(13, 'CBD 10:30', '10:30', 'LOGIN', 'Shivajinagar', 'Majestic', 'active'),
(14, 'Outer Ring 11:00', '11:00', 'LOGIN', 'Hebbal', 'BTM', 'active'),
(15, 'Tech Shuttle 12:00', '12:00', 'LOGOUT', 'Manyata Tech Park', 'Bagmane Tech Park', 'active'),
(16, 'Metro North 13:00', '13:00', 'LOGIN', 'Yelahanka', 'Shivajinagar', 'active'),
(17, 'Metro South 14:00', '14:00', 'LOGOUT', 'Bannerghatta Road', 'HSR Layout', 'active'),

-- Evening shifts (16:00 - 21:00)
(10, 'WF-Airport 16:30', '16:30', 'LOGOUT', 'Whitefield', 'Yelahanka', 'active'),
(10, 'WF-Airport 17:00', '17:00', 'LOGOUT', 'Whitefield', 'Yelahanka', 'active'),
(11, 'Manyata Return 17:30', '17:30', 'LOGOUT', 'Manyata Tech Park', 'Yelahanka', 'active'),
(11, 'Manyata Return 18:00', '18:00', 'LOGOUT', 'Manyata Tech Park', 'Yelahanka', 'active'),
(12, 'EC-Sarjapur 18:30', '18:30', 'LOGOUT', 'Electronic City', 'Sarjapur Road', 'active'),
(12, 'EC-Sarjapur 19:00', '19:00', 'LOGOUT', 'Electronic City', 'Sarjapur Road', 'active'),
(13, 'Koramangala 19:30', '19:30', 'LOGOUT', 'Koramangala', 'Marathahalli', 'active'),
(14, 'BTM-HSR 20:00', '20:00', 'LOGOUT', 'BTM', 'HSR Layout', 'active'),

-- Night shifts (21:00 - 06:00)
(18, 'Night Owl 22:00', '22:00', 'LOGOUT', 'Peenya', 'Electronic City', 'active'),
(18, 'Late Night 23:30', '23:30', 'LOGOUT', 'Peenya', 'Electronic City', 'active'),
(18, 'Graveyard 01:00', '01:00', 'LOGIN', 'Peenya', 'Electronic City', 'active'),
(18, 'Early Morning 03:00', '03:00', 'LOGOUT', 'Peenya', 'Electronic City', 'active'),

-- Weekend routes
(19, 'Weekend AM 08:00', '08:00', 'LOGIN', 'Gavipuram', 'Majestic', 'active'),
(19, 'Weekend Brunch 10:00', '10:00', 'LOGIN', 'Gavipuram', 'Majestic', 'active'),
(19, 'Weekend PM 14:00', '14:00', 'LOGOUT', 'Majestic', 'Gavipuram', 'active'),
(19, 'Weekend Evening 18:00', '18:00', 'LOGOUT', 'Majestic', 'Gavipuram', 'active'),

-- Tech park shuttles
(15, 'Tech Shuttle 08:15', '08:15', 'LOGIN', 'Manyata Tech Park', 'Bagmane Tech Park', 'active'),
(15, 'Tech Shuttle 08:45', '08:45', 'LOGIN', 'Manyata Tech Park', 'Bagmane Tech Park', 'active'),
(15, 'Tech Return 17:45', '17:45', 'LOGOUT', 'Bagmane Tech Park', 'Manyata Tech Park', 'active'),
(15, 'Tech Return 18:15', '18:15', 'LOGOUT', 'Bagmane Tech Park', 'Manyata Tech Park', 'active');

-- Additional Vehicles (bringing total to 25+)
INSERT INTO vehicles (license_plate, type, capacity) VALUES
-- Buses (Large capacity)
('KA-01-BB-1111', 'Bus', 45),
('KA-01-BB-2222', 'Bus', 45),
('KA-01-BB-3333', 'Bus', 40),
('KA-01-BB-4444', 'Bus', 40),
('KA-02-BB-5555', 'Bus', 50),
('KA-02-BB-6666', 'Bus', 50),
('KA-03-BB-7777', 'Bus', 42),
('KA-03-BB-8888', 'Bus', 42),
('TN-01-BB-9999', 'Bus', 48),
('TN-02-BB-1010', 'Bus', 48),

-- Mini Buses (Medium capacity)
('KA-04-MB-1212', 'Bus', 25),
('KA-04-MB-1313', 'Bus', 25),
('KA-05-MB-1414', 'Bus', 28),
('KA-05-MB-1515', 'Bus', 28),
('MH-01-MB-1616', 'Bus', 30),

-- Cabs (Small capacity)
('KA-06-CC-1717', 'Cab', 6),
('KA-06-CC-1818', 'Cab', 6),
('KA-07-CC-1919', 'Cab', 7),
('KA-07-CC-2020', 'Cab', 7),
('MH-02-CC-2121', 'Cab', 6);

-- Additional Drivers (bringing total to 25+)
INSERT INTO drivers (name, phone_number) VALUES
-- Senior drivers
('Rajesh Kumar', '+91-9876543215'),
('Suresh Patel', '+91-9876543216'),
('Mahesh Reddy', '+91-9876543217'),
('Ganesh Iyer', '+91-9876543218'),
('Ramesh Nair', '+91-9876543219'),

-- Experienced drivers
('Prakash Rao', '+91-9876543220'),
('Dinesh Shah', '+91-9876543221'),
('Anil Varma', '+91-9876543222'),
('Sunil Gupta', '+91-9876543223'),
('Mukesh Jain', '+91-9876543224'),

-- Mid-level drivers
('Vijay Singh', '+91-9876543225'),
('Ajay Sharma', '+91-9876543226'),
('Sanjay Verma', '+91-9876543227'),
('Manoj Desai', '+91-9876543228'),
('Ashok Menon', '+91-9876543229'),

-- Junior drivers
('Ravi Krishnan', '+91-9876543230'),
('Kiran Hegde', '+91-9876543231'),
('Naveen Bhat', '+91-9876543232'),
('Praveen Shetty', '+91-9876543233'),
('Deepak Kamath', '+91-9876543234');

-- Additional Daily Trips (bringing total to 30+)
INSERT INTO daily_trips (route_id, display_name, booking_percentage, live_status) VALUES
-- Morning trips (High booking)
(13, 'Airport Express 06:00', 85, 'Scheduled'),
(14, 'Airport Express 06:30', 90, 'Scheduled'),
(15, 'Manyata Shuttle 07:00', 75, 'Scheduled'),
(16, 'Manyata Shuttle 07:30', 80, 'Scheduled'),
(17, 'Sarjapur Run 08:00', 70, 'Scheduled'),
(18, 'Sarjapur Run 08:30', 65, 'Scheduled'),
(19, 'Marathahalli Express 09:00', 55, 'Scheduled'),
(20, 'Marathahalli Express 09:30', 60, 'Scheduled'),
(21, 'HSR-BTM 09:45', 50, 'Scheduled'),

-- Mid-day trips (Medium booking)
(22, 'CBD Shuttle 10:30', 40, 'Scheduled'),
(23, 'Outer Ring 11:00', 35, 'Scheduled'),
(24, 'Tech Shuttle 12:00', 45, 'Scheduled'),
(25, 'Metro North 13:00', 50, 'Scheduled'),
(26, 'Metro South 14:00', 42, 'Scheduled'),

-- Evening trips (Very high booking)
(27, 'Evening Rush 16:30', 95, 'Scheduled'),
(28, 'Evening Rush 17:00', 98, 'Scheduled'),
(29, 'Manyata Return 17:30', 88, 'Scheduled'),
(30, 'Manyata Return 18:00', 92, 'Scheduled'),
(31, 'EC-Sarjapur 18:30', 78, 'Scheduled'),
(32, 'EC-Sarjapur 19:00', 72, 'Scheduled'),

-- Night trips (Low booking)
(35, 'Night Owl 22:00', 25, 'Scheduled'),
(36, 'Late Night 23:30', 15, 'Scheduled'),
(37, 'Graveyard 01:00', 10, 'Scheduled');

-- Additional Deployments (bringing total to 25+)
INSERT INTO deployments (trip_id, vehicle_id, driver_id) VALUES
-- Morning trips deployments
(9, 7, 6),   -- Airport Express 06:00
(10, 8, 7),  -- Airport Express 06:30
(11, 9, 8),  -- Manyata Shuttle 07:00
(12, 10, 9), -- Manyata Shuttle 07:30
(13, 11, 10), -- Sarjapur Run 08:00
(14, 12, 11), -- Sarjapur Run 08:30
(15, 13, 12), -- Marathahalli Express 09:00
(16, 14, 13), -- Marathahalli Express 09:30
(17, 15, 14), -- HSR-BTM 09:45

-- Mid-day trips deployments
(18, 16, 15), -- CBD Shuttle 10:30
(19, 17, 16), -- Outer Ring 11:00
(20, 18, 17), -- Tech Shuttle 12:00
(21, 19, 18), -- Metro North 13:00
(22, 20, 19), -- Metro South 14:00

-- Evening trips deployments
(23, 21, 20), -- Evening Rush 16:30
(24, 5, 21),  -- Evening Rush 17:00 (original vehicle)
(25, 22, 22), -- Manyata Return 17:30
(26, 23, 23), -- Manyata Return 18:00
(27, 24, 24), -- EC-Sarjapur 18:30
(28, 25, 25); -- EC-Sarjapur 19:00

-- ============================================
-- VERIFICATION QUERIES (for testing)
-- ============================================

-- Uncomment to verify data after initialization:
-- SELECT 'Stops:', COUNT(*) FROM stops;
-- SELECT 'Paths:', COUNT(*) FROM paths;
-- SELECT 'Routes:', COUNT(*) FROM routes;
-- SELECT 'Vehicles:', COUNT(*) FROM vehicles;
-- SELECT 'Drivers:', COUNT(*) FROM drivers;
-- SELECT 'Daily Trips:', COUNT(*) FROM daily_trips;
-- SELECT 'Deployments:', COUNT(*) FROM deployments;
--
-- -- Show trips with their deployment status:
-- SELECT
--     dt.display_name,
--     dt.booking_percentage,
--     CASE WHEN d.deployment_id IS NOT NULL THEN 'Assigned' ELSE 'Unassigned' END as vehicle_status
-- FROM daily_trips dt
-- LEFT JOIN deployments d ON dt.trip_id = d.trip_id;
