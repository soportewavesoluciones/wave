import ugit
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('cotemax_975','cote120f')

ugit.pull_all(isconnected=True)