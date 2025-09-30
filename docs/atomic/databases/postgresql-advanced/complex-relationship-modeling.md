# Complex Relationship Modeling in PostgreSQL

Advanced patterns for modeling complex relationships, inheritance, polymorphism, and domain-driven design with PostgreSQL.

## Prerequisites

- [PostgreSQL Basic Setup](../postgresql/basic-setup.md)
- [SQLAlchemy Integration](../postgresql/sqlalchemy-integration.md)
- Understanding of database normalization principles

## Polymorphic Associations

### Single Table Inheritance (STI)

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Content(Base):
    __tablename__ = 'contents'

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)  # Discriminator column
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'))

    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_identity': 'content',
        'polymorphic_on': type
    }

class Article(Content):
    __tablename__ = 'contents'  # Same table

    content = Column(Text)
    word_count = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }

class Video(Content):
    __tablename__ = 'contents'  # Same table

    duration = Column(Integer)  # in seconds
    video_url = Column(String(500))
    thumbnail_url = Column(String(500))

    __mapper_args__ = {
        'polymorphic_identity': 'video'
    }

class Product(Content):
    __tablename__ = 'contents'  # Same table

    price = Column(Float)
    sku = Column(String(100))
    inventory_count = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'product'
    }
```

### Class Table Inheritance (CTI)

```python
class BaseContent(Base):
    __tablename__ = 'base_contents'

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'base_content',
        'polymorphic_on': type
    }

class Article(BaseContent):
    __tablename__ = 'articles'

    id = Column(Integer, ForeignKey('base_contents.id'), primary_key=True)
    content = Column(Text, nullable=False)
    word_count = Column(Integer)
    reading_time = Column(Integer)  # in minutes
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")

    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }

class Video(BaseContent):
    __tablename__ = 'videos'

    id = Column(Integer, ForeignKey('base_contents.id'), primary_key=True)
    duration = Column(Integer)
    video_url = Column(String(500))
    thumbnail_url = Column(String(500))
    resolution = Column(String(20))  # 1080p, 720p, etc.

    __mapper_args__ = {
        'polymorphic_identity': 'video'
    }

class Product(BaseContent):
    __tablename__ = 'products'

    id = Column(Integer, ForeignKey('base_contents.id'), primary_key=True)
    price = Column(Numeric(10, 2))
    sku = Column(String(100), unique=True)
    inventory_count = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'))
    variants = relationship("ProductVariant", back_populates="product")

    __mapper_args__ = {
        'polymorphic_identity': 'product'
    }
```

## Advanced Relationship Patterns

### Self-Referencing Hierarchies

```python
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    level = Column(Integer, default=0)
    path = Column(String(500))  # Materialized path: /electronics/computers/laptops/
    left_boundary = Column(Integer)  # For nested set model
    right_boundary = Column(Integer)

    # Self-referencing relationship
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")

    def get_ancestors(self) -> List['Category']:
        """Get all parent categories"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors[::-1]  # Root first

    def get_descendants(self, session) -> List['Category']:
        """Get all child categories using nested set model"""
        if self.left_boundary and self.right_boundary:
            return session.query(Category).filter(
                Category.left_boundary > self.left_boundary,
                Category.right_boundary < self.right_boundary
            ).all()
        return []

class CategoryClosure(Base):
    """Closure table for efficient hierarchy queries"""
    __tablename__ = 'category_closures'

    ancestor_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    descendant_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    depth = Column(Integer, nullable=False)

    ancestor = relationship("Category", foreign_keys=[ancestor_id])
    descendant = relationship("Category", foreign_keys=[descendant_id])
```

### Many-to-Many with Attributes

```python
class UserRole(Base):
    """Association object with additional attributes"""
    __tablename__ = 'user_roles'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by_id = Column(Integer, ForeignKey('users.id'))
    expires_at = Column(DateTime)
    scope = Column(String(100))  # 'global', 'project:123', etc.

    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    granted_by = relationship("User", foreign_keys=[granted_by_id])

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)

    user_roles = relationship("UserRole", foreign_keys=[UserRole.user_id], back_populates="user")

    def has_role(self, role_name: str, scope: str = 'global') -> bool:
        """Check if user has specific role in scope"""
        return any(
            ur.role.name == role_name and ur.scope == scope
            for ur in self.user_roles
            if ur.expires_at is None or ur.expires_at > datetime.utcnow()
        )

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(Text)
    permissions = relationship("Permission", secondary="role_permissions")
    user_roles = relationship("UserRole", back_populates="role")
```

### Generic Foreign Keys (Polymorphic Associations)

```python
class Comment(Base):
    """Comments that can be attached to any entity"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))

    # Generic foreign key
    commentable_type = Column(String(50), nullable=False)  # 'article', 'product', etc.
    commentable_id = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User")

    @property
    def commentable(self):
        """Get the commented object"""
        if self.commentable_type == 'article':
            return session.query(Article).get(self.commentable_id)
        elif self.commentable_type == 'product':
            return session.query(Product).get(self.commentable_id)
        # Add more types as needed
        return None

