from flask import Flask
from flask import request
from logging.handlers import TimedRotatingFileHandler
import skpy
import logging
import sys

app = Flask(__name__)
app.config.from_pyfile("config.cfg")

@app.route("/", methods = ["GET"])
@app.route("/skype-messenger/status", methods = ["GET"])
def index():
	app.logger.info("checking status")
	return "status ok"

@app.route("/skype-messenger/send", methods = ["POST"])
def send():

	app.logger.info("send called")

	if "message" in request.form:
		message = request.form["message"]
		sendMessage(message)

	return "done"

def sendMessage(message):
	app.logger.info("message=%s", message)

	try:
		app.logger.info("attempting to send")
		sk = skpy.Skype(app.config["SKYPE_ACCOUNT_USERNAME"], app.config["SKYPE_ACCOUNT_PASSWORD"])
		chat = sk.chats[app.config["SKYPE_CHAT_ID"]]
		chat.sendMsg(message, rich = True)
		app.logger.info("message sent")

	except skpy.core.SkypeAuthException, args:
		app.logger.error("Send Failure: SkypeAuthException")
		app.logger.error(args[0])
		app.logger.error(args[1])

	except skpy.core.SkypeApiException, args:
		app.logger.error("Send Failure: SkypeApiException")
		app.logger.error(args[0])
		app.logger.error(args[1])

	except:
		app.logger.error("Generic Send Failure")
		app.logger.error(sys.exc_info()[0])

if __name__ == "__main__":
	handler = TimedRotatingFileHandler(
		app.config["LOG_FILE"],
		when = app.config["LOG_WHEN"],
		interval = app.config["LOG_INTERVAL"],
		backupCount = app.config["LOG_BACKUP_COUNT"]
	)
	handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT"]))
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.INFO)

	app.run(debug = app.config["DEBUG"], host = app.config["HOST"], port = app.config["PORT"])
