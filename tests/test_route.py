from app.models import Trail

def test_trail_can_be_added(fakedb):
    db = fakedb
    t1 = Trail(
        displayname='GR131',
        fullname='Brugse Ommeland - Ieperboog',
        length=144.05,
    )
    db.session.add(t1)
    db.session.commit()
    routes = Trail.query.all()

    assert len(routes) == 1
    assert routes[0].displayname == 'GR131'
    assert routes[0].fullname == 'Brugse Ommeland - Ieperboog'
    assert routes[0].length == 144.05