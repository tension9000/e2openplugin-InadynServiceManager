# inadyn config editor for inadyn-mt Version 02.24.44, January 2015 - [openpli 7.2]
from os import path, rename
from enigma import getDesktop

from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from Components.PluginComponent import plugins
from Components.ScrollLabel import ScrollLabel
from Components.config import config, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigText, ConfigInteger, ConfigYesNo

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard

from Plugins.Plugin import PluginDescriptor

from Tools.Directories import resolveFilename, SCOPE_PLUGINS

name = "Inadyn Service Manager"
description = _("Inadyn service monitor and configuration file editor")
icon = "plugin.png"
PROGRAMFILE = "/usr/bin/inadyn-mt"
INITSCRIPT = "/etc/init.d/inadyn-mt"
LOGFILE = "/var/log/inadyn.log"
CONFIGFILE = "/etc/inadyn.conf"
CONFIGOPTIONS = ("username", "password", "alias", "addr_pref", "debug", "input_file", "ip_server_name", "dyndns_server_name", "dyndns_server_url", "dyndns_system", "proxy_server", "update_period_sec", "log_file", "background", "verbose", "iterations", "syslog", "cache_dir", "wildcard", "online_check_url", "status_interval", "status_offline_interval")

dyndns_systems = [
("1", "dyndns@dyndns.org"), 
("2", "statdns@dyndns.org"),
("3", "default@freedns.afraid.org"),
("4", "default@zoneedit.com"),
("5", "default@no-ip.com"),
("6", "default@easydns.com"),
("7", "dyndns@3322.org"),
("8", "default@sitelutions.com"),
("9", "default@dnsomatic.com"),
("10", "ipv6tb@he.net"),
("11", "default@tzo.com"),
("12", "default@dynsip.org"),
("13", "default@dhis.org"),
("14", "default@majimoto.net"),
("15", "default@zerigo.com")
]

config.plugins.inadynservicemanager = ConfigSubsection()
config.plugins.inadynservicemanager.showinmenu = ConfigYesNo(default=False)
config.plugins.inadynservicemanager.showinextensions = ConfigYesNo(default=False)
config.plugins.inadynservicemanager.startatboot = ConfigYesNo(default=False)
config.plugins.inadynservicemanager.inputfile = ConfigText(default = "")
config.plugins.inadynservicemanager.logfile = ConfigText(default = LOGFILE)
CFG = config.plugins.inadynservicemanager

def saveConfigFile(filename, cfgString):
	rename(filename, filename + ".old")
	filedest=open(filename, "w")
	filedest.write(cfgString)
	del filedest

class ServiceConsole():

	def __init__(self):
		self.Console = Console()

	def runCmd(self, cmd, callback=None):
		self.Console.ePopen(cmd, self.runCmdFinished, callback)

	def runCmdFinished(self, result, retval, callback):
		if callback is not None:
			(callback) = callback
			if result:
				callback(result.strip())
				print "[ServiceConsole] result: ", result.strip()
			else:
				callback(str(retval))
				print "[ServiceConsole] retval: ", retval

HD = False
try:
	if getDesktop(0).size().width() >= 1280:
		HD = True
except:
	pass

