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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_url = db.Column(db.String(255), db.ForeignKey("site.url"))
    type = db.Column(db.String(255))
    content = db.Column(db.LargeBinary)
    url = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Attachement {self.url}>"
