"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, UTC
import tzlocal
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Post(db.Model):
    """User"""

    __tablename__ = "posts"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.String(128),
                      nullable=False,
                      default='Lorem Ipsum')

    content = db.Column(db.String(65535),
                        nullable=False,
                        default='Lorem Ipsum')

    created_at = db.Column(db.TIMESTAMP,
                           nullable=False,
                           default=datetime.now(UTC))

    modified_on = db.Column(db.TIMESTAMP,
                            nullable=True,
                            default=datetime.now(UTC))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Fix applied: viewonly=True
    # Accessing Post.user -> to access properties
    user = db.relationship("User", backref="posts", viewonly=True)

    # post_tags = db.relationship('PostTag', backref="post_tags", viewonly=True)

    post_tags = db.relationship('PostTag',
                                backref="post_tags",
                                cascade="all, delete")

    @staticmethod
    def get_friendly(timediff):
        """Return a friendly Time"""
        seconds = timediff.total_seconds()
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        days = int(hours / 24)
        if days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    @property
    def friendly_created_at(self):
        """Property to return a friendly Time for Created At"""
        return Post.get_friendly(datetime.now(UTC) -
                                 datetime.fromisoformat(
                                     self.created_at.replace(
                                         tzinfo=tzlocal.get_localzone())
                                     .isoformat()))

    @property
    def friendly_modified_on(self):
        """Property to return a friendly Time for Modified On"""
        return Post.get_friendly(datetime.now(UTC) -
                                 datetime.fromisoformat(
                                     self.modified_on.replace(
                                         tzinfo=tzlocal.get_localzone())
                                     .isoformat()))

    @property
    def homepage_content(self):
        """Property to return a truncated content string"""
        return ((f"{self.content[:252]}" if len(self.content) > 255 else
                 self.content))

    @property
    def homepage_minified(self):
        """Property to return a boolean if content will be truncated"""
        return len(self.content) > 252

    def __repr__(self):
        """Show info about post."""

        return (f"<Post ID={self.id} " +
                f"Title={self.title[:32]} " +
                f"Content=" +
                ("[truncated]" if len(self.content) > 32 else "") +
                f"{self.content[:32]}" +
                (f"[post_tags]{(str(self.post_tags)[:32])}" if
                 self.post_tags else "") +
                f" Created At={self.created_at}>")


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    first_name = db.Column(db.String(50),
                           nullable=False)

    middle_name = db.Column(db.String(50),
                            nullable=True)

    last_name = db.Column(db.String(50),
                          nullable=False)

    image_url = db.Column(db.String(255),
                          nullable=False,
                          default='https://via.placeholder.com/30')

    created_posts = db.relationship('Post', cascade="all, delete")

    # SAWarning: relationship 'User.created_posts' will copy column users.id to
    # column posts.user_id, which conflicts with relationship(s): 'Post.user'
    # (copies users.id to posts.user_id), 'User.posts' (copies users.id to
    # posts.user_id). If this is not the intention, consider if these
    # relationships should be linked with back_populates, or if viewonly=True
    # should be applied to one or more if they are read-only. For the less
    # common case that foreign key constraints are partially overlapping, the
    # orm.foreign() annotation can be used to isolate the columns that should
    # be written towards.   To silence this warning, add the parameter
    # 'overlaps="posts,user"' to the 'User.created_posts' relationship.
    # (Background on this error at: https://sqlalche.me/e/14/qzyx)

    def get_full_name(self):
        """Function to add middle name + first/last name as an individual
        return string"""
        return self.first_name + \
            (" " + self.middle_name if self.middle_name is
                not None and len(self.middle_name) > 0
                else "") + \
            " " + self.last_name

    @property
    def full_name(self):
        """Property to return the full name, calling the function"""
        return self.get_full_name()

    def __repr__(self):
        """Show info about user."""

        return (f"<User ID={self.id} " +
                f"First Name={self.first_name} " +
                (f"Middle Name={self.middle_name} " if self.middle_name is
                    not None and len(self.middle_name) > 0 else "") +
                f"Last Name={self.last_name} " +
                f"Image URL={self.image_url}>")


class Tag(db.Model):
    """Tag"""
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True)

    def __repr__(self):
        """Show info about Tag."""
        return (f"<Tag id={self.id} " +
                f"name={self.name}>")


class PostTag(db.Model):
    """Post_Tag"""
    __tablename__ = "post_tags"
    post = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

    def __repr__(self):
        """Show info about Post Tag"""
        return (f"<Post Tag post_id={self.post} " +
                f"tag_id={self.tag}>")