class InadynLog(Screen):
	skin = """
	<screen name="InadynLog" position="center,center" size="540,490" title="Inadyn Log">
		<widget name="InadynLogScrollLabel" font="Regular;20" position="0,40" size="540,450" zPosition="2" halign="center"/>
		<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on"/>
		<widget name="key_red" position="0,0" zPosition="1" size="135,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.setup_title = _("Inadyn Log")

		self["InadynLogScrollLabel"] = ScrollLabel()
		self["key_red"] = Button(_("Delete"))
		self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions"],
		{
			"cancel": self.close,
			"ok": self.close,
			"red": self.deleteLog,
			"up": self["InadynLogScrollLabel"].pageUp,
			"down": self["InadynLogScrollLabel"].pageDown,
		})

		self.sc = ServiceConsole()
		self.logfile = CFG.logfile.value
		self.readLog()

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def cmdCallback(self, data):
		if data:
			self["InadynLogScrollLabel"].setText(data)

	def readLog(self):
		cmd = "cat " + self.logfile
		self.sc.runCmd(cmd, self.cmdCallback)

	def deleteLog(self):
		cmd = "rm -f " + self.logfile
		self.sc.runCmd(cmd, self.cmdCallback)

class InadynServiceMonitor(Screen, ConfigListScreen):
	if HD:
		skin = """
		<screen position="center,center" size="600,500" title="Inadyn Service Monitor" >
			<ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="config" position="10,70" size="590,80" scrollbarMode="showOnDemand" />
			<widget font="Regular;18" halign="left" position="545,480" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget name="state" position="25,150" size="140,40" font="Regular;20" />
			<widget name="status" position="500,150" size="100,40" halign="right" font="Regular;20" />
		</screen>"""
	else:
		skin = """
		<screen position="center,center" size="600,430" title="Inadyn Service Monitor" >
			<ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="config" position="10,60" size="590,120" scrollbarMode="showOnDemand" />
			<widget font="Regular;18" halign="left" position="545,400" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget name="state" position="25,180" size="140,40" font="Regular;20" />
			<widget name="status" position="500,180" size="100,40" halign="right" font="Regular;20" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session

		ConfigListScreen.__init__(self, [], session = session)
		self.setup_title = _("Inadyn Service Monitor")

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Start"))
		self["key_yellow"] = Button(_("Stop"))
		self["key_blue"] = Button(_("View Log"))
		self["state"] = Label(_("Status:"))
		self["status"] = Label()
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "OkCancelActions", "MenuActions"],
		{
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.startService,
			"yellow": self.stopService,
			"blue": self.viewLog,
			"menu": self.keyCancel,
		}, -2)

		self.sc = ServiceConsole()
		self.getBootSetting()
		self.updateServiceStatus()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def updateMenu(self):
		list = [ ]
		list.append(getConfigListEntry(_("Show plugin in setup menu"), CFG.showinmenu))
		list.append(getConfigListEntry(_("Show plugin in extensions menu"), CFG.showinextensions))
		list.append(getConfigListEntry(_("Start inadyn at boot"), CFG.startatboot))
		self["config"].list = list
		self["config"].l.setList(list)

	def updateServiceStatusCallback(self, data):
		self.running = False
		if PROGRAMFILE in data and not "none killed" in data:
			self.running = True
		self["status"].setText("started" if self.running else "stopped")

	def updateServiceStatus(self):
		cmd = "ps -w | grep /usr/bin/inadyn-mt | grep -v grep"
		self.sc.runCmd(cmd, self.updateServiceStatusCallback)

	def getBootSettingCallback(self, data):
		if data:
			self.start_at_boot = "links" in data.split()
			CFG.startatboot.value = self.start_at_boot
		self.updateMenu()

	def getBootSetting(self):
		cmd = "update-rc.d -n inadyn-mt defaults"
		self.sc.runCmd(cmd, self.getBootSettingCallback)

	def startService(self):
		action = "restart" if self.running else "start"
		cmd = INITSCRIPT + " " + action
		self.sc.runCmd(cmd, self.updateServiceStatusCallback)

	def stopService(self):
		cmd = INITSCRIPT + " stop"
		self.sc.runCmd(cmd, self.updateServiceStatusCallback)

	def updateBootSettingCallback(self, data):
		pass

	def updateBootSetting(self):
		cmd = "update-rc.d -f inadyn-mt remove"
		if CFG.startatboot.value:
			cmd = "update-rc.d inadyn-mt defaults"
		self.sc.runCmd(cmd, self.updateBootSettingCallback)

	def saveConfirm(self, save):
		if save:
			CFG.save()
			plugins.clearPluginList()
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
			CFG.startatboot.value is not self.start_at_boot and self.updateBootSetting()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.saveConfirm, MessageBox, _("Apply new settings?"), MessageBox.TYPE_YESNO)
		self.close()

	def viewLog(self):
		self.session.open(InadynLog)

