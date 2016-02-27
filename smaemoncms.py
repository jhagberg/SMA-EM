"""
 * 
 * by Wenger Florian 2015-08-12
 * wenger@unifox.at
 *
 *
 * 
 *  this software is released under GNU General Public License, version 2.
 *  This program is free software; 
 *  you can redistribute it and/or modify it under the terms of the GNU General Public License 
 *  as published by the Free Software Foundation; version 2 of the License.
 *  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 *  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 *  See the GNU General Public License for more details.
 * 
 *  You should have received a copy of the GNU General Public License along with this program; 
 *  if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.  
 * 
 */
"""
import socket
import struct
import binascii
import signal
import sys
import httplib
import json

# listen to the broadcasts; SMA-Energymeter broadcasts is measurements to 239.12.255.254:9522
MCAST_GRP = '239.12.255.254'
MCAST_PORT = 9522

#EMONCMS
# Domain you want to post to: localhost would be an emoncms installation on your own laptop
# this could be changed to emoncms.org to post to emoncms.org
domain = "192.168.1.219"

# Location of emoncms in your server, the standard setup is to place it in a folder called emoncms
# To post to emoncms.org change this to blank: ""
emoncmspath = "emoncms"

# Write apikey of emoncms account
apikey = "789a1c8bd4b6eb0137961ac1d49f1aa4"

# Node id youd like the emontx to appear as
nodeid = 1

conn = httplib.HTTPConnection(domain)



# function to transform HEX to DEC
def hex2dec(s):
    """return the integer value of a hexadecimal string s"""
    return int(s, 16)

# clean exit
def abortprogram(signal,frame):
    # Housekeeping -> nothing to cleanup 
    print('STRG + C = end program')
    sys.exit(0)

    
    
# prepare listen to socket-Multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


def readem():  
  smainfo=sock.recv(600)
  smainfoasci=binascii.b2a_hex(smainfo)
  
  # split the received message to seperate vars
  smaserial=hex2dec(smainfoasci[40:48])
  pregard=hex2dec(smainfoasci[64:72])/10.0
  pregardcounter=hex2dec(smainfoasci[80:96])/3600000.0
  psurplus=hex2dec(smainfoasci[104:112])/10.0
  qregard=hex2dec(smainfoasci[144:152])/10.0
  qsurplus=hex2dec(smainfoasci[184:192])/10.0
  sregard=hex2dec(smainfoasci[224:232])/10.0
  ssurplus=hex2dec(smainfoasci[264:272])/10.0
  cosphi=hex2dec(smainfoasci[304:312])/1000.0
  

  #L1
  p1regard=hex2dec(smainfoasci[320:328])/10.0
  p1surplus=hex2dec(smainfoasci[360:368])/10.0
  q1regard=hex2dec(smainfoasci[400:408])/10.0
  q1surplus=hex2dec(smainfoasci[440:448])/10.0
  s1regard=hex2dec(smainfoasci[480:488])/10.0
  s1surplus=hex2dec(smainfoasci[520:528])/10.0
  thd1=hex2dec(smainfoasci[560:568])/1000.0
  v1=hex2dec(smainfoasci[576:584])/1000.0
  cosphi1=hex2dec(smainfoasci[592:600])/1000.0
  #L2
  p2regard=hex2dec(smainfoasci[608:616])/10.0
  p2surplus=hex2dec(smainfoasci[648:656])/10.0
  q2regard=hex2dec(smainfoasci[688:696])/10.0
  q2surplus=hex2dec(smainfoasci[728:736])/10.0
  s2regard=hex2dec(smainfoasci[768:776])/10.0
  s2surplus=hex2dec(smainfoasci[808:816])/10.0
  thd2=hex2dec(smainfoasci[848:856])/1000.0
  v2=hex2dec(smainfoasci[864:872])/1000.0
  cosphi2=hex2dec(smainfoasci[880:888])/1000
  #L3
  p3regard=hex2dec(smainfoasci[896:904])/10.0
  p3surplus=hex2dec(smainfoasci[936:944])/10.0
  q3regard=hex2dec(smainfoasci[976:984])/10.0
  q3surplus=hex2dec(smainfoasci[1016:1024])/10.0
  s3regard=hex2dec(smainfoasci[1056:1064])/10.0
  s3surplus=hex2dec(smainfoasci[1096:1104])/10.0
  thd3=hex2dec(smainfoasci[1136:1144])/1000.0
  v3=hex2dec(smainfoasci[1152:1160])/1000.0
  cosphi3=hex2dec(smainfoasci[1168:1176])/1000.0
  #

# Send to emoncms
  data={
       "house_power" : pregard,
       "import_kwh"  : pregardcounter,
       "house_export": psurplus,
       "L1_import"   : p1regard,
       "L1_export"   : p1surplus,
       "L2_import"   : p2regard,
       "L2_export"   : p2surplus,
       "L3_import"   : p3regard,
       "L3_export"   : p3surplus

        }
  jsonstring=json.dumps(data,separators=(',', ':'))
  
  print jsonstring
 # print pregard
 # print str(pregard)
  deg= "/input/post.json?apikey="+apikey+"&node="+str(nodeid)+"&json="+str(jsonstring)
  conn.request("GET", deg)
  response = conn.getresponse()
  conn.close()
#  print response.read()
