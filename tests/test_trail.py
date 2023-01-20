from app.models import Route

def test_route_can_be_added(fakedb):
    db = fakedb
    t1 = Route(
        displayname='GR131',
        fullname='Brugse Ommeland - Ieperboog',
        length=144.05,
    )
    db.session.add(t1)
    db.session.commit()
    routes = Route.query.all()

    assert len(routes) == 1
    assert routes[0].displayname == 'GR131'
    assert routes[0].fullname == 'Brugse Ommeland - Ieperboog'
    assert routes[0].length == 144.05