# Mixin for commentable entities
class CommentableMixin:
    @property
    def comments(self):
        return session.query(Comment).filter(
            Comment.commentable_type == self.__class__.__name__.lower(),
            Comment.commentable_id == self.id
        ).all()

    def add_comment(self, content: str, author_id: int) -> Comment:
        comment = Comment(
            content=content,
            author_id=author_id,
            commentable_type=self.__class__.__name__.lower(),
            commentable_id=self.id
        )
        session.add(comment)
        return comment

class Article(Content, CommentableMixin):
    # ... existing fields ...
    pass

class Product(Content, CommentableMixin):
    # ... existing fields ...
    pass
```

## Advanced Querying Patterns

### Dynamic Relationships with Hybrid Properties

```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func, case

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")

    @hybrid_property
    def total_amount(self):
        """Calculate total order amount"""
        return sum(item.quantity * item.unit_price for item in self.items)

    @total_amount.expression
    def total_amount(cls):
        """SQL expression for total amount"""
        return (
            select([func.sum(OrderItem.quantity * OrderItem.unit_price)])
            .where(OrderItem.order_id == cls.id)
            .label('total_amount')
        )

    @hybrid_property
    def item_count(self):
        return len(self.items)

    @item_count.expression
    def item_count(cls):
        return (
            select([func.count(OrderItem.id)])
            .where(OrderItem.order_id == cls.id)
            .label('item_count')
        )

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

# Usage examples
def get_high_value_orders(session, min_amount: float):
    """Get orders above certain amount using hybrid property"""
    return session.query(Order).filter(Order.total_amount >= min_amount).all()

def get_order_statistics(session):
    """Get aggregated order statistics"""
    return session.query(
        func.count(Order.id).label('total_orders'),
        func.avg(Order.total_amount).label('avg_order_value'),
        func.sum(Order.total_amount).label('total_revenue'),
        func.max(Order.total_amount).label('largest_order')
    ).first()
```

### Complex Join Patterns

```python
class OrderAnalytics:
    """Complex analytical queries for orders"""

    @staticmethod
    def get_customer_lifetime_value(session, user_id: int):
        """Calculate customer lifetime value with detailed breakdown"""
        return session.query(
            User.id,
            User.username,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('lifetime_value'),
            func.avg(Order.total_amount).label('avg_order_value'),
            func.min(Order.created_at).label('first_order_date'),
            func.max(Order.created_at).label('last_order_date'),
            func.extract('days', func.max(Order.created_at) - func.min(Order.created_at)).label('customer_lifespan_days')
        ).join(Order).filter(User.id == user_id).group_by(User.id, User.username).first()

    @staticmethod
    def get_product_performance(session, start_date: datetime, end_date: datetime):
        """Analyze product performance with category breakdown"""
        return session.query(
            Product.id,
            Product.title,
            Category.name.label('category_name'),
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.count(func.distinct(OrderItem.order_id)).label('unique_orders'),
            func.avg(OrderItem.unit_price).label('avg_selling_price')
        ).join(OrderItem).join(Order).join(Category).filter(
            Order.created_at.between(start_date, end_date),
            Order.status == 'completed'
        ).group_by(Product.id, Product.title, Category.name).order_by(
            func.sum(OrderItem.quantity * OrderItem.unit_price).desc()
        ).all()

    @staticmethod
    def get_cohort_analysis(session):
        """Customer cohort analysis by month"""
        # First order month for each user
        first_order_subquery = session.query(
            Order.user_id,
            func.date_trunc('month', func.min(Order.created_at)).label('cohort_month')
        ).group_by(Order.user_id).subquery()

        # Cohort analysis
        return session.query(
            first_order_subquery.c.cohort_month,
            func.extract('month', Order.created_at - first_order_subquery.c.cohort_month).label('period_number'),
            func.count(func.distinct(Order.user_id)).label('customers'),
            func.sum(Order.total_amount).label('revenue')
        ).join(
            first_order_subquery, Order.user_id == first_order_subquery.c.user_id
        ).group_by(
            first_order_subquery.c.cohort_month,
            func.extract('month', Order.created_at - first_order_subquery.c.cohort_month)
        ).order_by(
            first_order_subquery.c.cohort_month,
            func.extract('month', Order.created_at - first_order_subquery.c.cohort_month)
        ).all()
