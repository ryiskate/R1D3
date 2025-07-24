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
            
            -- Check if tables exist before dropping them
            -- This avoids errors when tables don't exist
            
            -- Function to safely drop tables if they exist
            DROP PROCEDURE IF EXISTS drop_if_table_exists;
            CREATE PROCEDURE drop_if_table_exists(IN table_name VARCHAR(255))
            BEGIN
                DECLARE table_count INT;
                SELECT COUNT(*) INTO table_count FROM information_schema.tables 
                WHERE table_schema = DATABASE() AND table_name = table_name;
                
                IF table_count > 0 THEN
                    SET @sql = CONCAT('DROP TABLE `', table_name, '`;');
                    PREPARE stmt FROM @sql;
                    EXECUTE stmt;
                    DEALLOCATE PREPARE stmt;
                END IF;
            END;
            
            -- Drop tables that might have foreign key relationships first
            CALL drop_if_table_exists('auth_group_permissions');
            CALL drop_if_table_exists('auth_user_groups');
            CALL drop_if_table_exists('auth_user_user_permissions');
            
            -- Then drop the main tables
            CALL drop_if_table_exists('account_emailaddress');
            CALL drop_if_table_exists('account_emailconfirmation');
            CALL drop_if_table_exists('auth_group');
            CALL drop_if_table_exists('auth_permission');
            CALL drop_if_table_exists('core_profile');
            
            -- Clean up
            DROP PROCEDURE IF EXISTS drop_if_table_exists;
            
            SET FOREIGN_KEY_CHECKS = 1;
            """,
            reverse_sql="""
            -- This is intentionally empty as we cannot restore dropped tables in a reverse migration
            -- If you need to restore these tables, you'll need to run migrations from scratch
            """
        ),
    ]
