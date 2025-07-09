# Generated manually to fix missing table in production

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0002_remove_is_completed_add_status'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS "strategy_strategymilestone" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "title" varchar(200) NOT NULL,
                "description" text NOT NULL,
                "target_date" date NULL,
                "status" varchar(20) NOT NULL,
                "completion_date" date NULL,
                "order" integer NOT NULL,
                "phase_id" integer NOT NULL REFERENCES "strategy_strategyphase" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS strategy_strategymilestone;"
        ),
    ]
