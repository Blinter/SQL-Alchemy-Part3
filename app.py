"""Blogly application."""
import datetime

from flask import Flask, request, redirect, render_template, flash

from models import db, connect_db, User, Post, PostTag, Tag
# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_part3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret3'
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)

app.config['SECRET_KEY'] = "SECRET11!"
# debug = DebugToolbarExtension(app)


@app.errorhandler(404)
def page_not_found(e):
    """Default 404 Page"""
    flash("Page not found!" + request.url, 'success')
    return render_template('404.html',
                           tags=db.session.query(Tag).all(),
                           posts=db.session.query(Post).order_by(
                               Post.created_at.desc()).limit(5)), 404


@app.route("/")
def home():
    """To Fix Again Later"""
    return redirect("/posts")


@app.route("/tags")
def show_tags():
    """Show tags"""
    tags = db.session.query(Tag).all()
    posts = db.session.query(Post).join(PostTag).all()
    return render_template("tags.html",
                           tags=tags,
                           posts=posts)


@app.route("/tags/new")
def new_tag():
    """New Tag"""
    return render_template("add_new_tag.html")


@app.route("/tags/new", methods=["POST"])
def new_tag_apply():
    """New Tag Apply"""
    name = request.form.get('name', None)
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    flash("Tag has been added to the list!", 'success')
    return redirect(f"/tags/{tag.id}")


@app.route("/tags/<int:tag_id>")
def show_tag(tag_id):
    """Show Tag Details"""
    posts = (db.session.query(Post)
             .join(PostTag).join(Tag)
             .filter(Tag.id == tag_id).all())
    found_tag = db.get_or_404(Tag, tag_id)
    return render_template("tag_details.html",
                           posts=posts,
                           tag=found_tag)


@app.route("/tags/<int:tag_id>/edit")
def edit_tag(tag_id):
    """Edit Tag"""
    posts = (db.session.query(Post)
             .join(PostTag).join(Tag)
             .filter(Tag.id == tag_id).all())
    found_tag = db.get_or_404(Tag, tag_id)
    return render_template("edit_tag.html",
                           posts=posts,
                           tag=found_tag)


@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def tag_post_apply(tag_id):
    """Edit Tag Apply"""
    tag = db.get_or_404(Tag, tag_id)
    tag.name = request.form.get('name', None)
    if tag.name is None:
        return redirect(f"/tags/{tag.id}")
    tag.verified = True
    db.session.commit()
    flash("Tag modified successfully!", 'success')
    return redirect(f"/tags/{tag.id}")


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """Delete Tag"""
    for post_tag in db.session.query(PostTag).filter(PostTag.tag == tag_id):
        db.session.delete(post_tag)
    db.session.delete(db.get_or_404(Tag, tag_id))
    db.session.commit()
    flash("Tag deleted successfully!", 'success')
    return redirect(f"/tags")


@app.route("/users")
def list_users():
    """List Users"""
    return render_template("user.html",
                           users=db.session.query(User).order_by(
                               User.last_name.asc()).order_by(
                               User.first_name.asc()).all())


@app.route("/users/new")
def add_new_user_form():
    """Show New User Form"""
    return render_template("new_user.html")


@app.route("/users/new", methods=["POST"])
def add_new_user():
    """Add New User"""
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    image_url = request.form['image_url']
    image_url = str(image_url) if image_url else None
    user = User(first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                image_url=image_url)
    db.session.add(user)
    db.session.commit()
    flash("New user added successfully!", 'success')
    return redirect(f"/users")


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Show User Details"""
    return render_template("user_details.html",
                           user=db.get_or_404(User, user_id))


@app.route("/users/<int:user_id>/posts/new")
def new_post(user_id):
    """New Post"""
    return render_template("add_new_post.html",
                           tags=db.session.query(Tag).all(),
                           user=db.get_or_404(User, user_id))


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def new_post_apply(user_id):
    """New Post Apply"""
    user = db.get_or_404(User, user_id)
    title = request.form.get('title', None)
    content = request.form.get('content', None)
    post = Post(title=title, content=content, user_id=user.id)
    db.session.add(post)
    db.session.commit()
    for tag in db.session.query(Tag).all():
        if not request.form.get('tag-[' + str(tag.id) + "]", False):
            continue
        db.session.add(PostTag(post=post.id, tag=tag.id))
    db.session.commit()
    flash("Post has been added to the list!", 'success')
    return redirect(f"/posts/{post.id}")


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Edit User"""
    return render_template("edit_user.html",
                           user=db.get_or_404(User, user_id))


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user_apply(user_id):
    """Edit User Apply"""
    user = db.get_or_404(User, user_id)

    first_name = request.form.get('first_name', False)
    middle_name = request.form.get('middle_name', False)
    last_name = request.form.get('last_name', False)
    image_url = request.form.get('image_url', False)

    user.first_name = first_name if first_name and len(str(first_name)) > 0\
        else ' '
    user.middle_name = middle_name if middle_name and len(str(middle_name)) > 0\
        else ''
    user.last_name = last_name if last_name and len(str(last_name)) > 0 else ' '
    user.image_url = image_url if image_url and len(str(image_url)) > 0 else \
        'https://via.placeholder.com/50'

    user.verified = True
    db.session.commit()
    flash("User modified successfully!", 'success')
    return redirect(f"/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete User"""
    db.session.delete(db.get_or_404(User, user_id))
    db.session.commit()
    flash("User deleted successfully!", 'success')
    return redirect(f"/users")


@app.route("/posts")
def show_posts():
    """Show 5 more recent posts"""
    return render_template("posts.html",
                           tags=db.session.query(Tag).all(),
                           posts=db.session.query(Post).order_by(
                               Post.created_at.desc()).limit(5))


@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """Show Post"""
    post_tags = (db.session.query(Tag).join(PostTag)
                 .filter(PostTag.post == post_id).all())
    return render_template("post_details.html",
                           tags=post_tags,
                           post=db.get_or_404(Post, post_id))

@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """Edit Post"""
    return render_template("edit_post.html",
                           tags=db.session.query(Tag).all(),
                           post=db.get_or_404(Post, post_id))


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post_apply(post_id):
    """Edit Post Apply"""
    post = db.get_or_404(Post, post_id)
    post.title = request.form.get('title', None)
    post.content = request.form.get('content', None)
    post.modified_on = datetime.datetime.now(datetime.UTC)
    for tag in post.post_tags:
        if not request.form.get('tag-[' + str(tag.tag) + "]", False):
            db.session.delete(tag)
    for tag in db.session.query(Tag).all():
        if request.form.get('tag-[' + str(tag.id) + "]", False):
            found_in = False
            for current_tags in post.post_tags:
                if current_tags.tag == tag.id:
                    found_in = True
                    break
            if not found_in:
                db.session.add(PostTag(post=post.id, tag=tag.id))
    db.session.commit()
    post.verified = True
    db.session.commit()
    flash("Post modified successfully!", 'success')
    return redirect(f"/posts/{post.id}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Delete Post"""
    db.session.delete(db.get_or_404(Post, post_id))
    db.session.commit()
    flash("Post deleted successfully!", 'success')
    return redirect(f"/posts")
