# Database Naming Conventions

This guide covers database naming patterns for PostgreSQL and MongoDB in the doc4microservices framework. It ensures consistent, self-documenting database schemas that align with the service architecture.

**Key Principle**: Use snake_case for all database objects. Tables/collections use plural nouns. Follow service boundaries for database separation.

---

## PostgreSQL

### Database Naming

Each service context gets its own database:

```sql
-- Database per context
CREATE DATABASE finance_db;
CREATE DATABASE healthcare_db;
CREATE DATABASE logistics_db;

-- Or database per service for complete isolation
CREATE DATABASE lending_service_db;
CREATE DATABASE telemedicine_service_db;
```

### Table Naming

Tables use **plural nouns** in snake_case:

```sql
-- Good table names
CREATE TABLE users (...);
CREATE TABLE loan_applications (...);
CREATE TABLE payment_transactions (...);
CREATE TABLE user_sessions (...);

-- Bad table names (avoid)
CREATE TABLE User (...);           -- No PascalCase
CREATE TABLE user (...);           -- Use plural
CREATE TABLE tbl_users (...);      -- No prefixes
CREATE TABLE UsersTable (...);     -- No suffixes
```

### Column Naming

Columns use snake_case with descriptive names:

```sql
CREATE TABLE users (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic fields
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),

    -- Boolean flags
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    has_premium BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,

    -- JSON fields
    metadata JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}'
);
```

### Foreign Key Naming

```sql
-- Pattern: {table}_{column}_fkey
ALTER TABLE loan_applications
    ADD CONSTRAINT loan_applications_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE payment_transactions
    ADD CONSTRAINT payment_transactions_loan_id_fkey
    FOREIGN KEY (loan_id) REFERENCES loan_applications(id);
```

### Index Naming

```sql
-- Pattern: idx_{table}_{column(s)}
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_loan_applications_user_id ON loan_applications(user_id);
CREATE INDEX idx_loan_applications_status_created_at
    ON loan_applications(status, created_at);

-- Unique index: uniq_{table}_{column(s)}
CREATE UNIQUE INDEX uniq_users_email ON users(email);
```

### View Naming

```sql
-- Pattern: v_{description} or {table}_view
CREATE VIEW v_active_loans AS
    SELECT * FROM loan_applications
    WHERE status = 'active';

CREATE VIEW user_statistics_view AS
    SELECT user_id, COUNT(*) as loan_count
    FROM loan_applications
    GROUP BY user_id;
```

### Function/Procedure Naming

```sql
-- Pattern: {verb}_{noun}
CREATE FUNCTION calculate_interest(
    principal DECIMAL,
    rate DECIMAL,
    months INT
) RETURNS DECIMAL AS $$
BEGIN
    RETURN principal * rate * months / 12;
END;
$$ LANGUAGE plpgsql;

CREATE PROCEDURE process_expired_loans() AS $$
BEGIN
    UPDATE loan_applications
    SET status = 'expired'
    WHERE expires_at < NOW()
    AND status = 'pending';
END;
$$ LANGUAGE plpgsql;
```

---

## MongoDB

### Database Naming

```javascript
// Database per context
use finance_db
use healthcare_db
use logistics_db
```

### Collection Naming

Collections use **plural nouns** in snake_case:

```javascript
// Good collection names
db.users
db.loan_applications
db.payment_transactions
db.audit_logs

// Bad collection names (avoid)
db.User              // No PascalCase
db.user              // Use plural
db.usersCollection   // No suffixes
```

### Field Naming

Fields use snake_case (not camelCase):

```javascript
// Good document structure
{
  _id: ObjectId(),
  user_id: "usr_123",
  email: "user@example.com",
  first_name: "John",
  last_name: "Doe",
  is_active: true,
  is_verified: false,
  created_at: ISODate(),
  updated_at: ISODate(),

  // Nested objects
  address: {
    street_address: "123 Main St",
    city: "Boston",
    state_code: "MA",
    postal_code: "02101"
  },

  // Arrays
  phone_numbers: [
    {
      type: "mobile",
      number: "+1-555-0123",
      is_primary: true
    }
  ]
}
```

### Index Naming

```javascript
// Single field index
db.users.createIndex(
  { email: 1 },
  { name: "idx_users_email" }
)

// Compound index
db.loan_applications.createIndex(
  { user_id: 1, created_at: -1 },
  { name: "idx_loan_applications_user_id_created_at" }
)

// Unique index
db.users.createIndex(
  { email: 1 },
  {
    name: "uniq_users_email",
    unique: true
  }
)

// Text index
db.products.createIndex(
  { name: "text", description: "text" },
  { name: "idx_products_text_search" }
)
```

### Aggregation Pipeline Naming

```javascript
// Name pipeline stages clearly
db.loan_applications.aggregate([
  { $match: { status: "approved" } },           // filter_approved
  { $group: {                                   // group_by_user
      _id: "$user_id",
      total_amount: { $sum: "$amount" }
    }
  },
  { $sort: { total_amount: -1 } },              // sort_by_amount
  { $limit: 10 }                                // limit_top_10
])
```

---

## Migration File Naming

### SQL Migrations (Alembic/Flyway)

```
migrations/
├── V001__create_users_table.sql
├── V002__create_loan_applications_table.sql
├── V003__add_email_index_to_users.sql
├── V004__add_status_column_to_loans.sql
```

### MongoDB Migrations

```
migrations/
├── 001_create_users_collection.js
├── 002_create_loan_applications_collection.js
├── 003_add_users_email_index.js
├── 004_add_status_field_to_loans.js
```

---

## Common Patterns

### Timestamp Columns

Always include these columns in PostgreSQL:
```sql
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
```

MongoDB equivalent:
```javascript
{
  created_at: ISODate(),
  updated_at: ISODate()
}
```

### Soft Delete Pattern

PostgreSQL:
```sql
deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
```

MongoDB:
```javascript
{
  deleted_at: null,  // or ISODate() when deleted
  is_deleted: false  // boolean alternative
}
```

### Status Fields

```sql
-- PostgreSQL enum
CREATE TYPE loan_status AS ENUM ('pending', 'approved', 'rejected', 'expired');
status loan_status NOT NULL DEFAULT 'pending'

-- Or simple varchar
status VARCHAR(20) NOT NULL DEFAULT 'pending'
```

```javascript
// MongoDB
{
  status: "pending"  // one of: pending, approved, rejected, expired
}
```

---

## Checklist

- [ ] Databases named per context or service
- [ ] Tables/collections use plural nouns
- [ ] All names use snake_case (no camelCase)
- [ ] Foreign keys follow {table}_{column}_fkey pattern
- [ ] Indexes follow idx_{table}_{columns} pattern
- [ ] Include created_at/updated_at timestamps
- [ ] No type prefixes (tbl_, col_, etc.)
- [ ] Migration files numbered sequentially

---

## Related Documents

- `./README.md` — Main naming conventions hub
- `naming-python.md` — Python model naming
- `naming-services.md` — Service naming patterns