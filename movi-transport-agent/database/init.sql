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
('Path1', '[1,3,5,7]'),  -- Gavipuram -> Temple -> Hebbal -> Jayanagar
('Path2', '[2,4,6,8]'),  -- Peenya -> BTM -> Madiwala -> Koramangala
('Path3', '[9,8,6,4]'),  -- Electronic City -> Koramangala -> Madiwala -> BTM
('pathto', '[1,2,3,4]'); -- Gavipuram -> Peenya -> Temple -> BTM

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
