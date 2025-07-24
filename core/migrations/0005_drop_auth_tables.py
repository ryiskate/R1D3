from django.db import migrations

class Migration(migrations.Migration):
    """
    Custom migration to drop specific auth-related tables.
    This migration will drop the following tables:
    - account_emailaddress
    - account_emailconfirmation
    - auth_group
    - auth_group_permissions
    - auth_permission
    - auth_user_groups
    - auth_user_user_permissions
    - core_profile
    """

    dependencies = [
        ('core', '0002_quicklink'),  # Update this to match your last core migration
    ]

    operations = [
        # Simply drop the tables with foreign key checks disabled
        migrations.RunSQL(
            sql="""
            SET FOREIGN_KEY_CHECKS = 0;
            
            -- Drop tables that might have foreign key relationships first
            DROP TABLE IF EXISTS auth_group_permissions;
            DROP TABLE IF EXISTS auth_user_groups;
            DROP TABLE IF EXISTS auth_user_user_permissions;
            
            -- Then drop the main tables
            DROP TABLE IF EXISTS account_emailaddress;
            DROP TABLE IF EXISTS account_emailconfirmation;
            DROP TABLE IF EXISTS auth_group;
            DROP TABLE IF EXISTS auth_permission;
            DROP TABLE IF EXISTS core_profile;
            
            SET FOREIGN_KEY_CHECKS = 1;
            """,
            reverse_sql="""
            -- This is intentionally empty as we cannot restore dropped tables in a reverse migration
            -- If you need to restore these tables, you'll need to run migrations from scratch
            """
        ),
    ]