class InadynServiceManager(ConfigListScreen, Screen):
	if HD:
		skin = """
		<screen position="center,center" size="600,500" title="Inadyn Service Manager" >
			<ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
			<ePixmap position="10,470" size="50,30" pixmap="buttons/key_menu.png" alphatest="on" />
			<ePixmap position="60,470" size="50,30" pixmap="buttons/key_0.png" alphatest="on" />
			<ePixmap position="110,470" size="50,30" pixmap="buttons/key_info.png" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="config" position="10,70" size="590,300" scrollbarMode="showOnDemand" />
			<widget font="Regular;18" halign="left" position="545,470" render="Label" size="55,30" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget name="status" position="10,410" size="500,60" font="Regular;18" />
		</screen>"""
	else:
		skin = """
		<screen position="center,center" size="600,430" title="Inadyn Service Manager" >
			<ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
			<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
			<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" />
			<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" />
			<ePixmap position="10,395" size="50,30" pixmap="buttons/key_menu.png" alphatest="on" />
			<ePixmap position="60,395" size="50,30" pixmap="buttons/key_0.png" alphatest="on" />
			<ePixmap position="110,395" size="50,30" pixmap="buttons/key_info.png" alphatest="on" />
			<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
			<widget name="config" position="10,60" size="590,230" scrollbarMode="showOnDemand" />
			<widget font="Regular;18" halign="left" position="545,400" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget name="status" position="10,340" size="500,60" font="Regular;18" />
		</screen>"""

	def __init__(self, session):
		self.session = session
		self.skin = InadynServiceManager.skin
		self.setup_title = _("Inadyn Service Manager")
		Screen.__init__(self, session)
		self["status"] = Label()
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self["key_yellow"] = Button(_("Add alias"))
		self["key_blue"] = Button(_("Reload"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions", "TimerEditActions"],
		{
			"red": self.keyExit,
			"green": self.saveConfig,
			"yellow": self.addAlias,
			"blue": self.loadConfig,
			"cancel": self.keyExit,
			"ok": self.keyOk,
			"menu": self.openMenu,
			"0": self.resetConfig,
			"log": self.showInfo,
		}, -2)

		ConfigListScreen.__init__(self, [])
		self.inadynConfig = {}
		if path.exists(PROGRAMFILE):
			self.loadConfig()
		else:
			self["status"].setText("Please install <inadyn-mt> package first!")

		self.configChanged = False
		self.infoVisible = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def initConfig(self):
		self.readConfig()
		CFG.inputfile.value = self.inadynConfig.get("input_file")
		
	def createMenuEntries(self):
		self.menuEntryUserName         = getConfigListEntry(_("User"), ConfigText(default = self.inadynConfig.get("username")))
		self.menuEntryPassword         = getConfigListEntry(_("Password"), ConfigText(default = self.inadynConfig.get("password")))
		self.menuEntryAliases          = []
		for alias in self.aliases:
			self.menuEntryAliases.append(getConfigListEntry(_("Alias"), ConfigText(default = alias)))
		self.menuEntryInputFile        = getConfigListEntry(_("Input file"), CFG.inputfile)
		self.menuEntryIPServerName     = getConfigListEntry(_("IP server name"), ConfigText(default = self.inadynConfig.get("ip_server_name")))
		self.menuEntryDynServerName    = getConfigListEntry(_("Free dns server name"), ConfigText(default = self.inadynConfig.get("dyndns_server_name")))
		self.menuEntryServerUrl        = getConfigListEntry(_("Free dns server url"), ConfigText(default = self.inadynConfig.get("dyndns_server_url")))
		self.menuEntryDnsSystem        = getConfigListEntry(_("Free dns system"), ConfigSelection(default = self.inadynConfig.get("dyndns_system"), choices=dyndns_systems))
		self.menuEntryUpdatePeriodSec  = getConfigListEntry(_("Update period (seconds)"), ConfigInteger(default = int(self.inadynConfig.get("update_period_sec")), limits=(30,864000)))
		self.menuEntryLogFile          = getConfigListEntry(_("Log file"), ConfigText(default = self.inadynConfig.get("log_file")))
		self.menuEntryLogLevel         = getConfigListEntry(_("Log level (0-5)"), ConfigInteger(default = int(self.inadynConfig.get("verbose")), limits=(0,5)))
		self.menuEntryBackground       = getConfigListEntry(_("Run service in background"), ConfigYesNo(default = True if self.inadynConfig.get("background") == "Yes" else False))
		self.menuEntryCheckUrl         = getConfigListEntry(_("Online check url"), ConfigText(default = self.inadynConfig.get("online_check_url")))
		self.menuEntryStatusInterval   = getConfigListEntry(_("Status interval"), ConfigInteger(default = int(self.inadynConfig.get("status_interval")), limits=(30,864000)))
		self.menuEntryOfflineInterval  = getConfigListEntry(_("Offline status interval"), ConfigInteger(default = int(self.inadynConfig.get("status_offline_interval")), limits=(5,864000)))

	def updateMenuList(self):
		list = []
		list.append(self.menuEntryUserName)
		list.append(self.menuEntryPassword)
		list += self.menuEntryAliases
		list.append(self.menuEntryInputFile)
		list.append(self.menuEntryIPServerName)
		list.append(self.menuEntryDynServerName)
		list.append(self.menuEntryServerUrl)
		list.append(self.menuEntryDnsSystem)
		list.append(self.menuEntryUpdatePeriodSec)
		list.append(self.menuEntryLogFile)
		list.append(self.menuEntryLogLevel)
		list.append(self.menuEntryBackground)
		list.append(self.menuEntryCheckUrl)
		list.append(self.menuEntryStatusInterval)
		list.append(self.menuEntryOfflineInterval)

		self["config"].list = list
		self["config"].l.setList(list)
		self["status"].setText("")
#		print "[InadynServiceManager]updateMenuList ", list

	def loadConfig(self):
		self.initConfig()
		self.createMenuEntries()
		self.updateMenuList()

	def resetConfig(self):
		self.menuEntryUserName[1].value          = self.inadynConfig.get("username")
		self.menuEntryPassword[1].value          = self.inadynConfig.get("password")
		for alias in self.aliases:
			self.menuEntryAliases[self.aliases.index(alias)][1].value = alias
		self.menuEntryInputFile[1].value         = self.inadynConfig.get("input_file")
		self.menuEntryIPServerName[1].value      = self.inadynConfig.get("ip_server_name")
		self.menuEntryDynServerName[1].value     = self.inadynConfig.get("dyndns_server_name")
		self.menuEntryServerUrl[1].value         = self.inadynConfig.get("dyndns_server_url")
		self.menuEntryDnsSystem[1].value         = "1"
		self.menuEntryUpdatePeriodSec[1].value   = 600
		self.menuEntryLogFile[1].value           = LOGFILE
		self.menuEntryLogLevel[1].value          = 0
		self.menuEntryBackground[1].value        = False
		self.menuEntryCheckUrl[1].value          = "http"
		self.menuEntryStatusInterval[1].value    = 600
		self.menuEntryOfflineInterval[1].value   = 15
		self.updateMenuList()

	def saveConfirm(self, result):
		if result:
			CFG.inputfile.value = self.menuEntryInputFile[1].value
			CFG.logfile.value = self.menuEntryLogFile[1].value
			CFG.save()
			self.saveConfig()

	def keyExit(self):
		if self["config"].isChanged() or self.configChanged:
			self.session.openWithCallback(self.saveConfirm, MessageBox, _("Do you want to save config settings?"))
		self.close()

	def VirtualKeyBoardCallback(self, callback=None):
		cur = self["config"].getCurrent()
		if callback is not None:
			if callback == "":
				self.removeAlias(cur)
			else:
				cur[1].setValue(callback)
				self["config"].invalidate(cur)

	def removeAlias(self, cur):
		if len(self.menuEntryAliases) <= 1:
			self.session.open(MessageBox, _("Last alias removing not permitted"), MessageBox.TYPE_INFO, timeout = 5)
			return
		for aliasEntry in self.menuEntryAliases:
			if cur == aliasEntry:
				self.aliases.remove(aliasEntry[1].value)
				self.menuEntryAliases.remove(aliasEntry)
				self.updateMenuList()
				self.configChanged = True

	def addAliasCallback(self, callback=None):
		if callback is not None and callback != "":
			self.menuEntryAliases.append(getConfigListEntry(_("Alias"), ConfigText(default = callback)))
			self.updateMenuList()				
			self.configChanged = True		

	def addAlias(self):
		self.session.openWithCallback(self.addAliasCallback, VirtualKeyBoard, title="Add new alias", text="")

	def showInfo(self):
		if not self.infoVisible:
			self["status"].setText("Button 0 resets config to convenient values\nFor removing alias accept empty keyboard string")
			self.infoVisible = True
		else:
			self["status"].setText("")
			self.infoVisible = False

	def keyOk(self):
		sel = self["config"].getCurrent()
		if sel in (self.menuEntryUpdatePeriodSec, self.menuEntryLogLevel, self.menuEntryStatusInterval, self.menuEntryOfflineInterval):
			print "[InadynServiceManager]keyOk config number"
		elif sel != self.menuEntryBackground:
			print "[InadynServiceManager]keyOk virtual keyboard"
			self.KeyText()

	def saveConfig(self):
		cfgString = ""
		def addLine(string, key, value):
			if value is not None:
				string += "%s %s\n" % (key,value)
			return string
		cfgString = addLine(cfgString, "username", self.menuEntryUserName[1].value)
		cfgString = addLine(cfgString, "password", self.menuEntryPassword[1].value)	
		for alias in self.menuEntryAliases:
			cfgString = addLine(cfgString, "alias", alias[1].value)
		if self.menuEntryInputFile[1].value.strip() != "":
			cfgString = addLine(cfgString, "input_file", self.menuEntryInputFile[1].value)
		cfgString = addLine(cfgString, "ip_server_name", self.menuEntryIPServerName[1].value)
		cfgString = addLine(cfgString, "dyndns_server_name", self.menuEntryDynServerName[1].value)
		cfgString = addLine(cfgString, "dyndns_server_url", self.menuEntryServerUrl[1].value)
		cfgString = addLine(cfgString, "dyndns_system", self.menuEntryDnsSystem[1].getText())
		cfgString = addLine(cfgString, "update_period_sec", str(self.menuEntryUpdatePeriodSec[1].value))
		cfgString = addLine(cfgString, "log_file", self.menuEntryLogFile[1].value)
		cfgString = addLine(cfgString, "verbose", str(self.menuEntryLogLevel[1].value))
		if self.menuEntryBackground[1].value:
			cfgString = addLine(cfgString, "background", " ")
		cfgString = addLine(cfgString, "online_check_url", self.menuEntryCheckUrl[1].value)
		cfgString = addLine(cfgString, "status_interval", str(self.menuEntryStatusInterval[1].value))
		cfgString = addLine(cfgString, "status_offline_interval", str(self.menuEntryOfflineInterval[1].value))

		saveConfigFile(self.inputFile, cfgString)
		print "[InadynServiceManager]saveConfig", cfgString
		self.loadConfig()
		self.configChanged = False

	def readConfig(self):
		self.aliases = []
		if CFG.inputfile.value is not "":
			self.inputFile = CFG.inputfile.value
		else:
			self.inputFile = CONFIGFILE
		if path.exists(self.inputFile):
			for line in file(self.inputFile).readlines():
				line = line.strip()
				line = line.strip("--")
				if line == "" or line[0] == '#':
					continue
				try:
					i = line.find(' ')
					if i == -1 and line in ("background", "syslog", "wildcard"):	# options without value
						k,v = line,"Yes"
					else:
						k,v = line[:i],line[i+1:]
						k,v = k.strip(),v.strip()
					if k not in CONFIGOPTIONS:
						continue
					if k == "alias":						# multi alias
						self.aliases.append(v)
						self.inadynConfig[k] = self.aliases
						continue
					self.inadynConfig[k] = v
				except : pass
#			print "[InadynServiceManager]readConfig aliases ", self.aliases

		def setValue(key, default):
			try:
				value = self.inadynConfig.get(key)
				if value is None or value.strip() == "":
					self.inadynConfig[key] = default
			except: self.inadynConfig[key] = default
# anyway get a default value
		setValue("username", "yourloginuser")
		setValue("password", "yourloginpwd")
		if len(self.aliases) == 0:
			setValue("alias", "yourdynamichost")
		setValue("input_file", "")				#empty input_file key
		setValue("ip_server_name", "youripservername")
		setValue("dyndns_server_name", "yourdyndnsservername")
		setValue("dyndns_server_url", "yourdyndnsserverurl")
		setValue("dyndns_system", "dyndns@dyndns.org")
		setValue("update_period_sec", "600")			#sec	30..864000	Default is about 10 min. Max is 10 days
		setValue("log_file", LOGFILE)
		setValue("verbose", "0")				#levels: 0-5
		setValue("background", "No")
		setValue("online_check_url", "checkurl")
		setValue("status_interval", "600")			#sec	30..864000
		setValue("status_offline_interval", "15")		#sec	5..864000
#		print "[InadynServiceManager]readConfig ", self.inadynConfig

	def openMenu(self):
		self.session.open(InadynServiceMonitor)

def main(session, **kwargs):
	session.open(InadynServiceManager)

def extensionsmenu(session, **kwargs):
	main(session, **kwargs)

def setupmenu(menuid):
	if menuid == "setup":
		return [(name, main, "inadyn_service_manager", 50)]
	return [ ]

def Plugins(**kwargs):
	result = [PluginDescriptor(name=name, description=description, where=[PluginDescriptor.WHERE_PLUGINMENU], icon=icon, fnc=main)]
	if CFG.showinmenu.value:
		result.append(PluginDescriptor(name=name, description=description, where=[PluginDescriptor.WHERE_MENU], icon=icon, fnc=setupmenu))
	if CFG.showinextensions.value:
		result.append(PluginDescriptor(name=name, description=description, where=[PluginDescriptor.WHERE_EXTENSIONSMENU], icon=icon, fnc=extensionsmenu))
	return result


