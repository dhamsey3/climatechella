from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stories.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    location = db.Column(db.String(100))
    date = db.Column(db.String(50), default=datetime.now().strftime('%B %d, %Y'))
    image_url = db.Column(db.String(300))
    published = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50))

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    featured_stories = Story.query.filter_by(published=True).order_by(Story.id.desc()).limit(3).all()
    return render_template('index.html', stories=featured_stories)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stories')
def stories():
    all_stories = Story.query.filter_by(published=True).all()
    return render_template('stories.html', stories=all_stories)

@app.route('/story/<int:id>')
def story(id):
    story = Story.query.get_or_404(id)
    return render_template('story.html', story=story)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()
        
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/submit-story', methods=['GET', 'POST'])
def submit_story():
    if request.method == 'POST':
        # Required fields validation
        required_fields = ['title', 'content']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'{field.capitalize()} is required', 'error')
                return redirect(url_for('submit_story'))
        
        # Create story with defaults
        new_story = Story(
            title=request.form['title'],
            content=request.form['content'],
            author=request.form.get('author', 'Anonymous'),
            location=request.form.get('location', ''),
            image_url=request.form.get('image_url') or url_for('static', filename='images/default-story.jpg'),
            category=request.form.get('category', 'Personal Story'),
            published=False
        )
        
        db.session.add(new_story)
        db.session.commit()
        flash('Story submitted for review!', 'success')
        return redirect(url_for('home'))
    
    return render_template('submit_story.html')

@app.route('/test-static')
def test_static():
    return f"""
    CSS exists: {os.path.exists('static/css/style.css')}<br>
    Image exists: {os.path.exists('static/images/test-image.jpg')}<br>
    Templates exist: {os.path.exists('templates/base.html')}
    """

@app.route('/debug-stories')
def debug_stories():
    stories = Story.query.all()
    return {
        'count': len(stories),
        'stories': [{
            'id': s.id,
            'title': s.title,
            'author': s.author,
            'has_content': bool(s.content),
            'has_image': bool(s.image_url)
        } for s in stories]
    }

# CLI Commands
@app.cli.command('init-db')
def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Add sample stories
        sample_stories = [
            Story(
                title="Welcome to My Climate Definition",
                content="Over the past six years, I have personally experienced...",
                author="Patricia Korir",
                location="Kenya",
                category="Personal Story",
                image_url="https://images.unsplash.com/photo-1466611653911-95081537e5b7",
                published=True
            ),
            Story(
                title="Building Resilience From Within",
                content="How our community is adapting to climate challenges...",
                author="James Mwangi",
                location="Mukuru kwa Njenga",
                category="Community",
                image_url="https://images.unsplash.com/photo-1566438480900-0609be27a4be",
                published=True
            )
        ]
        
        db.session.bulk_save_objects(sample_stories)
        db.session.commit()
    print("Database initialized with sample data!")

if __name__ == '__main__':
    app.run(debug=True)