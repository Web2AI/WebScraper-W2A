from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Site(db.Model):  # type: ignore
    url = db.Column(db.String(255), primary_key=True)
    parent_url = db.Column(db.String(255), nullable=True)
    json = db.Column(db.JSON)
    date = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Site {self.url}>"


class Attachment(db.Model):  # type: ignore
    # NOTE:
    # The attachment_url could POTENTIALLY be the primary key,
    # but it is not guaranteed to be not null.
    # At this stage an artificial key is used.

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(255))      # TODO: add foreign key
    attachment_type = db.Column(db.String(255))
    attachment_content = db.Column(db.LargeBinary)
    attachment_url = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Attachement {self.url}>"