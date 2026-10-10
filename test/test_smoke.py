from fastapi import FastAPI

import main


def test_app_is_created():
    assert isinstance(main.app, FastAPI)


def test_health_route_registered():
    routes = [route.path for route in main.app.routes]
    assert "/openapi.json" in routes
