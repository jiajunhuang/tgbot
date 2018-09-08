import gevent.monkey
gevent.monkey.patch_all()  # noqa

import base64

from flask import Flask, render_template, make_response, request, send_from_directory

from models import get_session, URLShare

app = Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory("./static/", "favicon.ico")


@app.route("/")
def index():
    jump = request.args.get("jump")
    if not jump.startswith("https"):
        jump = str(base64.urlsafe_b64decode(bytes(jump)))

    with get_session() as s:
        urls = s.query(URLShare).order_by(URLShare.id.desc()).all()

        return render_template('index.html', urls=urls, jump=jump)


@app.route("/rss")
def rss():
    with get_session() as s:
        urls = s.query(URLShare).order_by(URLShare.id.desc()).all()

        response = make_response(render_template('rss.xml', urls=urls))
        response.headers['Content-Type'] = 'application/xml'

        return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
