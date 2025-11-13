# Movi Transport Agent - Database Summary

## Overview

The database has been populated with comprehensive realistic Bangalore transport data covering all major areas, routes, and operational scenarios.

## Final Database Counts

| Table | Count | Target | Status |
|-------|-------|--------|--------|
| **Stops** | 36 | 20+ | ✅ |
| **Paths** | 23 | 20+ | ✅ |
| **Routes** | 46 | 20+ | ✅ |
| **Vehicles** | 26 | 20+ | ✅ |
| **Drivers** | 25 | 20+ | ✅ |
| **Daily Trips** | 31 | 20+ | ✅ |
| **Deployments** | 23 | 20+ | ✅ |

## Geographic Coverage

### Stops (36 locations)

#### **Original Stops (10)**
1. Gavipuram
2. Peenya
3. Temple
4. BTM
5. Hebbal
6. Madiwala
7. Jayanagar
8. Koramangala
9. Electronic City
10. Whitefield

#### **Additional Stops (26)**

**Central Bangalore (6)**
- Indiranagar
- MG Road Metro
- Cunningham Road
- Shivajinagar
- Majestic
- Marathahalli

**North Bangalore (4)**
- Yelahanka
- Sahakara Nagar
- RT Nagar
- Nagawara

**South Bangalore (4)**
- JP Nagar
- Bannerghatta Road
- HSR Layout
- Sarjapur Road

**East Bangalore (4)**
- Whitefield Main Road
- Brookefield
- KR Puram
- Mahadevapura

**West Bangalore (4)**
- Rajajinagar
- Basaveshwaranagar
- Vijayanagar
- Magadi Road

**Tech Parks & Business Hubs (4)**
- Manyata Tech Park
- Bagmane Tech Park
- Embassy Tech Village
- RMZ Ecoworld

## Path Categories

### Paths (23 total)

#### **Original Paths (4)**
1. Path1 - Gavipuram → Temple → Hebbal → Jayanagar
2. Path2 - Peenya → BTM → Madiwala → Koramangala
3. Path3 - Electronic City → Koramangala → Madiwala → BTM
4. pathto - Gavipuram → Peenya → Temple → BTM

#### **Morning Commute Paths (5)**
- Airport-Whitefield
- Yelahanka-Manyata
- Sarjapur-Electronic-City
- Marathahalli-Koramangala
- HSR-BTM

#### **Evening Commute Paths (5)**
- Whitefield-Airport
- Manyata-Yelahanka
- Electronic-City-Sarjapur
- Koramangala-Marathahalli
- BTM-HSR

#### **Cross-City Paths (5)**
- North-South-Express (7 stops)
- East-West-Corridor (7 stops)
- Outer-Ring-Road (6 stops)
- Central-Business-District (4 stops)
- Tech-Park-Shuttle (4 tech parks)

#### **Specialized Routes (4)**
- Metro-Feeder-North (5 stops)
- Metro-Feeder-South (4 stops)
- Night-Shift-Route (4 stops)
- Weekend-Special (6 stops)

## Routes Distribution

### Routes (46 total)

| Time Period | Count | Description |
|-------------|-------|-------------|
| **Morning (06:00-10:00)** | 12 | High capacity buses for rush hour |
| **Mid-day (10:00-16:00)** | 8 | Medium capacity vehicles |
| **Evening (16:00-21:00)** | 12 | Very high capacity for evening rush |
| **Night (21:00-06:00)** | 6 | Small capacity cabs |
| **Weekend** | 4 | Variable capacity based on demand |
| **Original** | 4 | Legacy routes from initial seed |

### Route Breakdown by Direction

- **LOGIN routes**: 24 (morning commute to work/school)
- **LOGOUT routes**: 22 (evening return home)

## Vehicle Fleet

### Vehicles (26 total)

| Type | Count | Capacity Range | Use Case |
|------|-------|----------------|----------|
| **Large Buses** | 14 | 40-50 seats | Morning/evening rush hours |
| **Mini Buses** | 5 | 25-30 seats | Mid-day shuttles |
| **Cabs** | 7 | 6-7 seats | Night shifts, low demand |

