/*
 * View model for OctoPrint-AutoLogout
 *
 * Author: OllisGit
 * License: AGPLv3
 */
$(function() {

    var PLUGIN_ID = "AutoLogout"; // from setup.py plugin_identifier

    var countdownTimeInMinutes = null;
    var countdownReachedFunction = null;
    var countdownTimer = null;
    function AutologoutViewModel(parameters) {
        var self = this;

       // enable support of resetSettings
        new ResetSettingsUtil().assignResetSettingsFeature(PLUGIN_ID, function(data){
                                // assign default settings-values
                                self.pluginSettings.countdownTimeInMinutes(data.countdownTimeInMinutes);
                                self.pluginSettings.isEnabled(data.isEnabled);
        });

        function startLogoutCounter() {

            if (self.pluginSettings.isEnabled() == false){
                if (countdownTimer != null) {
                    clearInterval(countdownTimer);
                }
                return;
            }

            var countdownDisplay = $('#autologout-countdown');
            var counter = countdownTimeInMinutes * 60, minutes, seconds;
            if (countdownTimer != null) {
                clearInterval(countdownTimer);
            }

            countdownTimer = setInterval(function () {
                minutes = parseInt(counter / 60, 10)
                seconds = parseInt(counter % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                countdownDisplay.text( minutes + ":" + seconds );

                if (--counter < 0) {
                    countdownReachedFunction();
                }
                //console.info(".");
            }, 1000);
        }

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];

        self.pluginSettings = null;
        self.onBeforeBinding = function() {
            // assign current pluginSettings
            self.pluginSettings = self.settingsViewModel.settings.plugins[PLUGIN_ID];

            countdownTimeInMinutes = self.pluginSettings["countdownTimeInMinutes"]()

            countdownReachedFunction = function(){
                self.loginStateViewModel.logout();
            }
        }

        countdownStartEventFunction = function (){
            startLogoutCounter();
        }
        self.onUserLoggedIn = countdownStartEventFunction;
        self.onSettingsShown  = countdownStartEventFunction;
        self.onSettingsHidden = countdownStartEventFunction;
        self.onTabChange = countdownStartEventFunction;
        self.onEventUpload = countdownStartEventFunction;
        self.onEventFileRemoved = countdownStartEventFunction;
        self.onEventFileSelected = countdownStartEventFunction;
        self.onEventFileDeselected = countdownStartEventFunction;
        self.onEventPrintStarted = countdownStartEventFunction;
        self.onEventPrintPaused = countdownStartEventFunction;
        self.onEventPrintResumed = countdownStartEventFunction;
        self.onEventPrintCancelled = countdownStartEventFunction;
        self.onEventPrintFailed = countdownStartEventFunction;

    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: AutologoutViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [
            "loginStateViewModel", "settingsViewModel"
         ],
        // Elements to bind to, e.g. #settings_plugin_AutoLogout, #tab_plugin_AutoLogout, ...
        elements: [
            document.getElementById("autologout-navbar"),
            document.getElementById("autologout_plugin_settings")
        ]
    });
});
