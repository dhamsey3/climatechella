from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    date = db.Column(db.String(50))
    image_url = db.Column(db.String(300))
    published = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Story {self.title}>'
        