**Sample Vehicle IDs:**
- KA-01-AB-1234 (Bus, 40 seats) - Original test vehicle
- KA-02-CD-5678 (Bus, 35 seats) - Used for Test #17
- MH-12-GH-3456 (Cab, 6 seats) - Used for Test #10
- KA-01-BB-1111 through TN-02-BB-1010 (Large buses)
- KA-04-MB-1212 through MH-01-MB-1616 (Mini buses)
- KA-06-CC-1717 through MH-02-CC-2121 (Cabs)

## Driver Pool

### Drivers (25 total)

| Experience Level | Count | Shift Assignment |
|------------------|-------|------------------|
| **Senior Drivers** | 5 | Critical morning routes |
| **Experienced** | 5 | High-demand routes |
| **Mid-level** | 5 | Regular routes |
| **Junior** | 5 | Backup and support |
| **Original** | 5 | Test scenarios |

**Note:** All drivers have unique phone numbers (+91-987654321X format)

## Daily Trips Distribution

### Daily Trips (31 total)

| Booking Range | Count | Status | Priority |
|---------------|-------|--------|----------|
| **90-100%** | 2 | Very High Demand | Critical |
| **70-89%** | 6 | High Demand | High |
| **50-69%** | 5 | Medium Demand | Medium |
| **25-49%** | 4 | Low-Medium | Normal |
| **0-24%** | 14 | Low Demand | Low |

### Booking Percentage Examples:
- **Evening Rush 17:00**: 98% (Critical - needs largest bus)
- **Evening Rush 16:30**: 95% (Critical)
- **Manyata Return 18:00**: 92% (High)
- **Airport Express 06:30**: 90% (High)
- **Bulk - 00:01**: 25% (Test fixture for consequence flow)
- **Graveyard 01:00**: 10% (Night shift - cab sufficient)

## Deployments

### Vehicle-Driver Assignments (23 total)

| Shift Period | Deployments | Deployment Rate |
|--------------|-------------|-----------------|
| **Morning (06:00-10:00)** | 9 | 100% of morning trips |
| **Mid-day (10:00-16:00)** | 5 | 100% of mid-day trips |
| **Evening (16:00-21:00)** | 6 | 100% of evening trips |
| **Night (21:00-06:00)** | 0 | Pending assignment |
| **Original** | 3 | Test fixtures |

**Unassigned Trips**: 8 trips have no vehicle/driver assignments (available for testing assignment operations)

## Data Characteristics

### Realistic Scenarios

1. **Peak Hours**: Morning (07:00-09:00) and Evening (17:00-19:00) have highest bookings
2. **Off-Peak**: Mid-day and night have lower bookings
3. **Weekend**: Special routes with moderate bookings
4. **Tech Park Shuttles**: Dedicated routes for IT corridors
5. **Metro Feeders**: Last-mile connectivity routes

### Test-Friendly Features

1. **Multiple Booking Percentages**: From 0% to 98% for consequence testing
2. **Unassigned Vehicles**: Several vehicles available for assignment tests
3. **Unassigned Trips**: Several trips without vehicles for testing
4. **Original Test Data**: Preserved "Bulk - 00:01" at 25% for existing tests
5. **Vehicle Variety**: Mix of buses and cabs for different scenarios

## Database Schema

```sql
stops (36 rows)
├── stop_id (PK)
├── name (UNIQUE)
├── latitude, longitude
└── created_at

paths (23 rows)
├── path_id (PK)
├── path_name (UNIQUE)
├── ordered_stop_ids (JSON array)
└── created_at

routes (46 rows)
├── route_id (PK)
├── path_id (FK)
├── route_display_name
├── shift_time
├── direction (LOGIN/LOGOUT)
├── start_point, end_point
├── status (active/deactivated)
└── created_at

vehicles (26 rows)
├── vehicle_id (PK)
├── license_plate (UNIQUE)
├── type (Bus/Cab)
├── capacity
└── created_at

drivers (25 rows)
├── driver_id (PK)
├── name
├── phone_number
└── created_at

daily_trips (31 rows)
├── trip_id (PK)
├── route_id (FK)
├── display_name
├── booking_percentage (0-100)
├── live_status
├── trip_date
└── created_at

deployments (23 rows)
├── deployment_id (PK)
├── trip_id (FK)
├── vehicle_id (FK)
├── driver_id (FK)
└── deployed_at
```

