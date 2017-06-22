from flask import Flask
from flask import request
from logging.handlers import TimedRotatingFileHandler
from skpy import Skype
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

	if "message" not in request.form:
		return "message not correctly sent", 400

	if "recipients" not in request.form:
		return "receipients not correctly sent", 400

	message = request.form["message"]
	recipients = request.form.getlist("recipients")

	sendMessage(message, recipients)

	return "done", 201

def sendMessage(message, recipients):
	app.logger.info("message=%s", message)

	try:
		sk.conn.readToken()
	except SkypeAuthException:
		connect()

	try:
		for recipient in recipients:
			app.logger.info("sending to=%s", recipient)
			chat = sk.chats[recipient]
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

def connect():
	app.logger.info("Attempting to connect...")
	sk.conn.setUserPwd(app.config["SKYPE_ACCOUNT_USERNAME"], app.config["SKYPE_ACCOUNT_PASSWORD"])
	sk.conn.getSkypeToken()
	app.logger.info("Connection established")

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

	sk = Skype()
	sk.conn.setTokenFile(".tokens-app")
	connect()

	app.run(debug = app.config["DEBUG"], host = app.config["HOST"], port = app.config["PORT"])
