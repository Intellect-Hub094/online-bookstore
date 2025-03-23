from flask import session


def _clear_flashes():
    if "_flashes" in session:
        session["_flashes"] = []
