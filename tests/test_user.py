from app.models import User, PrivacyOption, Following
from app.auth.manager import UserManager


# def test_password_is_hashed():
#     u = User(username='susan')
#     u.set_password('cat')
#     assert not u.check_password('dog')
#     assert u.check_password('cat')


# def test_avatar_is_obtained():
#     u = User(username='john', email='john@example.com')
#     assert u.avatar(128) ==  ('https://www.gravatar.com/avatar/'
#                                          'd4c74594d841139328695756648b6bd6'
#                                          '?d=identicon&s=128')


# def test_user_can_be_added_by_anyone(dummy_db,user_alice):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice)
#     assert alice


# def test_public_user_can_be_followed(dummy_db,user_alice,user_bob):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.public)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=bob.username)
#     assert alice.is_following_accepted(target_user=bob)
#     assert not bob.is_following(target_user=alice)


# def test_user_cannot_follow_themselves(dummy_db,user_alice):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=alice.username)
#     assert not alice.is_following(target_user=alice)
    

# def test_private_user_cannot_be_followed(dummy_db,user_alice,user_bob):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.private)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=bob.username)
#     assert not alice.is_following(target_user=bob)
#     assert not bob.is_following(target_user=alice)


# def test_nonexisting_follow_cannot_be_accepted(dummy_db,user_alice,user_bob):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

#     assert not alice.is_following(target_user=bob)
#     assert not bob.is_following(target_user=alice)

#     um_bob = UserManager(session=dummy_db.session,user=bob)
#     um_bob.accept_following(source_username=alice.username)
#     assert not alice.is_following(target_user=bob)
#     assert not bob.is_following(target_user=alice)


# def test_friends_user_must_accept_follow_request(dummy_db,user_alice,user_bob):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=bob.username)
#     assert alice.is_following(target_user=bob)
#     assert not alice.is_following_accepted(target_user=bob)
#     assert not bob.is_following(target_user=alice)

#     um_bob = UserManager(session=dummy_db.session,user=bob)
#     um_bob.accept_following(source_username=alice.username)
#     assert alice.is_following_accepted(target_user=bob)
#     assert not bob.is_following(target_user=alice)


# def test_switching_privacy_to_public_accepts_all_follow_requests(dummy_db,user_alice,user_bob):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=bob.username)
#     assert alice.is_following(target_user=bob)
#     assert not bob.is_following_accepted(target_user=bob)

#     um_bob = UserManager(session=dummy_db.session,user=bob)
#     um_bob.set_privacy(new_privacy=PrivacyOption.public)
#     assert alice.is_following_accepted(target_user=bob)
#     assert not bob.is_following(target_user=alice)


# def test_switching_privacy_to_private_removes_all_followers(dummy_db,user_alice,user_bob):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.public)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=bob.username)
#     assert alice.is_following_accepted(target_user=bob)
#     assert not bob.is_following(target_user=alice)

#     um_bob = UserManager(session=dummy_db.session,user=bob)
#     um_bob.set_privacy(new_privacy=PrivacyOption.private)

#     assert not alice.is_following_accepted(target_user=bob)
#     assert not alice.is_following(target_user=bob)
#     assert not bob.is_following(target_user=alice)


# def test_outgoing_follows_can_be_retrieved(dummy_db,user_alice,user_bob,user_charlie,user_david,user_elvis):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.public)
#     charlie = um.add_user(**user_charlie,privacy=PrivacyOption.public)
#     david = um.add_user(**user_david,privacy=PrivacyOption.friends)
#     elvis = um.add_user(**user_elvis,privacy=PrivacyOption.private)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_alice.follow_user(target_username=bob.username)
#     um_alice.follow_user(target_username=charlie.username)
#     um_alice.follow_user(target_username=david.username)
#     um_alice.follow_user(target_username=elvis.username)

#     alice_outgoing_follows = um_alice.get_outgoing_follows()
#     alice_incoming_follows = um_alice.get_incoming_follows()

#     assert alice.username not in alice_outgoing_follows.keys()
#     assert bob.username in alice_outgoing_follows.keys()
#     assert charlie.username in alice_outgoing_follows.keys()
#     assert david.username in alice_outgoing_follows.keys()
#     assert elvis.username not in alice_outgoing_follows.keys()

#     assert not alice_incoming_follows


# def test_incoming_follows_can_be_retrieved(dummy_db,user_alice,user_bob,user_charlie,user_david):
#     um = UserManager(session=dummy_db.session)
#     alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
#     bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)
#     charlie = um.add_user(**user_charlie,privacy=PrivacyOption.private)
#     david = um.add_user(**user_david,privacy=PrivacyOption.public)

#     um_alice = UserManager(session=dummy_db.session,user=alice)
#     um_bob = UserManager(session=dummy_db.session,user=bob)
#     um_charlie = UserManager(session=dummy_db.session,user=charlie)
#     um_david = UserManager(session=dummy_db.session,user=david)

#     um_david.follow_user(target_username=alice.username)
#     um_david.follow_user(target_username=bob.username)
#     um_david.follow_user(target_username=charlie.username)
#     um_david.follow_user(target_username=david.username)

#     alice_incoming_follows = um_alice.get_incoming_follows()
#     bob_incoming_follows = um_bob.get_incoming_follows()
#     charlie_incoming_follows = um_charlie.get_incoming_follows()
#     david_incoming_follows = um_david.get_incoming_follows()

#     assert david.username in alice_incoming_follows.keys()
#     assert david.username in bob_incoming_follows.keys()
#     assert david.username not in charlie_incoming_follows.keys()
#     assert david.username not in david_incoming_follows.keys()

    
def test_incoming_pending_follow_can_be_removed(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_bob = UserManager(session=dummy_db.session,user=bob)

    um_alice.follow_user(target_username=bob.username)
    assert not alice.is_following_accepted(target_user=bob)
    assert alice.is_following(target_user=bob)

    um_bob.remove_following(source_username=alice.username)
    assert not alice.is_following(target_user=bob)


def test_incoming_accepted_follow_can_be_removed(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_bob = UserManager(session=dummy_db.session,user=bob)

    um_alice.follow_user(target_username=bob.username)
    assert not alice.is_following_accepted(target_user=bob)
    assert alice.is_following(target_user=bob)

    um_bob.accept_following(source_username=alice.username)
    assert alice.is_following_accepted(target_user=bob)

    um_bob.remove_following(source_username=alice.username)
    assert not alice.is_following(target_user=bob)


def test_outgoing_pending_follow_can_be_removed(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_bob = UserManager(session=dummy_db.session,user=bob)

    um_alice.follow_user(target_username=bob.username)
    assert not alice.is_following_accepted(target_user=bob)
    assert alice.is_following(target_user=bob)

    um_alice.cancel_outgoing_following(target_username=bob.username)
    assert not alice.is_following(target_user=bob)


def test_outgoing_accepted_follow_can_be_removed(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_bob = UserManager(session=dummy_db.session,user=bob)

    um_alice.follow_user(target_username=bob.username)
    assert not alice.is_following_accepted(target_user=bob)
    assert alice.is_following(target_user=bob)

    um_bob.accept_following(source_username=alice.username)
    assert alice.is_following_accepted(target_user=bob)

    um_alice.cancel_outgoing_following(target_username=bob.username)
    assert not alice.is_following(target_user=bob)