from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.users import migrate_users_from_file
from app.services.user_service import register_user, login_user
from app.data.incidents import (
    load_csv_to_table, insert_incident, get_all_incidents, 
    update_incident_status, delete_incident, get_incidents_by_type_count
)

