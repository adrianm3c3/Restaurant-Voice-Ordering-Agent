from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

from src.agent import handle_user_input, MENU, is_checkout_complete_response
from src.order_manager import OrderManager
from src.config import CONFIG


app = Flask(__name__)

# Stores active call sessions by Twilio CallSid
sessions = {}


def make_initial_state():
    return {
        "last_removed": None,
        "last_modified": None,
        "pending_wing_item": None,
        "checkout_step": None,
        "checkout_info": None,
    }


def get_call_session(call_sid):
    if call_sid not in sessions:
        sessions[call_sid] = {
            "order_manager": OrderManager(),
            "state": make_initial_state(),
        }

    return sessions[call_sid]


def build_gather_response(message):
    """
    Tell Twilio to speak a message, then listen for the caller's next response.
    """
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/voice",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(message)
    response.append(gather)

    # If no speech is detected, Twilio continues here.
    response.say("I did not catch that. Please say that again.")
    response.redirect("/voice", method="POST")

    return Response(str(response), mimetype="text/xml")


@app.route("/voice", methods=["GET", "POST"])
def voice():
    call_sid = request.values.get("CallSid", "local-test-call")
    user_text = request.values.get("SpeechResult")

    session = get_call_session(call_sid)
    order_manager = session["order_manager"]
    state = session["state"]

    if not user_text:
        restaurant_name = CONFIG["restaurant"]["name"]
        return build_gather_response(
            f"Hello, welcome to {restaurant_name}. What would you like to order?"
        )

    print(f"[{call_sid}] Caller said: {user_text}")

    try:
        assistant_reply = handle_user_input(
            user_text=user_text,
            order_manager=order_manager,
            menu=MENU,
            state=state,
        )
    except Exception as exc:
        print(f"[{call_sid}] ERROR: {exc}")
        assistant_reply = (
            "Sorry, I had trouble understanding that. "
            "Could you say that another way?"
        )

    print(f"[{call_sid}] Assistant: {assistant_reply}")

    if is_checkout_complete_response(assistant_reply):
        response = VoiceResponse()
        response.say(assistant_reply)
        response.hangup()
        sessions.pop(call_sid, None)
        return Response(str(response), mimetype="text/xml")

    return build_gather_response(assistant_reply)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


@app.route("/debug", methods=["POST"])
def debug():
    """
    Optional local debug endpoint.
    Lets you test the agent without calling Twilio.
    """
    data = request.get_json(silent=True) or {}
    call_sid = data.get("call_sid", "debug-call")
    user_text = data.get("text", "")

    session = get_call_session(call_sid)

    try:
        reply = handle_user_input(
            user_text=user_text,
            order_manager=session["order_manager"],
            menu=MENU,
            state=session["state"],
        )

        return {
            "call_sid": call_sid,
            "user_text": user_text,
            "reply": reply,
            "order": session["order_manager"].get_order(),
            "state": session["state"],
        }

    except Exception as exc:
        print(f"[DEBUG ERROR] {type(exc).__name__}: {exc}")

        return {
            "call_sid": call_sid,
            "user_text": user_text,
            "reply": (
                "Sorry, I had trouble processing that. "
                "Could you say that another way?"
            ),
            "error": str(exc),
        }, 500

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "api-demo")
    user_text = data.get("text", "")

    session = get_call_session(session_id)

    try:
        reply = handle_user_input(
            user_text=user_text,
            order_manager=session["order_manager"],
            menu=MENU,
            state=session["state"],
        )

        return {
            "session_id": session_id,
            "user_text": user_text,
            "reply": reply,
            "order": session["order_manager"].get_order(),
            "state": session["state"],
        }

    except Exception as exc:
        return {
            "session_id": session_id,
            "user_text": user_text,
            "reply": "Sorry, I had trouble processing that request.",
            "error": str(exc),
        }, 500
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)