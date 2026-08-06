# DristiSewa Entity-Relationship Diagram

This diagram represents the implemented application data model. Every entity has
an implicit Django `id` primary key unless a key is explicitly named. Models that
inherit `TimeStampedModel` also contain `created_at` and `updated_at`.

```mermaid
erDiagram
    BRANCH {
        int id PK
        string name UK
        string code UK
        string address
        string phone
        string email
        boolean is_active
    }

    USER {
        int id PK
        string email UK
        string role
        int branch_id FK
        string phone
        string experience_details
        datetime last_seen
    }

    STUDENT {
        int id PK
        int user_id FK_UK
        int assigned_to_id FK
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
    }

    APPLICATION {
        int id PK
        int student_id FK
        string destination_country
        string institution
        string status
        text remarks
    }

    DOCUMENT {
        int id PK
        int student_id FK
        string doc_type
        string file
        string status
        string remarks
    }

    FOLLOW_UP {
        int id PK
        int student_id FK
        int assigned_to_id FK
        text note
        date scheduled_date
        boolean is_done
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
        string entity_type
        string entity_id
        string status
        json changes
        datetime created_at
    }

    AGGREGATED_ANALYTICS {
        int id PK
        date date UK
        int branch_id FK_UK
        int total_students
        int total_applications
        int total_documents
        int followups_pending
        float visa_success_rate
    }

    USER_ENGAGEMENT_METRICS {
        int id PK
        date date UK
        int user_id FK_UK
        int branch_id FK
        int login_count
        int total_actions
        int followups_completed
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
        int user_id FK_UK
        boolean is_active
        datetime last_login
        int login_count
    }

    DATABASE_BACKUP {
        int id PK
        int created_by_id FK
        string backup_file
        string backup_type
        boolean is_verified
        datetime created_at
    }

    DATA_EXPORT {
        int id PK
        int created_by_id FK
        string export_file
        string export_type
        text tables_included
        datetime created_at
    }

    DATA_IMPORT {
        int id PK
        int created_by_id FK
        string import_file
        string import_type
        string status
        int total_records
        datetime created_at
    }

    SUPER_ADMIN_AUDIT_LOG {
        int id PK
        int superadmin_id FK
        string action
        string status
        int affected_records
        datetime created_at
    }

    DATABASE_STATISTICS {
        int id PK
        datetime timestamp
        int total_users
        int total_students
        int total_applications
        int total_documents
    }

    BRANCH o|--o{ USER : employs
    USER ||--o| STUDENT : "has profile"
    USER o|--o{ STUDENT : "assigned to"
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
- `STUDENT.user_id` and `SUPER_ADMIN.user_id` are one-to-one relationships.
- `AGGREGATED_ANALYTICS` is unique per `(date, branch)` and
  `USER_ENGAGEMENT_METRICS` is unique per `(date, user)`.
- `OTP_VERIFICATION` and `DATABASE_STATISTICS` are standalone operational
  records. OTP records deliberately use email rather than a user foreign key
  because they can be created before registration.
