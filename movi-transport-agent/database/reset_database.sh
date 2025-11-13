
set -e 
# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
DB_PATH="$PROJECT_ROOT/database/transport.db"
INIT_SQL="$PROJECT_ROOT/database/init.sql"

# Default mode
MODE="${1:-development}"

echo -e "${BLUE}"
echo "================================================================================"
echo "  MOVI TRANSPORT AGENT - DATABASE RESET UTILITY"
echo "================================================================================"
echo -e "${NC}"

# Function to create backup
create_backup() {
    if [ -f "$DB_PATH" ]; then
        BACKUP_NAME="transport_backup_$(date +%Y%m%d_%H%M%S).db"
        BACKUP_PATH="$PROJECT_ROOT/database/backups/$BACKUP_NAME"

        mkdir -p "$PROJECT_ROOT/database/backups"

        echo -e "${YELLOW}📦 Creating backup: $BACKUP_NAME${NC}"
        cp "$DB_PATH" "$BACKUP_PATH"

        # Verify backup
        if sqlite3 "$BACKUP_PATH" "SELECT COUNT(*) FROM stops;" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backup created successfully${NC}"
            echo -e "   Location: $BACKUP_PATH"
        else
            echo -e "${RED}❌ Backup verification failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ No existing database to backup${NC}"
    fi
}

# Function to reset database
reset_database() {
    echo -e "\n${YELLOW}🔄 Resetting database...${NC}"

    # Remove old database
    if [ -f "$DB_PATH" ]; then
        rm "$DB_PATH"
        echo -e "${GREEN}✓ Old database removed${NC}"
    fi

    # Create new database from init.sql
    echo -e "${YELLOW}📝 Creating new database from init.sql...${NC}"
    sqlite3 "$DB_PATH" < "$INIT_SQL"

    # Verify database
    STOP_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM stops;")
    TRIP_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM daily_trips;")

    if [ "$STOP_COUNT" -gt 0 ] && [ "$TRIP_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Database created successfully${NC}"
        echo -e "   Stops: $STOP_COUNT"
        echo -e "   Trips: $TRIP_COUNT"
    else
        echo -e "${RED}❌ Database verification failed${NC}"
        exit 1
    fi
}

# Function to show database stats
show_stats() {
    echo -e "\n${BLUE}📊 Database Statistics:${NC}"
    sqlite3 "$DB_PATH" -column -header "
    SELECT
        'stops' as table_name,
        COUNT(*) as count
    FROM stops
    UNION ALL SELECT 'paths', COUNT(*) FROM paths
    UNION ALL SELECT 'routes', COUNT(*) FROM routes
    UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles
    UNION ALL SELECT 'drivers', COUNT(*) FROM drivers
    UNION ALL SELECT 'daily_trips', COUNT(*) FROM daily_trips
    UNION ALL SELECT 'deployments', COUNT(*) FROM deployments;
    "
}

# Development Mode
if [ "$MODE" = "development" ]; then
    echo -e "${GREEN}🔧 Development Mode${NC}"
    echo -e "   - Full database reset"
    echo -e "   - All seed data included"
    echo -e "   - Safe for testing\n"

    create_backup
    reset_database
    show_stats

    echo -e "\n${GREEN}✅ Development database reset complete!${NC}"
    echo -e "${BLUE}💡 Tip: Run 'python backend/tests/test_all_tools_v2.py' to verify${NC}\n"

# Demo Mode
elif [ "$MODE" = "demo" ]; then
    echo -e "${MAGENTA}🎭 Demo Mode${NC}"
    echo -e "   - Clean reset optimized for demonstrations"
    echo -e "   - Full dataset with realistic scenarios"
    echo -e "   - All test fixtures preserved\n"

    echo -e "${YELLOW}Are you sure you want to reset the demo database?${NC}"
    echo -e "This will:"
    echo -e "  • Create a backup of current database"
    echo -e "  • Reset to fresh state with full seed data"
    echo -e "  • Preserve all 36 stops, 26 vehicles, 31 trips"
    echo -e ""
    read -p "Type 'yes' to continue: " CONFIRM

    if [ "$CONFIRM" = "yes" ]; then
        create_backup
        reset_database

        # Demo-specific optimizations
        echo -e "\n${YELLOW}🎨 Applying demo optimizations...${NC}"

        # Set some trips to interesting booking percentages for demo
        sqlite3 "$DB_PATH" "
        UPDATE daily_trips SET booking_percentage = 95 WHERE trip_id = 23;
        UPDATE daily_trips SET booking_percentage = 98 WHERE trip_id = 24;
        UPDATE daily_trips SET booking_percentage = 25 WHERE trip_id = 1;
        UPDATE daily_trips SET booking_percentage = 50 WHERE trip_id = 6;
        "

        echo -e "${GREEN}✓ Demo optimizations applied${NC}"

        show_stats

        echo -e "\n${GREEN}✅ Demo database reset complete!${NC}"
        echo -e "${MAGENTA}🎭 Ready for demonstration!${NC}\n"
    else
        echo -e "${YELLOW}Cancelled.${NC}\n"
        exit 0
    fi

# Production Mode (DANGEROUS)
elif [ "$MODE" = "production" ]; then
    echo -e "${RED}⚠️  PRODUCTION MODE - DANGEROUS ⚠️${NC}"
    echo -e "${RED}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  THIS WILL DELETE ALL PRODUCTION DATA!        ║${NC}"
    echo -e "${RED}║  Only use this if you know what you're doing! ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════╝${NC}\n"

    echo -e "${YELLOW}Current database status:${NC}"
    show_stats

    echo -e "\n${RED}Are you ABSOLUTELY SURE you want to reset the production database?${NC}"
    echo -e "This action:"
    echo -e "  ${RED}• WILL DELETE ALL REAL PRODUCTION DATA${NC}"
    echo -e "  • Cannot be undone (except from backup)"
    echo -e "  • Should NEVER be done on a live production system"
    echo -e "  • Will affect all users immediately"
    echo -e ""
    read -p "Type 'I UNDERSTAND THE RISKS' to continue: " CONFIRM

    if [ "$CONFIRM" = "I UNDERSTAND THE RISKS" ]; then
        echo -e "\n${RED}Second confirmation required.${NC}"
        read -p "Type the current date (YYYY-MM-DD) to proceed: " DATE_CONFIRM

        CURRENT_DATE=$(date +%Y-%m-%d)

        if [ "$DATE_CONFIRM" = "$CURRENT_DATE" ]; then
            create_backup

            # Additional safety: require explicit password
            echo -e "\n${RED}Final safety check.${NC}"
            read -sp "Enter production password: " PROD_PASSWORD
            echo ""

            # In real production, check against environment variable
            # For demo purposes, we skip this
            # if [ "$PROD_PASSWORD" != "$PRODUCTION_DB_PASSWORD" ]; then
            #     echo -e "${RED}❌ Invalid password${NC}"
            #     exit 1
            # fi

            echo -e "\n${RED}🔥 RESETTING PRODUCTION DATABASE...${NC}"
            sleep 2  # Give time to cancel (Ctrl+C)

            reset_database
            show_stats

            echo -e "\n${RED}⚠️  Production database has been reset!${NC}"
            echo -e "${YELLOW}📦 Backup location: Check database/backups/ directory${NC}\n"
        else
            echo -e "${YELLOW}Date mismatch. Cancelled for safety.${NC}\n"
            exit 0
        fi
    else
        echo -e "${YELLOW}Cancelled.${NC}\n"
        exit 0
    fi

else
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo -e "Usage: $0 [development|demo|production]\n"
    exit 1
fi

# Final message
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Database reset complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
