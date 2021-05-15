# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import eventManager, Events
import flask
class AutoLogoutPlugin(octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
					   octoprint.plugin.EventHandlerPlugin,
					   octoprint.plugin.SimpleApiPlugin,
                       octoprint.plugin.TemplatePlugin):

	def _sendDataToClient(self, payloadDict):
		self._plugin_manager.send_plugin_message(self._identifier,
												 payloadDict)

	#### print job finished
	# printStatus = "success", "failed", "canceled"
	def _printJobFinished(self, printStatus, payload):
		if (self._settings.get_boolean(["isEnabledByAfterPrint"])):
			if (self._settings.get(["afterPrintStatus"]) == "anyStatus"):
				self._doLogout()
				pass
			else:
				if (printStatus == "success"):
					self._doLogout()
					pass
			pass

	def _doLogout(self):
		payload = {
			"action": "doLogout"
		}
		self._sendDataToClient(payload)
		pass

	def initialize(self):
		self.alreadyCanceled = False

	# start/stop event-hook
	def on_event(self, event, payload):

		if Events.PRINT_STARTED == event:
			self.alreadyCanceled = False
		elif Events.PRINT_DONE == event:
			self._printJobFinished("success", payload)
		elif Events.PRINT_FAILED == event:
			if self.alreadyCanceled == False:
				self._printJobFinished("failed", payload)
		elif Events.PRINT_CANCELLED == event:
			self.alreadyCanceled = True
			self._printJobFinished("canceled", payload)
		pass

	def on_api_get(self, request):
		action = request.values["action"]

		if "isResetSettingsEnabled" == action:
			return flask.jsonify(enabled="true")

		if "resetSettings" == action:
			self._settings.set([], self.get_settings_defaults())
			self._settings.save()
			return flask.jsonify(self.get_settings_defaults())


	##~~ SettingsPlugin mixin
	def get_settings_defaults(self):
		return dict(
			countdownTimeInMinutes = 10,
			isEnabledByInactivity = True,
			isEnabledByAfterPrint = True,
			afterPrintStatus = "anyStatus"
		)

	##~~ TemplatePlugin mixin
	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=True)
		]


	##~~ AssetPlugin mixin
	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/AutoLogout.js", "js/ResetSettingsUtilV3.js"],
			css=["css/AutoLogout.css"],
			less=["less/AutoLogout.less"]
		)

	##~~ Softwareupdate hook
	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			AutoLogout=dict(
				displayName="AutoLogout Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="OllisGit",
				repo="OctoPrint-AutoLogout",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/OllisGit/OctoPrint-AutoLogout/releases/latest/download/master.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "AutoLogout Plugin"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = AutoLogoutPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