```

## Event Sourcing Pattern

```python
class EventStore(Base):
    """Event store for domain events"""
    __tablename__ = 'event_store'

    id = Column(Integer, primary_key=True)
    aggregate_id = Column(String(100), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=False)
    event_version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    correlation_id = Column(String(100))
    causation_id = Column(String(100))

    __table_args__ = (
        Index('ix_aggregate_id_version', 'aggregate_id', 'event_version'),
        UniqueConstraint('aggregate_id', 'event_version', name='uq_aggregate_version')
    )

class OrderAggregate:
    """Order aggregate for event sourcing"""

    def __init__(self, order_id: str):
        self.id = order_id
        self.version = 0
        self.status = 'pending'
        self.items = []
        self.total_amount = 0
        self.events = []

    @classmethod
    def from_events(cls, order_id: str, events: List[EventStore]) -> 'OrderAggregate':
        """Reconstruct aggregate from events"""
        order = cls(order_id)
        for event in sorted(events, key=lambda e: e.event_version):
            order.apply_event(event.event_type, event.event_data)
            order.version = event.event_version
        return order

    def add_item(self, product_id: int, quantity: int, unit_price: float):
        """Add item to order"""
        event_data = {
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': unit_price
        }
        self.add_event('ItemAdded', event_data)

    def remove_item(self, product_id: int):
        """Remove item from order"""
        event_data = {'product_id': product_id}
        self.add_event('ItemRemoved', event_data)

    def confirm_order(self):
        """Confirm the order"""
        if self.status != 'pending':
            raise ValueError("Order can only be confirmed from pending status")
        self.add_event('OrderConfirmed', {})

    def add_event(self, event_type: str, event_data: dict):
        """Add new event to aggregate"""
        self.version += 1
        event = {
            'aggregate_id': self.id,
            'aggregate_type': 'Order',
            'event_type': event_type,
            'event_data': event_data,
            'event_version': self.version
        }
        self.events.append(event)
        self.apply_event(event_type, event_data)

    def apply_event(self, event_type: str, event_data: dict):
        """Apply event to update aggregate state"""
        if event_type == 'ItemAdded':
            self.items.append({
                'product_id': event_data['product_id'],
                'quantity': event_data['quantity'],
                'unit_price': event_data['unit_price']
            })
            self.total_amount += event_data['quantity'] * event_data['unit_price']

        elif event_type == 'ItemRemoved':
            self.items = [
                item for item in self.items
                if item['product_id'] != event_data['product_id']
            ]
            self.recalculate_total()

        elif event_type == 'OrderConfirmed':
            self.status = 'confirmed'

    def recalculate_total(self):
        """Recalculate total amount"""
        self.total_amount = sum(
            item['quantity'] * item['unit_price']
            for item in self.items
        )

class EventRepository:
    """Repository for managing events"""

    def __init__(self, session):
        self.session = session

    def save_events(self, events: List[dict]) -> None:
        """Save events to event store"""
        for event_data in events:
            event = EventStore(**event_data)
            self.session.add(event)
        self.session.commit()

    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[EventStore]:
        """Get events for aggregate"""
        return self.session.query(EventStore).filter(
            EventStore.aggregate_id == aggregate_id,
            EventStore.event_version > from_version
        ).order_by(EventStore.event_version).all()

    def get_aggregate(self, aggregate_id: str) -> OrderAggregate:
        """Reconstruct aggregate from events"""
        events = self.get_events(aggregate_id)
        return OrderAggregate.from_events(aggregate_id, events)
