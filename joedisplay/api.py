from flask import Flask, jsonify, request, make_response

"""
Simple API to control the display.
No auth as it's just running on the LAN, which may or may not be appropriate for your use case.
"""


def create_api(name, stage_controller):
    app = Flask("display_api")

    @app.route('/display', methods=['POST'])
    def update_stage():
        stage_controller.event_handler(request.json, {})
        return jsonify({"status": "ok"})

    return app
