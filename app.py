import time
import os
from urllib.parse import urlparse

import dash
from dash import DiskcacheManager, CeleryManager, Input, Output, html

using = None

if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery

    celery_app = Celery(__name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"])
    background_callback_manager = CeleryManager(celery_app)
    print("using celery")
    using = "celery"

elif "REDIS_SERVICE_HOST" in os.environ and "REDIS_SERVICE_PORT" in os.environ:

    from celery import Celery

    redis_host = os.getenv("REDIS_SERVICE_HOST", "127.0.0.1")
    redis_pw = os.getenv("database-password", "")
    redis_port = os.getenv("REDIS_SERVICE_PORT", "6379")


    redis_string = f"redis://:{ redis_pw }@{ redis_host }:{ redis_port }"

    celery_app = Celery(
        __name__,
        broker=redis_string,
        backend=redis_string
    )

    background_callback_manager = CeleryManager(celery_app)
    print("using celery w/ env vars")
    using = "celery, env vars"

else:
    # Diskcache for non-production apps when developing locally
    import diskcache

    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)
    print("using diskcache")
    using = "diskcache"


app = dash.Dash(__name__, background_callback_manager=background_callback_manager)

server = app.server

app.layout = html.Div(
    [
        html.Div([html.P(id="paragraph_id", children=["Button not clicked"])]),
        html.Button(id="button_id", children="Run Job!"),
    ]
)


@dash.callback(
    output=Output("paragraph_id", "children"),
    inputs=Input("button_id", "n_clicks"),
    background=True,
)
def update_clicks(n_clicks):
    time.sleep(2.0)
    global using
    return [f"Clicked {n_clicks} times, using: {using}"]


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