```

## JSONB and Advanced Data Types

```python
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID
from sqlalchemy import text

class ProductCatalog(Base):
    """Product with flexible attributes using JSONB"""
    __tablename__ = 'product_catalog'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    category = Column(String(100))

    # Flexible attributes stored as JSONB
    attributes = Column(JSONB)
    specifications = Column(JSONB)
    pricing = Column(JSONB)

    # Array fields
    tags = Column(ARRAY(String))
    image_urls = Column(ARRAY(String))

    # Full-text search
    search_vector = Column(String)  # Will be populated by trigger

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_attribute(self, key: str, value: Any):
        """Set flexible attribute"""
        if self.attributes is None:
            self.attributes = {}
        self.attributes[key] = value

    def get_attribute(self, key: str, default=None):
        """Get flexible attribute"""
        if self.attributes is None:
            return default
        return self.attributes.get(key, default)

class ProductQuery:
    """Advanced querying for JSONB data"""

    @staticmethod
    def find_by_attribute(session, key: str, value: Any):
        """Find products by JSONB attribute"""
        return session.query(ProductCatalog).filter(
            ProductCatalog.attributes[key].astext == str(value)
        ).all()

    @staticmethod
    def find_by_price_range(session, min_price: float, max_price: float):
        """Find products by price range in JSONB"""
        return session.query(ProductCatalog).filter(
            ProductCatalog.pricing['base_price'].astext.cast(Float) >= min_price,
            ProductCatalog.pricing['base_price'].astext.cast(Float) <= max_price
        ).all()

    @staticmethod
    def find_by_tags(session, tags: List[str]):
        """Find products containing any of the specified tags"""
        return session.query(ProductCatalog).filter(
            ProductCatalog.tags.overlap(tags)
        ).all()

    @staticmethod
    def search_specifications(session, spec_criteria: dict):
        """Search by complex specification criteria"""
        filters = []
        for key, value in spec_criteria.items():
            filters.append(
                ProductCatalog.specifications[key].astext == str(value)
            )

        return session.query(ProductCatalog).filter(*filters).all()

    @staticmethod
    def full_text_search(session, search_term: str):
        """Full-text search across product data"""
        return session.query(ProductCatalog).filter(
            text("search_vector @@ plainto_tsquery(:search)")
        ).params(search=search_term).all()

# SQL for setting up full-text search trigger
FULLTEXT_SEARCH_SETUP = """
-- Add tsvector column for full-text search
ALTER TABLE product_catalog ADD COLUMN search_vector tsvector;

-- Create index for fast text search
CREATE INDEX idx_product_search ON product_catalog USING gin(search_vector);

-- Function to update search vector
CREATE OR REPLACE FUNCTION update_product_search_vector()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.category, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.attributes::text, '')), 'C') ||
        setweight(to_tsvector('english', coalesce(NEW.specifications::text, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update search vector
CREATE TRIGGER update_product_search_trigger
    BEFORE INSERT OR UPDATE ON product_catalog
    FOR EACH ROW EXECUTE FUNCTION update_product_search_vector();
"""
```

## Related Documentation

- [PostgreSQL Performance Optimization](performance-optimization.md)
- [Production Migrations](production-migrations.md)
- [Multi-tenant Patterns](multi-tenant-patterns.md)
- [SQLAlchemy Integration](../postgresql/sqlalchemy-integration.md)

## Best Practices

1. **Relationship Design**:
   - Choose inheritance pattern based on query patterns
   - Use closure tables for deep hierarchies
   - Consider performance implications of joins

2. **JSONB Usage**:
   - Index frequently queried JSON paths
   - Use appropriate data types for better performance
   - Implement proper validation for flexible schemas

3. **Event Sourcing**:
   - Keep events immutable and append-only
   - Use correlation IDs for tracking related events
   - Implement snapshots for large aggregates

4. **Query Optimization**:
   - Use hybrid properties for computed fields
   - Implement proper indexing strategies
   - Consider materialized views for complex analytics

5. **Data Integrity**:
   - Use database constraints where possible
   - Implement domain validation in application layer
   - Use transactions for multi-table operations