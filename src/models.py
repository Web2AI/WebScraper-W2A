from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Site(db.Model):  # type: ignore
    url = db.Column(db.String(255), primary_key=True)
    parent_url = db.Column(db.String(255),  nullable=True)
    json = db.Column(db.JSON)
    date = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Site {self.url}>"