## Usage Examples

### Query All Morning Trips
```sql
SELECT dt.display_name, dt.booking_percentage, r.shift_time
FROM daily_trips dt
JOIN routes r ON dt.route_id = r.route_id
WHERE r.shift_time BETWEEN '06:00' AND '10:00'
ORDER BY r.shift_time;
```

### Find Unassigned Vehicles
```sql
SELECT v.vehicle_id, v.license_plate, v.type, v.capacity
FROM vehicles v
LEFT JOIN deployments d ON v.vehicle_id = d.vehicle_id
WHERE d.deployment_id IS NULL;
```

### High-Risk Trips (70%+ booking)
```sql
SELECT dt.display_name, dt.booking_percentage, v.license_plate
FROM daily_trips dt
LEFT JOIN deployments d ON dt.trip_id = d.trip_id
LEFT JOIN vehicles v ON d.vehicle_id = v.vehicle_id
WHERE dt.booking_percentage >= 70
ORDER BY dt.booking_percentage DESC;
```

### Trips by Geographic Area
```sql
SELECT dt.display_name, r.start_point, r.end_point, r.shift_time
FROM daily_trips dt
JOIN routes r ON dt.route_id = r.route_id
WHERE r.start_point LIKE '%Tech Park%' OR r.end_point LIKE '%Tech Park%';
```

## Verification Commands

```bash
# Count all tables
sqlite3 database/transport.db "
SELECT 'stops' as table_name, COUNT(*) as count FROM stops
UNION ALL SELECT 'paths', COUNT(*) FROM paths
UNION ALL SELECT 'routes', COUNT(*) FROM routes
UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL SELECT 'drivers', COUNT(*) FROM drivers
UNION ALL SELECT 'daily_trips', COUNT(*) FROM daily_trips
UNION ALL SELECT 'deployments', COUNT(*) FROM deployments;
"

# View sample data
sqlite3 database/transport.db -header -column "SELECT * FROM stops LIMIT 10;"
sqlite3 database/transport.db -header -column "SELECT * FROM vehicles LIMIT 10;"
sqlite3 database/transport.db -header -column "SELECT * FROM daily_trips LIMIT 10;"

# View deployment status
sqlite3 database/transport.db -header -column "
SELECT dt.display_name, dt.booking_percentage,
       CASE WHEN d.deployment_id IS NOT NULL THEN 'Assigned' ELSE 'Unassigned' END as status
FROM daily_trips dt
LEFT JOIN deployments d ON dt.trip_id = d.trip_id
ORDER BY dt.booking_percentage DESC;
"
```

## Maintenance

### Backup Database
```bash
cp database/transport.db database/transport_backup_$(date +%Y%m%d).db
```

### Reset to Clean State
```bash
rm database/transport.db
sqlite3 database/transport.db < database/init.sql
```

### Add More Data
Edit `database/init.sql` and add new INSERT statements in the "EXTENDED SEED DATA" section, then recreate:
```bash
rm database/transport.db
sqlite3 database/transport.db < database/init.sql
```

## Notes

1. **Test Compatibility**: All original test data preserved for backward compatibility
2. **Realistic Data**: Based on actual Bangalore geography and traffic patterns
3. **Scalability**: Structure supports adding more stops, routes, and vehicles
4. **Foreign Keys**: Properly enforced relationships between tables
5. **Timestamps**: All tables have created_at/deployed_at for audit trail

## Summary

✅ **36 stops** covering all major Bangalore areas
✅ **23 paths** for various commute scenarios
✅ **46 routes** distributed across morning/evening/night shifts
✅ **26 vehicles** (buses and cabs) with realistic capacities
✅ **25 drivers** across all experience levels
✅ **31 daily trips** with booking percentages from 0-98%
✅ **23 deployments** linking vehicles/drivers to trips

**Total database size**: ~150KB (SQLite file)
**Total records**: 210+ across all tables
**Ready for**: Development, testing, and agent training
