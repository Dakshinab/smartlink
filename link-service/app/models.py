from app import db
from datetime import datetime

class Link(db.Model):
    """
    This is our database table called 'link'.
    Each row = one shortened URL.
    
    Think of it like an Excel sheet with these columns:
    id | short_code | original_url | created_at | click_count | is_active
    """
    __tablename__ = "link"

    # Primary key - auto-increments (1, 2, 3...)
    id = db.Column(db.Integer, primary_key=True)

    # The short code e.g. "abc123" - must be unique
    short_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # The original long URL e.g. "https://google.com/very/long/path"
    original_url = db.Column(db.String(2048), nullable=False)

    # Optional custom title for the link
    title = db.Column(db.String(200), nullable=True)

    # When the link was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # How many times the link was clicked
    click_count = db.Column(db.Integer, default=0)

    # Whether the link is active (we soft-delete instead of hard-delete)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """
        Convert this object to a dictionary so we can return it as JSON.
        APIs speak JSON - Python objects need to be converted first.
        """
        return {
            "id": self.id,
            "short_code": self.short_code,
            "original_url": self.original_url,
            "title": self.title,
            "short_url": f"http://localhost:5001/{self.short_code}",
            "created_at": self.created_at.isoformat(),
            "click_count": self.click_count,
            "is_active": self.is_active,
        }