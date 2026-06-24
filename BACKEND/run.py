# from app import create_app
# import os

# app = create_app()

# @app.route("/test")
# def test():
#     return 10 / 0

# if __name__ == "__main__":
#     host = "127.0.0.1"   # localhost only
#     port = int(os.getenv("PORT", 8081))

#     print(f"Server starting at {host}:{port}")

#     app.run(
#         host=host,
#         port=port,
#         debug=False
#     )

from app import create_app
import os

app = create_app()

@app.route("/test")
def test():
    return "Test OK"

if __name__ == "__main__":
    host = "0.0.0.0"   # Allow external access
    port = int(os.getenv("PORT", 8081))

    print(f"Server starting at {host}:{port}")

    app.run(
        host=host,
        port=port,
        debug=True
    )