from unittest import TestCase

from app import app
from models import db, User, Post,  PostTag, Tag

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sqla_intro_test3'
app.config['SQLALCHEMY_ECHO'] = False

with app.app_context():
    db.drop_all()
    db.create_all()


class UserModelTests(TestCase):
    def setUp(self):
        """Initialize Database with test objects"""
        self.user_id = 0
        with app.app_context():
            with app.test_client() as client:
                db.drop_all()
                db.create_all()
                db.session.commit()
                user = User(first_name="Tracy", middle_name="",
                            last_name="Rera",
                            image_url="https://via.placeholder.com/50")
                db.session.add(user)
                db.session.commit()
                post = Post(title='Mauris cursus mattis molestie',
                            created_at="2022-01-30 04:47:04",
                            content='Lorem ipsum dolor sit amet',
                            user_id=user.id)
                db.session.add(post)

                tag = Tag(name='Bad!')
                tag2 = Tag(name='Good')
                db.session.add(tag)
                db.session.add(tag2)
                db.session.commit()

                self.tag = tag
                self.tag2 = tag2

                self.tag_id = tag.id
                self.tag_id2 = tag2.id
                self.post_id = post.id
                self.user_id = user.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            with app.test_client() as client:
                db.session.rollback()

    def test_show_404(self):
        """Test that 404 will show stories"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get(f"/posts/{self.post_id}FAULTTEST404")
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 404)
                self.assertIn("Mauris cursus mattis molestie", html)
                db.session.rollback()

    def test_show_post(self):
        """Test that post details will show content"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get(f"/posts/{self.post_id}")
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Mauris cursus mattis molestie", html)
                db.session.rollback()

    def test_new_post_show(self):
        """Test that new post form can be shown"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get(f"/users/{self.user_id}/posts/new")
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("NEW POST", html)
                db.session.rollback()

    def test_edit_post(self):
        """Test that post can be modified"""
        with app.app_context():
            with app.test_client() as client:
                d = {"title": "MODIFIEDTITLE",
                     "content": "MODIFIEDCONTENT"}
                resp2 = client.post(f"/posts/{self.post_id}/edit", data=d,
                                    follow_redirects=True)
                resp2.get_data(as_text=True)
                html2 = resp2.get_data(as_text=True)

                resp = client.get("/posts")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("MODIFIEDTITLE", html2)
                self.assertIn("MODIFIEDCONTENT", html2)
                self.assertIn("MODIFIEDTITLE", html)
                self.assertIn("MODIFIEDCONTENT", html)

    def test_list_users_show(self):
        """Test that user list will show user"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get("/users")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Tracy', html)

    def test_form_adduser_showing(self):
        """Test that user form will show"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get("/users/new")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("ADD USER", html)

    def test_add_user_displayed(self):
        """Test that users can be added then displayed"""
        with app.app_context():
            with app.test_client() as client:
                d = {"first_name": "Treyer",
                     "middle_name": "",
                     "last_name": "Darell",
                     "image_url": ""}
                resp2 = client.post("/users/new", data=d, follow_redirects=True)
                resp2.get_data(as_text=True)

                resp = client.get("/users", follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Treyer", html)

    def test_show_user_displayed(self):
        """Test that user details are displayed"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get(f"/users/{self.user_id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('<h2>Tracy Rera</h2>', html)

    def test_edit_user_form_displayed(self):
        """Test that edit user form can be displayed"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.get(f"/users/{self.user_id}/edit")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Tracy", html)

    def test_edit_user_change(self):
        """Test that users can be edited"""
        with app.app_context():
            with app.test_client() as client:
                d = {"first_name": "Treyer",
                     "middle_name": None,
                     "last_name": "Darell",
                     "image_url": "https://via.placeholder.com/50"}
                resp2 = client.post(f"/users/{self.user_id}/edit", data=d,
                                    follow_redirects=True)
                resp = client.get("/users", follow_redirects=True)
                resp2.get_data(as_text=True)
                html = resp.get_data(as_text=True)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Treyer", html)

    def test_delete_post(self):
        """Test that posts can be deleted"""
        with app.app_context():
            with app.test_client() as client:
                resp2 = client.post(f"/posts/{self.post_id}/delete",
                                    follow_redirects=True)
                resp2.get_data(as_text=True)
                html2 = resp2.get_data(as_text=True)

                resp = client.get("/posts")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("Mauris cursus", html)

    def test_delete_user(self):
        """Test that users can be deleted"""
        with app.app_context():
            with app.test_client() as client:
                resp = client.post(f"/users/{self.user_id}/delete",
                                   follow_redirects=True)

                resp = client.get("/users")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("Tracy", html)

    def test_delete_tag(self):
        """Test that tags can be deleted from database"""
        with app.app_context():
            with app.test_client() as client:

                db.session.add(PostTag(post=self.post_id, tag=self.tag_id))
                db.session.commit()
                resp = client.get("/posts")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Bad", html)

                resp = client.get("/tags")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Bad", html)

                resp = client.post(f"/tags/{self.tag_id}/delete",
                                   follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("Bad", html)

                resp = client.get("/posts")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("Bad", html)

    def test_show_all_tags(self):
        """Test that tags show on Posts"""
        with app.app_context():
            with app.test_client() as client:

                resp = client.get(f"/posts/{self.post_id}/edit")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(self.tag.name, html)
                self.assertIn(self.tag2.name, html)