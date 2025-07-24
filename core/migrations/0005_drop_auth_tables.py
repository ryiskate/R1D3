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
    
    Note: This migration handles dependencies by first dropping foreign key constraints
    before dropping the tables themselves.
    """

    dependencies = [
        ('core', '0002_quicklink'),  # Update this to match your last core migration
    ]

    operations = [
        # First, identify and drop foreign key constraints that reference these tables
        migrations.RunSQL(
            sql="""
            -- Find and drop foreign keys that reference the tables we want to drop
            SET @database_name = DATABASE();
            
            -- Create a temporary table to store constraint information
            CREATE TEMPORARY TABLE IF NOT EXISTS constraints_to_drop (
                table_name VARCHAR(255),
                constraint_name VARCHAR(255)
            );
            
            -- Find constraints referencing auth_group
            INSERT INTO constraints_to_drop
            SELECT TABLE_NAME, CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_SCHEMA = @database_name
              AND REFERENCED_TABLE_NAME IN ('auth_group', 'auth_permission', 'auth_user', 'core_profile')
              AND CONSTRAINT_NAME IS NOT NULL;
            
            -- Drop the identified constraints
            SET @sql = NULL;
            SELECT GROUP_CONCAT(CONCAT('ALTER TABLE `', table_name, '` DROP FOREIGN KEY `', constraint_name, '`;'))
            INTO @sql
            FROM constraints_to_drop;
            
            -- Execute the generated SQL if constraints were found
            SET FOREIGN_KEY_CHECKS = 0;
            
            -- Only execute if we found constraints
            SET @sql = IFNULL(@sql, 'SELECT "No constraints found"');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            
            -- Clean up
            DROP TEMPORARY TABLE IF EXISTS constraints_to_drop;
            """,
            reverse_sql="""
            -- Cannot restore constraints in reverse migration
            """
        ),
        
        # Then drop the tables with foreign key checks disabled
        migrations.RunSQL(
            sql="""
            SET FOREIGN_KEY_CHECKS = 0;
            
            DROP TABLE IF EXISTS account_emailaddress;
            DROP TABLE IF EXISTS account_emailconfirmation;
            DROP TABLE IF EXISTS auth_group;
            DROP TABLE IF EXISTS auth_group_permissions;
            DROP TABLE IF EXISTS auth_permission;
            DROP TABLE IF EXISTS auth_user_groups;
            DROP TABLE IF EXISTS auth_user_user_permissions;
            DROP TABLE IF EXISTS core_profile;
            
            SET FOREIGN_KEY_CHECKS = 1;
            """,
            reverse_sql="""
            -- This is intentionally empty as we cannot restore dropped tables in a reverse migration
            -- If you need to restore these tables, you'll need to run migrations from scratch
            """
        ),
    ]
