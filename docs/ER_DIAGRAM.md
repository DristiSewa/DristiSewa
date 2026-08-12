# DristiSewa Entity-Relationship Diagram

This diagram represents the implemented application data model and its 18
application tables. Django's 7 infrastructure tables are intentionally omitted:
`django_admin_log`, `django_content_type`, `django_migrations`, `django_session`,
`auth_group`, `auth_group_permissions`, and `auth_permission`. Every entity has
an implicit Django `id` primary key unless a key is explicitly named. Models that
inherit `TimeStampedModel` also contain `created_at` and `updated_at`.

```mermaid
erDiagram
    BRANCH {
        int id PK
        string name UK
        string code UK
        string address
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    USER {
        int id PK
        string email UK
        string role
        int branch_id FK
        string phone
        text experience_details
        string profile_pic
        datetime last_seen
        datetime date_joined
    }

    STUDENT {
        int id PK
        int user_id FK, UK
        int assigned_to_id FK
        int assigned_manager_id FK
        int assigned_by_id FK
        date date_of_birth
        string college
        int passed_year
        decimal gpa
        string test_type
        decimal test_score
        string preferred_country
        boolean is_archived
        boolean is_verified
        string profile_pic
        datetime created_at
        datetime updated_at
    }

    APPLICATION {
        int id PK
        int student_id FK
        string destination_country
        string institution
        string status
        text remarks
        datetime created_at
        datetime updated_at
    }

    DOCUMENT {
        int id PK
        int student_id FK
        string doc_type
        string file
        string status
        string remarks
        datetime created_at
        datetime updated_at
    }

    FOLLOW_UP {
        int id PK
        int student_id FK
        int assigned_to_id FK
        text note
        date scheduled_date
        boolean is_done
        datetime created_at
        datetime updated_at
    }

    APPOINTMENT {
        int id PK
        int student_id FK
        int staff_id FK
        string purpose
        date appointment_date
        time appointment_time
        string status
        text notes
        datetime created_at
        datetime updated_at
    }

    ACTIVITY_LOG {
        int id PK
        int user_id FK
        string action
        text description
        datetime created_at
    }

    DETAILED_ACTIVITY_LOG {
        int id PK
        int user_id FK
        int branch_id FK
        string action
        text description
        string entity_type
        string entity_id
        string status
        string ip_address
        text user_agent
        json changes
        datetime created_at
    }

    AGGREGATED_ANALYTICS {
        int id PK
        date date UK
        int branch_id FK, UK
        int total_students
        int new_students
        int active_students
        int verified_students
        int archived_students
        int total_applications
        int applications_pending
        int applications_approved
        int applications_rejected
        int applications_visa_granted
        int total_documents
        int documents_pending
        int documents_approved
        int documents_rejected
        int followups_pending
        int followups_completed
        int total_managers
        int total_frontdesk
        float visa_success_rate
        float student_growth_percentage
        float avg_documents_per_student
        datetime updated_at
    }

    USER_ENGAGEMENT_METRICS {
        int id PK
        date date UK
        int user_id FK, UK
        int branch_id FK
        int login_count
        int active_sessions
        int total_actions
        datetime last_activity
        int students_processed
        int documents_reviewed
        int followups_completed
        float average_response_time_hours
        float error_rate
    }

    OTP_VERIFICATION {
        int id PK
        string email
        string otp
        string purpose
        boolean is_verified
        datetime created_at
    }

    SUPER_ADMIN {
        int id PK
        int user_id FK, UK
        boolean can_manage_users
        boolean can_manage_branches
        boolean can_manage_students
        boolean can_manage_applications
        boolean can_manage_documents
        boolean can_view_analytics
        boolean can_export_data
        boolean can_import_data
        boolean can_backup_database
        boolean can_restore_database
        boolean can_manage_system
        boolean can_view_audit_logs
        boolean is_active
        datetime created_at
        datetime updated_at
        datetime last_login
        int login_count
    }

    DATABASE_BACKUP {
        int id PK
        int created_by_id FK
        string backup_file
        string backup_type
        text description
        float file_size_mb
        int table_count
        int record_count
        boolean is_verified
        datetime created_at
    }

    DATA_EXPORT {
        int id PK
        int created_by_id FK
        string export_file
        string export_type
        text tables_included
        int record_count
        float file_size_mb
        text description
        datetime created_at
    }

    DATA_IMPORT {
        int id PK
        int created_by_id FK
        string import_file
        string import_type
        string status
        int total_records
        int successful_records
        int failed_records
        text error_details
        datetime created_at
        datetime completed_at
    }

    SUPER_ADMIN_AUDIT_LOG {
        int id PK
        int superadmin_id FK
        string action
        text description
        int affected_records
        string status
        string ip_address
        text user_agent
        datetime created_at
    }

    DATABASE_STATISTICS {
        int id PK
        datetime timestamp
        int total_users
        int total_students
        int total_applications
        int total_documents
        int total_followups
        int total_branches
        int active_students
        int archived_students
        int verified_students
        int pending_applications
        int approved_applications
        int rejected_applications
        int visa_granted_applications
        int pending_documents
        int approved_documents
        int pending_followups
        int completed_followups
        int logins_today
        int actions_today
    }

    BRANCH o|--o{ USER : employs
    USER ||--o| STUDENT : "has profile"
    USER o|--o{ STUDENT : "assigned to"
    USER o|--o{ STUDENT : "assigned manager"
    USER o|--o{ STUDENT : "assigned by"
    STUDENT ||--o{ APPLICATION : submits
    STUDENT ||--o{ DOCUMENT : owns
    STUDENT ||--o{ FOLLOW_UP : needs
    USER o|--o{ FOLLOW_UP : assigned
    STUDENT ||--o{ APPOINTMENT : attends
    USER o|--o{ APPOINTMENT : staffs
    USER o|--o{ ACTIVITY_LOG : creates
    USER o|--o{ DETAILED_ACTIVITY_LOG : performs
    BRANCH o|--o{ DETAILED_ACTIVITY_LOG : scopes
    BRANCH ||--o{ AGGREGATED_ANALYTICS : summarizes
    USER ||--o{ USER_ENGAGEMENT_METRICS : records
    BRANCH o|--o{ USER_ENGAGEMENT_METRICS : scopes
    USER ||--o| SUPER_ADMIN : "has admin profile"
    SUPER_ADMIN o|--o{ DATABASE_BACKUP : creates
    SUPER_ADMIN o|--o{ DATA_EXPORT : creates
    SUPER_ADMIN o|--o{ DATA_IMPORT : creates
    SUPER_ADMIN o|--o{ SUPER_ADMIN_AUDIT_LOG : performs
```

## Notes

- `USER.role` distinguishes Admin, Manager, Front Desk, and Student accounts.
- The unused `User.groups` and `User.user_permissions` relationships were removed;
    the corresponding `accounts_user_groups` and `accounts_user_user_permissions`
    tables are not part of the database.
- `STUDENT.user_id` and `SUPER_ADMIN.user_id` are one-to-one relationships.
- `AGGREGATED_ANALYTICS` is unique per `(date, branch)` and
  `USER_ENGAGEMENT_METRICS` is unique per `(date, user)`.
- `OTP_VERIFICATION` and `DATABASE_STATISTICS` are standalone operational
  records. OTP records deliberately use email rather than a user foreign key
  because they can be created before registration.
- The database currently contains 25 tables in total: 18 application tables and
    7 Django infrastructure tables.
