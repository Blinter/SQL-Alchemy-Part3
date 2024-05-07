from unittest import TestCase
from app import app
from models import db, User, Post, PostTag, Tag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sqla_intro_test3'
app.config['SQLALCHEMY_ECHO'] = False


class TagModelTestCase(TestCase):
    """Tests for model for Tags."""

    def setUp(self):
        """Clean up any existing Tags."""

        with app.app_context():
            db.drop_all()
            db.create_all()
            self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()
            db.drop_all()
            db.create_all()

    def test_tag_repl(self):
        """Test for output for better debug"""
        with app.app_context():
            tag = Tag(name='Cool!')
            db.session.add(tag)
            db.session.commit()
            self.assertTrue(bool(tag))
            self.assertEqual(str(tag),
                             f"<Tag id={tag.id} name=Cool!>")

            tag = Tag(name='Bad!')
            db.session.add(tag)
            db.session.commit()
            self.assertTrue(bool(tag))
            self.assertEqual(str(tag),
                             f"<Tag id={tag.id} name=Bad!>")

            tag = Tag(name='Rad!')
            db.session.add(tag)
            db.session.commit()
            self.assertTrue(bool(tag))
            self.assertEqual(str(tag),
                             f"<Tag id={tag.id} name=Rad!>")

    def test_post_tag(self):
        """Test Post_Tag Database Support"""
        with app.app_context():
            user1 = User(first_name="Alice", last_name="Smith")
            db.session.add(user1)
            db.session.commit()
            self.assertEqual(str(user1),
                             "<User ID=1 First Name=Alice Last Name="
                             "Smith Image URL=https://via.placeholder.com/30>")
            post = Post(title='Mauris cursus mattis molestie',
                        created_at="2022-01-30 04:47:04",
                        content='Lorem ipsum dolor sit amet',
                        user_id=user1.id)
            db.session.add(post)
            db.session.commit()
            self.assertTrue(bool(post))
            self.assertEqual(str(post),
                             "<Post ID=1 Title=Mauris "
                             "cursus mattis molestie Content=Lorem "
                             "ipsum dolor sit amet Created At="
                             "2022-01-30 04:47:04>")
            # user1 tied to post
            # now add tag
            tag = Tag(name='Rad!')
            db.session.add(tag)
            db.session.commit()
            self.assertEqual(str(tag),
                             f"<Tag id={tag.id} name=Rad!>")
            db.session.add(PostTag(post=post.id, tag=tag.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(PostTag))
                                 .scalars().first()),
                             "<Post Tag post_id=1 tag_id=1>")
            tag = Tag(name='Bad!')
            db.session.add(tag)
            db.session.add(PostTag(post=post.id, tag=tag.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(
                db.select(PostTag)).scalars().all()),
                             "[<Post Tag post_id=1 tag_id=1>, "
                             "<Post Tag post_id=1 tag_id=2>]")

    def test_unique_tags(self):
        """Test Multiple Tags on Database Support"""
        with app.app_context():
            user1 = User(first_name="Alice", last_name="Smith")
            user2 = User(first_name="Ral", last_name="Rwt")
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            post1 = Post(title='Mauris cursus mattis molestie',
                         created_at="2022-01-30 04:47:04",
                         content='Lorem ipsum dolor sit amet',
                         user_id=user1.id)
            post2 = Post(title='Mauris cursus m3tis molestie',
                         created_at="2022-01-27 04:47:04",
                         content='Lorem ipsum dsor sit amet',
                         user_id=user2.id)
            post3 = Post(title='Mauris carsus m3tis molestie',
                         created_at="2022-02-13 04:42:04",
                         content='Lorem ipsum d3or sit amet',
                         user_id=user1.id)
            db.session.add(post1)
            db.session.add(post2)
            db.session.add(post3)
            tag1 = Tag(name='Rad!')
            tag2 = Tag(name='None')
            tag3 = Tag(name='Bad!')
            tag4 = Tag(name='Sad!')
            tag5 = Tag(name='Wad!')
            tag6 = Tag(name='Rau')
            db.session.add_all([tag1, tag2, tag3, tag4, tag5, tag6])
            db.session.commit()
            self.assertEqual(str(tag1),
                             f"<Tag id={tag1.id} name=Rad!>")
            db.session.add(PostTag(post=post1.id, tag=tag1.id))
            db.session.add(PostTag(post=post1.id, tag=tag2.id))
            db.session.add(PostTag(post=post1.id, tag=tag3.id))
            db.session.add(PostTag(post=post1.id, tag=tag4.id))
            db.session.add(PostTag(post=post1.id, tag=tag5.id))
            db.session.add(PostTag(post=post1.id, tag=tag6.id))
            # commit not needed with "through" relationship
            self.assertEqual(str(
                db.session.execute(db.select(PostTag))
                .scalars().all()), "[<Post Tag post_id=1 tag_id=1>, "
                                  "<Post Tag post_id=1 tag_id=2>, <Post Tag "
                                  "post_id=1 tag_id=3>, <Post Tag post_id=1 "
                                  "tag_id=4>, <Post Tag post_id=1 tag_id=5>, "
                                  "<Post Tag post_id=1 tag_id=6>]")
            self.assertEqual(str(post1.post_tags),
                             "[<Post Tag post_id=1 tag_id=1>, "
                             "<Post Tag post_id=1 tag_id=2>, <Post Tag "
                             "post_id=1 tag_id=3>, <Post Tag post_id=1 "
                             "tag_id=4>, <Post Tag post_id=1 tag_id=5>, <Post "
                             "Tag post_id=1 tag_id=6>]")
            self.assertFalse(post2.post_tags)
            db.session.add(PostTag(post=post2.id, tag=tag1.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(PostTag)).all()),
                             "[(<Post Tag post_id=1 tag_id=1>,), "
                             "(<Post Tag post_id=1 tag_id=2>,), (<Post Tag "
                             "post_id=1 tag_id=3>,), (<Post Tag post_id=1 "
                             "tag_id=4>,), (<Post Tag post_id=1 tag_id=5>,), "
                             "(<Post Tag post_id=1 tag_id=6>,), (<Post Tag "
                             "post_id=2 tag_id=1>,)]")
            self.assertTrue(post2.post_tags)
            self.assertFalse(post3.post_tags)

    def test_delete_cascade_tags(self):
        """Test Delete Tags Support"""
        with app.app_context():
            user1 = User(first_name="Alice", last_name="Smith")
            user2 = User(first_name="Ral", last_name="Rwt")
            db.session.add(user1)
            db.session.commit()
            post1 = Post(title='Mauris cursus mattis molestie',
                         created_at="2022-01-30 04:47:04",
                         content='Lorem ipsum dolor sit amet',
                         user_id=user1.id)
            post2 = Post(title='Mauris cursus m3tis molestie',
                         created_at="2022-01-27 04:47:04",
                         content='Lorem ipsum dsor sit amet',
                         user_id=user2.id)
            db.session.add(post1)
            db.session.add(post2)
            tag1 = Tag(name='Rad!')
            tag2 = Tag(name='None')
            tag3 = Tag(name='Bad!')
            db.session.add_all([tag1, tag2, tag3])
            db.session.commit()
            post_tag1 = PostTag(post=post1.id, tag=tag1.id)
            post_tag2 = PostTag(post=post1.id, tag=tag2.id)
            post_tag3 = PostTag(post=post2.id, tag=tag3.id)
            db.session.add(post_tag1)
            db.session.add(post_tag2)
            db.session.add(post_tag3)
            db.session.commit()
            # commit not needed with "through" relationship
            self.assertTrue(post2.post_tags)
            self.assertEqual(str(post2.post_tags), "[<Post Tag "
                                                   "post_id=2 tag_id=3>]")
            self.assertEqual(str(post2),
                             "<Post ID=2 Title=Mauris cursus m3tis "
                             "molestie Content=Lorem ipsum dsor sit amet"
                             "[post_tags][<Post Tag post_id=2 tag_id=3>] "
                             "Created At=2022-01-27 04:47:04>")
            db.session.delete(post_tag3)
            db.session.commit()
            self.assertEqual(str(post2), "<Post ID=2 Title=Mauris "
                                         "cursus m3tis molestie Content=Lorem "
                                         "ipsum dsor sit amet Created At="
                                         "2022-01-27 04:47:04>")
            self.assertEqual(str(post2.post_tags), "[]")
            self.assertFalse(post2.post_tags)
            post_tag4 = PostTag(post=post2.id, tag=tag3.id)
            db.session.add(post_tag4)
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(PostTag)).all()),
                             "[(<Post Tag post_id=1 tag_id=1>,), (<Post"
                             " Tag post_id=1 tag_id=2>,), (<Post Tag post_id=2 "
                             "tag_id=3>,)]")
            self.assertEqual(str(db.session.execute(db.select(Tag)).all()),
                             "[(<Tag id=1 name=Rad!>,), "
                             "(<Tag id=2 name=None>,), (<Tag id=3"
                             " name=Bad!>,)]")
            self.assertEqual(str(db.session.execute(db.select(Post)).all()),
                             "[(<Post ID=1 Title=Mauris cursus "
                             "mattis molestie Content=Lorem ipsum dolor sit "
                             "amet[post_tags][<Post Tag post_id=1 tag_id=1>,  "
                             "Created At=2022-01-30 04:47:04>,), (<Post ID=2 "
                             "Title=Mauris cursus m3tis molestie Content=Lorem "
                             "ipsum dsor sit amet[post_tags][<Post Tag "
                             "post_id=2 tag_id=3>] Created At=2022-01-27 "
                             "04:47:04>,)]")
            db.session.delete(post1.post_tags[0])
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(Tag)).all()),
                             "[(<Tag id=1 name=Rad!>,), "
                             "(<Tag id=2 name=None>,), "
                             "(<Tag id=3 name=Bad!>,)]")
            db.session.delete(post1.post_tags[0])
            db.session.commit()
            self.assertEqual(str(post1),
                             "<Post ID=1 Title=Mauris cursus "
                             "mattis molestie Content=Lorem ipsum dolor "
                             "sit amet Created At=2022-01-30 04:47:04>")
            self.assertFalse(post1.post_tags)
            self.assertTrue(post2.post_tags)
            self.assertEqual(str(post2.post_tags),
                             "[<Post Tag post_id=2 tag_id=3>]")
            self.assertEqual(str(db.session.execute(db.select(PostTag)).all()),
                             "[(<Post Tag post_id=2 tag_id=3>,)]")
            # now delete post
            self.assertEqual(str(db.session.execute(db.select(Post)).all()),
                             "[(<Post ID=1 Title=Mauris cursus mattis "
                             "molestie Content=Lorem ipsum dolor sit amet "
                             "Created At=2022-01-30 04:47:04>,), (<Post ID=2 "
                             "Title=Mauris cursus m3tis molestie Content=Lorem "
                             "ipsum dsor sit amet[post_tags][<Post Tag "
                             "post_id=2 tag_id=3>] Created At=2022-01-27 "
                             "04:47:04>,)]")
            db.session.delete(post2)
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(Post)).all()),
                             "[(<Post ID=1 Title=Mauris cursus mattis "
                             "molestie Content=Lorem ipsum dolor sit amet "
                             "Created At=2022-01-30 04:47:04>,)]")
            self.assertEqual(str(db.session.execute(db.select(PostTag)).all()),
                             "[]")
            self.assertFalse(db.session.execute(db.select(PostTag)).all())

    def test_select(self):
        """Test Post Tags"""
        with app.app_context():
            user1 = User(first_name="Alice", last_name="Smith")
            db.session.add(user1)
            db.session.commit()
            self.assertEqual(str(user1),
                             "<User ID=1 First Name=Alice Last Name="
                             "Smith Image URL=https://via.placeholder.com/30>")
            post = Post(title='Mauris cursus mattis molestie',
                        created_at="2022-01-30 04:47:04",
                        content='Lorem ipsum dolor sit amet',
                        user_id=user1.id)
            db.session.add(post)
            db.session.commit()
            self.assertTrue(bool(post))
            self.assertEqual(str(post),
                             "<Post ID=1 Title=Mauris "
                             "cursus mattis molestie Content=Lorem "
                             "ipsum dolor sit amet Created At="
                             "2022-01-30 04:47:04>")
            # user1 tied to post
            # now add tag
            tag = Tag(name='Rad!')
            db.session.add(tag)
            db.session.commit()
            self.assertEqual(str(tag),
                             f"<Tag id={tag.id} name=Rad!>")
            db.session.add(PostTag(post=post.id, tag=tag.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(PostTag))
                                 .scalars().first()),
                             "<Post Tag post_id=1 tag_id=1>")
            tag = Tag(name='Bad!')
            db.session.add(tag)
            db.session.add(PostTag(post=post.id, tag=tag.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(
                db.select(PostTag)).scalars().all()),
                             "[<Post Tag post_id=1 tag_id=1>, "
                             "<Post Tag post_id=1 tag_id=2>]")
            # Select All posts
            # test = db.session.query(PostTag.post).distinct().all()
            # print(test)
            # self.assertTrue(False)

    def test_select_from_tag(self):
        """Test Select Posts from Tags"""
        with app.app_context():
            user1 = User(first_name="Alice", last_name="Smith")
            db.session.add(user1)
            db.session.commit()
            self.assertEqual(str(user1),
                             "<User ID=1 First Name=Alice Last Name="
                             "Smith Image URL=https://via.placeholder.com/30>")
            post_new = Post(title='Mauris cursus mattis molestie',
                        created_at="2022-01-30 04:47:04",
                        content='Lorem ipsum dolor sit amet',
                        user_id=user1.id)
            db.session.add(post_new)
            db.session.commit()
            self.assertTrue(bool(post_new))
            self.assertEqual(str(post_new),
                             "<Post ID=1 Title=Mauris "
                             "cursus mattis molestie Content=Lorem "
                             "ipsum dolor sit amet Created At="
                             "2022-01-30 04:47:04>")
            # user1 tied to post
            # now add tag
            tag_rad = Tag(name='Rad!')
            db.session.add(tag_rad)
            db.session.commit()
            self.assertEqual(str(tag_rad),
                             f"<Tag id={tag_rad.id} name=Rad!>")
            db.session.add(PostTag(post=post_new.id, tag=tag_rad.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(db.select(PostTag))
                                 .scalars().first()),
                             "<Post Tag post_id=1 tag_id=1>")
            tag_bad = Tag(name='Bad!')
            db.session.add(tag_bad)
            db.session.add(PostTag(post=post_new.id, tag=tag_bad.id))
            db.session.commit()
            self.assertEqual(str(db.session.execute(
                db.select(PostTag)).scalars().all()),
                             "[<Post Tag post_id=1 tag_id=1>, "
                             "<Post Tag post_id=1 tag_id=2>]")
            # select single
            self.assertEqual(str(db.session.query(Post).join(
                PostTag).filter(PostTag.tag == 1).first()),
                             "<Post ID=1 Title=Mauris cursus mattis "
                             "molestie Content=Lorem ipsum dolor sit "
                             "amet[post_tags][<Post Tag post_id=1 tag_id=1>,  "
                             "Created At=2022-01-30 04:47:04>")
            #select two
            post_new2 = Post(title='Massuris cursus mattis molestie',
                        created_at="2022-01-30 04:42:04",
                        content='Lor3m ipsum dolor sit amet',
                        user_id=user1.id)
            db.session.add(post_new2)
            db.session.commit()
            db.session.add(PostTag(post=post_new2.id, tag=tag_bad.id))
            db.session.commit()
            select_post_tag = db.session.query(Post).join(
                PostTag).join(Tag).filter(Tag.id == 2).all()
            self.assertEqual(str(select_post_tag),
                             "[<Post ID=1 Title=Mauris cursus mattis "
                             "molestie Content=Lorem ipsum dolor sit amet"
                             "[post_tags][<Post Tag post_id=1 tag_id=1>,  "
                             "Created At=2022-01-30 04:47:04>, "
                             "<Post ID=2 Title=Massuris cursus mattis molestie "
                             "Content=Lor3m ipsum dolor sit amet[post_tags]"
                             "[<Post Tag post_id=2 tag_id=2>] Created At="
                             "2022-01-30 04:42:04>]")
